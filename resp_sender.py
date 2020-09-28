#!/usr/bin/env python3.8
import asyncio


async def send_response(server, writer, resp):
    status_line = f'HTTP/1.1 {resp.status} {resp.description}\r\n'
    writer.write(status_line.encode('iso-8859-1'))

    if resp.headers:
        for key in resp.headers:
            writer.write(f'{key}: {resp.headers[key]}\r\n'.encode('iso-8859-1'))

    writer.write(b'\r\n')
    if resp.body:
        if server.bandwidth:
            await sleep_write(writer, resp.body, server.bandwidth)
        else:
            writer.write(resp.body)

    if resp.headers is None or resp.headers.get('Connection') != 'keep-alive':
        raise ConnectionResetError


async def sleep_write(writer, data, bandwidth):
    for index in range(0, len(data), bandwidth):
        writer.write(data[index:index + bandwidth])
        await asyncio.sleep(1)
        await writer.drain()
