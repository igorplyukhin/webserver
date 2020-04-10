#!/usr/bin/env python3.8
import asyncio
from email.parser import Parser
from functools import lru_cache
from urllib.parse import parse_qs, urlparse

MAX_REQ_LINE_LEN = 65535
MAX_HEADERS_COUNT = 100
REQ_END_SYMBOLS = [b'', b'\n', b'\r\n']


class HTTPError(Exception):
    def __init__(self, status, description, body=None):
        super()
        self.status = status
        self.description = description
        self.body = body


class Request:
    def __init__(self, method, target, version, headers):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers

    @property
    @lru_cache()
    def url(self):
        return urlparse(self.target)

    @property
    def path(self):
        return self.url.path


async def parse_request(server, reader):
    method, target, version = await parse_request_line(reader)
    headers = await parse_headers(reader)
    print(method, target, version)
    print(headers)
    host = headers.get('Host')
    if not host:
        raise HTTPError(400, 'Bad request', 'Host header is missing')
    if host not in (server.server_name, f'{server.server_name}:{server.port}'):
        raise HTTPError(404, 'Not Found')
    return Request(method, target, version, headers)


async def parse_request_line(reader):
    raw_line = await asyncio.wait_for(reader.readline(), 15)
    if not raw_line:
        raise ConnectionAbortedError

    if len(raw_line) > MAX_REQ_LINE_LEN:
        raise HTTPError(400, 'Bad request', 'Line is too long')

    line = str(raw_line, 'iso-8859-1')
    parts = line.split()
    if len(parts) != 3:
        raise HTTPError(400, 'Bad request', 'Malformed request line')

    method, target, version = parts
    if version != 'HTTP/1.1':
        raise HTTPError(505, 'HTTP Version Not Supported')

    return method, target, version


async def parse_headers(reader):
    headers = []
    while True:
        line = await reader.readline()
        if len(line) > MAX_REQ_LINE_LEN:
            raise HTTPError(494, 'Request header too large')
        if line in REQ_END_SYMBOLS:
            break

        headers.append(line)
        if len(headers) > MAX_HEADERS_COUNT:
            raise HTTPError(494, 'Too many headers')

    return Parser().parsestr(bytes.join(b'', headers).decode('iso-8859-1'))
