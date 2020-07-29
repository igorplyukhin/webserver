#!/usr/bin/env python3.8
import asyncio
from lru import LRU
from logger import log_access, get_access_log_file_descriptor
import json
import os
from req_parser import get_request_object, HTTPError
from req_handler import handle_request, handle_error
from resp_sender import send_response

SERVERS = []


class HTTPServer:
    def __init__(self, host="localhost", port=8000, name="server1", root_dir='static/server1',
                 log_dir='logs/server1', proxy_path=None):
        self.host = host
        self.port = port
        self.name = name
        self.root_directory = root_dir
        self.log_directory = log_dir
        self.fd_cache = LRU(1000, callback=lambda key, val: os.close(val))
        self.fd_cache[f'{log_dir}/access.log'] = get_access_log_file_descriptor(self)
        self.proxy_path = proxy_path

    async def get_asyncio_server(self):
        return await asyncio.start_server(self.serve_client, self.host, self.port)

    async def serve_client(self, reader, writer):
        try:
            connection_info = writer.get_extra_info('peername')
            while True:
                try:
                    request = await get_request_object(self, reader)
                    response = await handle_request(self, request)
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


async def main():
    with open('config.txt') as f:
        config = json.load(f)

    for server in config:
        SERVERS.append(await HTTPServer(**config[server]).get_asyncio_server())
    await asyncio.gather(*map(lambda x: x.serve_forever(), SERVERS))


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        for server in SERVERS:
            asyncio.run(server.__aexit__())
