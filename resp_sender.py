#!/usr/bin/env python3.8


def send_response(writer, resp):
    status_line = f'HTTP/1.1 {resp.status} {resp.description}\r\n'
    writer.write(status_line.encode('iso-8859-1'))

    if resp.headers:
        for key in resp.headers:
            writer.write(f'{key}: {resp.headers[key]}\r\n'.encode('iso-8859-1'))

    writer.write(b'\r\n')
    if resp.body:
        writer.write(resp.body)

    if resp.headers is None or resp.headers.get('Connection') != 'keep-alive':
        raise ConnectionResetError
