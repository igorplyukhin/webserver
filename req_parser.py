#!/usr/bin/env python3.8
import asyncio
from email.parser import Parser
from functools import lru_cache
from urllib.parse import urlparse

MAX_REQ_LINE_LEN = 65535
MAX_HEADERS_COUNT = 100
REQ_END_SYMBOLS = [b'', b'\n', b'\r\n']


class HTTPError(Exception):
    def __init__(self, status, description, request=None, body=None):
        super()
        self.status = status
        self.description = description
        self.request = request
        self.body = body


class Request:
    def __init__(self, method, target, version, headers, body=None):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.body = body

    def __str__(self):
        return ' '.join([self.method, self.target, self.version])

    @property
    def url(self):
        return urlparse(self.target)

    @property
    def path(self):
        return self.url.path


async def get_request_object(server, reader):
    raw_request = []
    raw_line = await asyncio.wait_for(reader.readline(), server.keep_alive_timeout)
    if not raw_line:
        raise ConnectionAbortedError
    raw_request.append(raw_line)
    while True:
        raw_line = await reader.readline()
        raw_request.append(raw_line)
        if raw_line in REQ_END_SYMBOLS:
            break
    request = parse_request(server, raw_request)
    if request.method == 'POST':
        body = await reader.read(int(request.headers['Content-Length']))
        request.body = body
    return request


def parse_request(server, raw_request):
    request_line = raw_request[0]
    headers = raw_request[1:]
    method, target, version = parse_request_line(request_line)
    headers = parse_headers(headers)
    host = headers.get('Host')
    if not host:
        raise HTTPError(400, 'Bad request', request_line, 'Host header is missing')
    if host not in (server.host, f'{server.host}:{server.port}'):
        raise HTTPError(404, 'Not Found', request_line)
    return Request(method, target, version, headers)


def parse_request_line(raw_line):
    if len(raw_line) > MAX_REQ_LINE_LEN:
        raise HTTPError(400, 'Bad request', raw_line, 'Line is too long')

    line = str(raw_line, 'iso-8859-1')
    parts = line.split()
    if len(parts) != 3:
        raise HTTPError(400, 'Bad request', raw_line, 'Malformed request line')

    method, target, version = parts
    if version != 'HTTP/1.1':
        raise HTTPError(505, 'HTTP Version Not Supported', raw_line)

    return method, target, version


def parse_headers(raw_headers):
    return Parser().parsestr(bytes.join(b'', raw_headers).decode('iso-8859-1'))
