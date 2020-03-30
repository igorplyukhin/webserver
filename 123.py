#!/usr/bin/env python3.8
import asyncio
import sys


class HTTPServer:

    def __init__(self, host, port):
        self.counter = 0
        self.host = host
        self.port = port

    async def run_server(self, host, port=8000):
        server = await asyncio.start_server(self.serve_client, host, port)
        await server.serve_forever()

    async def serve_client(self, reader, writer):
        cid = self.counter
        self.counter += 1
        print(f'Client #{cid} connected')

        while True:
            request = await self.read_request(reader)
            if request is None:
                print(f'Client #{cid} unexpectedly disconnected')
                writer.close()
                break
            else:
                response = await self.handle_request(request)
                await self.write_response(writer, response, cid)

    @staticmethod
    async def read_request(reader, delimiter=b'!'):
        request = bytearray()
        while True:
            chunk = await reader.read(4)
            if not chunk:
                # Клиент преждевременно отключился.
                break

            request += chunk
            if delimiter in request:
                return request

        return None

    @staticmethod
    async def handle_request(request):
        await asyncio.sleep(5)
        return request[::-1]

    @staticmethod
    async def write_response(writer, response, cid):
        writer.write(response)
        await writer.drain()
        # writer.close()
        print(f'Client #{cid} has been served')


async def loop():
    s1 = HTTPServer('192.168.1.83', 8000)
    s2 = HTTPServer('127.0.0.2', 8000)
    t1 = asyncio.create_task(s1.run_server(s1.host, s2.port))
    t2 = asyncio.create_task(s2.run_server(s2.host, s2.port))
    await t1
    await t2


if __name__ == '__main__':
    asyncio.run(loop())
