#!/usr/bin/env python3.8
import mimetypes
from req_parser import HTTPError
from functools import lru_cache


@lru_cache(1000)
def read_file(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        return content


def handle_request(server, request):
    if request.method == 'GET':
        return handle_get_request(server, request)
    else:
        raise NotImplementedError()


def handle_get_request(server, request):
    try:
        file_path = f'{server.root_directory}{request.path}'
        file_content = read_file(file_path)
        print(read_file.cache_info())
        headers = {'Server': 'my_server',
                   'Content-Type': mimetypes.guess_type(request.path)[0],
                   'Content-Length': len(file_content)}
        if 'Connection' in request.headers:
            headers['Connection'] = request.headers['Connection']
        else:
            headers['Connection'] = 'close'
        return Response(200, 'OK', headers, file_content)
    except FileNotFoundError:
        raise HTTPError(404, "Not Found")


def handle_error(error):
    try:
        status = error.status
        description = error.description
        body = (error.body or error.description).encode('utf-8')
    except:
        status = 500
        description = b'Internal Server Error'
        body = b'Internal Server Error'
    return Response(status, description, {'Content-Length': len(body), 'Connection': 'keep-alive'}, body)


class Response:
    def __init__(self, status, description, headers=None, body=None):
        self.status = status
        self.description = description
        self.headers = headers
        self.body = body

    def __str__(self):
        return '\r\n'.join([' '.join([str(self.status), str(self.description)]), str(self.headers)])
