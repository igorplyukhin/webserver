#!/usr/bin/env python3.8
import mimetypes
from req_parser import HTTPError
import os


def handle_request(server, request):
    if request.method == 'GET':
        return handle_get_request(server, request)
    else:
        raise NotImplementedError()


def handle_get_request(server, request):
    file_path = f'{server.root_directory}{request.path}'
    print(file_path)
    if os.path.isfile(file_path):
        return handle_get_file(server, request, file_path)
    if os.path.isdir(file_path):
        return handle_get_dir(request, file_path)
    else:
        raise HTTPError(404, 'Not Found')


def handle_get_file(server, request, file_path):
    try:
        if file_path in server.fd_cache:
            fd = server.fd_cache[file_path]
        else:
            if hasattr(os, 'O_BINARY'): # Windows
                attributes = os.O_RDONLY | os.O_BINARY
            else:
                attributes = os.O_RDONLY
            server.fd_cache[file_path] = os.open(file_path, attributes)
            fd = server.fd_cache[file_path]

        file_size = os.path.getsize(file_path)
        file_content = os.read(fd, file_size)
        os.lseek(fd, 0, 0)
    except (FileNotFoundError, IsADirectoryError):
        raise HTTPError(404, "Not Found")

    headers = {'Server': 'my_server',
               'Content-Type': mimetypes.guess_type(request.path)[0],
               'Content-Length': file_size}
    if 'Connection' in request.headers:
        headers['Connection'] = request.headers['Connection']
    else:
        headers['Connection'] = 'close'
    return Response(200, 'OK', headers, file_content)


def handle_get_dir(request, file_path):
    content = os.popen(f"cd {file_path}/ && tree -H '.' -L 1 --noreport --charset utf-8").read()
    print(content)
    headers = {'Server': 'my_server',
               'Content-Type': 'text/html',
               'Content-Length': len(content)}
    if 'Connection' in request.headers:
        headers['Connection'] = request.headers['Connection']
    else:
        headers['Connection'] = 'close'
    return Response(200, 'OK', headers, content.encode('utf-8'))


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
