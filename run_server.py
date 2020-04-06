#!/usr/bin/env python3.8

import asyncio
import req_parser
import req_handler
import resp_sender
import json
import sys


class HTTPServer:
    def __init__(self, host="127.0.0.1", port=8000, server_name="127.0.0.1", root_directory='./static/server1'):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.root_directory = root_directory

    async def run_server(self):
        server = await asyncio.start_server(self.serve_client, self.host, self.port)
        await server.serve_forever()

    async def serve_client(self, reader, writer):
        client_info = writer.get_extra_info('peername')
        print(f'Client {client_info} connected')

        while True:
            request = await req_parser.parse_request(self, reader)
            print(request.path)
            # if request is None:
            #     print(f'Client #{client_info} disconnected')
            #     writer.close()
            #     break
            response = await req_handler.handle_request(self, request)
            await resp_sender.send_response(writer, response)


# async def create_virtual_servers(count):
#     s1 = HTTPServer('192.168.1.83', 8000, '192.168.1.83')
#     s2 = HTTPServer('127.0.0.1', 8000, 'localhost')
#     t1 = asyncio.create_task(s1.run_server())
#     t2 = asyncio.create_task(s2.run_server())
#     await t1
#     await t2


if __name__ == '__main__':
    s = HTTPServer('127.0.0.1', 8000, 'localhost')
    try:
        asyncio.run(s.run_server())
    except KeyboardInterrupt:
        pass
