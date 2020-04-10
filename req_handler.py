#!/usr/bin/env python3.8
import os
import mimetypes
from functools import lru_cache
from req_parser import HTTPError


@lru_cache(maxsize=None)
async def handle_request(server, request):
    if request.method == 'GET':
        try:
            with open(f'{server.root_directory}{request.path}', 'rb') as f:
                file_content = f.read()
                headers = [('Server', 'my_server'),
                           ('Content-Type', mimetypes.guess_type(request.path)[0]),
                           ('Content-Length', len(file_content)),
                           ('Cache-Control', 'public'),
                           ('Connection', 'keep-alive')]
                return Response(200, 'OK', headers, file_content)
        except:
            raise HTTPError(404, 'Not Found')
    else:
        raise NotImplementedError()


async def handle_error(error):
    try:
        status = error.status
        description = error.description
        body = (error.body or error.description).encode('utf-8')
    except:
        status = 500
        description = b'Internal Server Error'
        body = b'Internal Server Error'
    return Response(status, description, [('Content-Length', len(body))], body)


class Response:
    def __init__(self, status, description, headers=None, body=None):
        self.status = status
        self.description = description
        self.headers = headers
        self.body = body
