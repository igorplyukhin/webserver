#!/usr/bin/env python3.8


async def send_response(writer, resp):
    status_line = f'HTTP/1.1 {resp.status} {resp.description}\r\n'
    writer.write(status_line.encode('iso-8859-1'))

    if resp.headers:
        for (key, value) in resp.headers:
            writer.write(f'{key}: {value}\r\n'.encode('iso-8859-1'))

    writer.write(b'\r\n')
    if resp.body:
        writer.write(resp.body)

    await writer.drain()
    writer.close()
