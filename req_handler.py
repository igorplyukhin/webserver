#!/usr/bin/env python3.8
import asyncio
import mimetypes
from req_parser import HTTPError
import os
from pathlib import Path
from subprocess import check_output, STDOUT
import requests
import re


class Response:
    def __init__(self, status, description, headers=None, body=None):
        self.status = status
        self.description = description
        self.headers = headers
        self.body = body

    def __str__(self):
        return '\r\n'.join([' '.join([str(self.status), str(self.description)]), str(self.headers)])


async def handle_request(server, request):
    if server.regexp_uri_rewrite:
        url = f'{server.host}:{server.port}{request.path}'
        for regexp in server.regexp_uri_rewrite:
            if re.findall(regexp, url):
                request.target = server.regexp_uri_rewrite[regexp]
                break
    if request.method == 'GET':
        return await handle_get_request(server, request)
    if request.method == 'POST':
        return handle_post_request(server, request)
    else:
        raise NotImplementedError()


def handle_post_request(server, request):
    file_path = f'{server.root_directory}{request.path}'
    if os.path.exists(file_path) and os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)
        file_content = read_file(server, file_path, file_size)
        if file_content == request.body:
            return Response(304, 'Not Modified', {'Connection': define_connection_type(request)})
        else:
            rewrite_file(server, file_path, request.body)
            return Response(200, 'OK', {'Connection': define_connection_type(request)})
    else:
        dir_name = os.path.dirname(file_path)
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        os.mknod(file_path)
        if os.path.isfile(file_path):
            rewrite_file(server, file_path, request.body)
            return Response(201, 'Created', {'Connection': define_connection_type(request)})
        return Response(304, 'Not Modified', {'Connection': define_connection_type(request)})


async def handle_get_request(server, request):
    file_path = f'{server.root_directory}{request.path}'
    if server.proxy_path:
        return await handle_proxy_request(server, request)
    if os.path.isfile(file_path):
        return handle_get_file(server, request, file_path)
    if os.path.isdir(file_path):
        return handle_get_dir(server, request, file_path)
    else:
        raise HTTPError(404, 'Not Found', request)


async def handle_proxy_request(server, request):
    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(None, requests.get, server.proxy_path + request.path)
    except:
        raise HTTPError(500, 'Proxy Error', request)
    headers = {'Server': server.name,
               'Content-Type': mimetypes.guess_type(request.path)[0],
               'Content-Length': len(response.content),
               'Connection': define_connection_type(request)}
    return Response(200, 'OK', headers, response.content)


def handle_get_file(server, request, file_path):
    try:
        if server.cgi and '/cgi-bin/' in file_path:
            file_content = check_output(f"python3 {file_path}", stderr=STDOUT, shell=True)
            file_size = len(file_content)
        else:
            file_size = os.path.getsize(file_path)
            file_content = read_file(server, file_path, file_size)
    except (FileNotFoundError, IsADirectoryError):
        raise HTTPError(404, "Not Found", request)

    headers = {'Server': server.name,
               'Content-Type': mimetypes.guess_type(request.path)[0],
               'Content-Length': file_size,
               'Connection': define_connection_type(request)}

    return Response(200, 'OK', headers, file_content)


def handle_get_dir(server, request, file_path):
    content = check_output(f"cd {file_path}/ && tree -H '.' -L 1 --noreport --charset utf-8",
                           stderr=STDOUT, shell=True)
    headers = {'Server': server.name,
               'Content-Type': 'text/html',
               'Content-Length': len(content),
               'Connection': define_connection_type(request)}

    return Response(200, 'OK', headers, content)


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


def rewrite_file(server, file_path, data_to_write):
    fd = get_file_descriptor(server, file_path)
    os.truncate(fd, 0)
    os.write(fd, data_to_write)
    os.lseek(fd, 0, 0)


def define_connection_type(request):
    if 'Connection' in request.headers:
        return request.headers['Connection']
    return 'close'


def read_file(server, file_path, file_size):
    fd = get_file_descriptor(server, file_path)
    file_content = os.read(fd, file_size)
    os.lseek(fd, 0, 0)
    return file_content


def get_file_descriptor(server, file_path):
    if file_path in server.fd_cache:
        fd = server.fd_cache[file_path]
    else:
        if hasattr(os, 'O_BINARY'):  # Windows
            attributes = os.O_RDWR | os.O_BINARY
        else:
            attributes = os.O_RDWR
        server.fd_cache[file_path] = os.open(file_path, attributes)
        fd = server.fd_cache[file_path]
    return fd
