#!/usr/bin/env python3.8
from email.parser import Parser
from functools import lru_cache
from urllib.parse import parse_qs, urlparse

MAX_REQ_LINE_LEN = 65535
MAX_HEADERS_COUNT = 100
REQ_END_SYMBOLS = [b'', b'\n', b'\r\n']


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
        raise Exception('Bad request')
    if host not in (server.server_name, f'{server.server_name}:{server.port}'):
        raise Exception('Not found')
    return Request(method, target, version, headers)


async def parse_request_line(reader):
    raw_line = await reader.readline()
    if len(raw_line) > MAX_REQ_LINE_LEN:
        raise Exception('Line is too long')

    line = str(raw_line, 'iso-8859-1')
    parts = line.split()
    if len(parts) != 3:
        raise Exception("Bad request")

    method, target, version = parts
    if version != 'HTTP/1.1':
        raise Exception()

    return method, target, version


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

