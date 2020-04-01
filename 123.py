#!/usr/bin/env python3.8
import asyncio
from email.parser import Parser
import json
import sys

MAX_REQ_LINE_LEN = 65535
MAX_HEADERS_COUNT = 100
REQ_END_SYMBOLS = [b'', b'\n', b'\r\n']


class HTTPServer:
    def __init__(self, host="127.0.0.1", port=8000, server_name="server"):
        self.counter = 0
        self.host = host
        self.port = port
        self.server_name = server_name

    async def run_server(self, host, port=8000):
        server = await asyncio.start_server(self.serve_client, host, port)
        await server.serve_forever()

    async def serve_client(self, reader, writer):
        cid = self.counter
        self.counter += 1
        print(f'Client #{cid} connected')

        while True:
            request = await self.parse_request(reader)
            if request is None:
                print(f'Client #{cid} disconnected')
                writer.close()
                break
            #response = await self.handle_request(request)
            #await self.write_response(writer, response, cid)

    async def parse_request(self, reader):
        method, target, version = await self.parse_request_line(reader)
        headers = await self.parse_headers(reader)
        print(headers)
        return Request(method, target, version)

    @staticmethod
    async def parse_request_line(reader):
        raw_line = await reader.readline()
        if len(raw_line) > MAX_REQ_LINE_LEN:
            raise Exception('Line is too long')

        line = str(raw_line, 'iso-8859-1')
        print(line)
        parts = line.split()
        if len(parts) != 3:
            raise Exception("Bad request")

        method, target, version = parts
        if version != 'HTTP/1.1':
            raise Exception()

        return method, target, version

    @staticmethod
    async def parse_headers(reader):
        headers = []
        while True:
            line = await reader.readline()
            if len(line) > MAX_REQ_LINE_LEN:
                raise Exception("Line is too long")
            if line in REQ_END_SYMBOLS:
                break

            headers.append(line)
            if len(headers) > MAX_HEADERS_COUNT:
                raise Exception("Too many headers")

        return Parser().parsestr(bytes.join(b'', headers).decode('iso-8859-1'))

    @staticmethod
    async def handle_request(request):
        return request

    @staticmethod
    async def write_response(writer, response, cid):
        writer.write(response)
        await writer.drain()
        print(f'Client #{cid} has been served')


class Request:
    def __init__(self, method, target, version):
        self.method = method
        self.target = target
        self.version = version


async def loop():
    s1 = HTTPServer('192.168.1.83', 8000)
    s2 = HTTPServer('127.0.0.1', 8000)
    t1 = asyncio.create_task(s1.run_server(s1.host, s2.port))
    t2 = asyncio.create_task(s2.run_server(s2.host, s2.port))
    await t1
    await t2


if __name__ == '__main__':
    try:
        asyncio.run(loop())
    except KeyboardInterrupt:
        pass
