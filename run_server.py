#!/usr/bin/env python3.8
import asyncio
from lru import LRU
from logger import log_access, get_access_log_file_descriptor
import json
import os
from req_parser import get_request_object, HTTPError
from req_handler import handle_request, handle_error
from resp_sender import send_response
import time
import multiprocessing as mp

SERVERS = []


class HTTPServer:
    def __init__(self, host="localhost", port=8000, name="server1", root_dir='static/server1',
                 log_dir='logs/server1', proxy_path=None, limit_rate=None, keep_alive_timeout=15):
        self.host = host
        self.port = port
        self.name = name
        self.root_directory = root_dir
        self.log_directory = log_dir
        self.fd_cache = LRU(1000, callback=lambda key, val: os.close(val))
        self.fd_cache[f'{log_dir}/access.log'] = get_access_log_file_descriptor(self)
        self.proxy_path = proxy_path
        self.limit_rate = limit_rate
        self.keep_alive_timeout = keep_alive_timeout

    async def serve_client(self, reader, writer):
        try:
            connection_info = writer.get_extra_info('peername')
            while True:
                try:
                    request = await get_request_object(self, reader)
                    response = await handle_request(self, request)
                    send_response(writer, response)
                    log_access(self, connection_info, request, response)
                    if self.limit_rate:
                        time.sleep(1 / self.limit_rate)
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
        finally:
            await writer.drain()
            writer.close()
            await writer.wait_closed()


class ProcessNoKeyboardInterruptException(mp.Process):
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)

    def run(self):
        try:
            mp.Process.run(self)
        except KeyboardInterrupt:
            for server in SERVERS:
                asyncio.run(server.__aexit__())


def main():
    with open('config.txt') as f:
        config = json.load(f)

    for server in config:
        server_obj = HTTPServer(**config[server])
        p = ProcessNoKeyboardInterruptException(target=build_server, args=(server_obj,))
        p.start()


def build_server(server_obj):
    async def f():
        server = await asyncio.start_server(client_connected_cb=server_obj.serve_client,
                                            host=server_obj.host, port=server_obj.port)
        SERVERS.append(server)
        await server.serve_forever()

    asyncio.run(f())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
