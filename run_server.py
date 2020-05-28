#!/usr/bin/env python3.8
import asyncio
from lru import LRU
from logger import log_access, get_access_log_file_descriptor
import os
from req_parser import get_request_object, HTTPError
from req_handler import handle_request, handle_error
from resp_sender import send_response


class HTTPServer:
    def __init__(self, host="localhost", port=8000, server_name="server1", root_directory='static/server1',
                 log_directory='logs/server1'):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.root_directory = root_directory
        self.log_directory = log_directory
        self.fd_cache = LRU(1000, callback=lambda key, val: os.close(val))
        self.fd_cache[f'{log_directory}/access.log'] = get_access_log_file_descriptor(self)

    async def run_server(self):
        server = await asyncio.start_server(self.serve_client, self.host, self.port)
        await server.serve_forever()

    async def serve_client(self, reader, writer):
        try:
            connection_info = writer.get_extra_info('peername')
            while True:
                try:
                    request = await get_request_object(self, reader)
                    response = handle_request(self, request)
                    send_response(writer, response)
                    log_access(self, connection_info, request, response)
                except asyncio.exceptions.TimeoutError:
                    print(f'connection {connection_info} closed by timeout')
                    break
                except ConnectionAbortedError:
                    print(f'connection {connection_info} reset by peer')
                    break
                except ConnectionResetError:
                    print(f'Keep-alive connection{connection_info} closed')
                    break
                except HTTPError as error:
                    response = handle_error(error)
                    send_response(writer, response)
                    log_access(self, connection_info, error.request, response)
        # except:
            # log smth ConnectionResetError if close connection while handling send_error()
            # BrokenPipeError ^C
        finally:
            await writer.drain()
            writer.close()
            await writer.wait_closed()


if __name__ == '__main__':
    s = HTTPServer()
    try:
        asyncio.run(s.run_server())
    except KeyboardInterrupt:
        pass
