#!/usr/bin/env python3.8
import asyncio
from lru import LRU
from logger import log_access, get_access_log_file_descriptor
import json
import os
from req_parser import get_request_object, HTTPError
from req_handler import handle_request, handle_error
from resp_sender import send_response
import multiprocessing as mp

SERVERS = []
PROCESSES = []


class HTTPServer:
    def __init__(self, host="127.0.0.1", port=8000, name="server1", root_dir='static/server1',
                 log_dir='logs/server1', proxy_pass=None, bandwidth=None, keep_alive_timeout=1,
                 regexp_uri_rewrite=None, cgi=False):
        if regexp_uri_rewrite is None:
            regexp_uri_rewrite = dict()
        self.host = host
        self.port = port
        self.name = name
        self.root_directory = root_dir
        self.log_directory = log_dir
        self.fd_cache = LRU(1000, callback=lambda key, val: os.close(val))
        self.fd_cache[f'{log_dir}/access.log'] = get_access_log_file_descriptor(self)
        self.proxy_path = proxy_pass
        self.bandwidth = bandwidth
        self.keep_alive_timeout = keep_alive_timeout
        self.regexp_uri_rewrite = regexp_uri_rewrite
        self.cgi = cgi

    async def serve_client(self, reader, writer):
        try:
            connection_info = writer.get_extra_info('peername')
            while True:
                try:
                    request = await get_request_object(self, reader)
                    response = await handle_request(self, request)
                    await send_response(self, writer, response)
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
                    await send_response(self, writer, response)
                    log_access(self, connection_info, error.request, response)
        finally:
            await writer.drain()
            writer.close()
            await writer.wait_closed()


def main():
    with open('config.txt') as f:
        config = json.load(f)

    for server in config:
        server_obj = HTTPServer(**config[server])
        p = mp.Process(target=build_server, args=(server_obj,))
        PROCESSES.append(p)
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
