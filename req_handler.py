#!/usr/bin/env python3.8
import os
import mimetypes


async def handle_request(server, request):
    if request.method == 'GET':
        try:
            with open(f'{server.root_directory}{request.path}') as f:
                file_content = f.read()
                headers = [('Server', 'my_server'),
                           ('Content-Type', mimetypes.guess_type(request.path)[0]),
                           ('Content-Length', len(file_content))]
                return Response(200, 'OK', headers, file_content.encode('utf-8'))
        except:
            phrase = 'Hello'
            headers = [('Content-Type', 'text/html'),
                       ('Content-Length', len(phrase))]
            return Response(200, 'OK', headers, phrase.encode('utf-8'))


class Response:
    def __init__(self, status, description, headers=None, body=None):
        self.status = status
        self.description = description
        self.headers = headers
        self.body = body
