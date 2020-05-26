from datetime import datetime
import os
from pathlib import Path


def log_access(server, connection_info, req, resp):
    time_zone = datetime.now().astimezone().tzinfo
    data = datetime.now().strftime(f'[%d/%m/%Y:%H:%M:%S {time_zone}]')
    fd = server.fd_cache[f'{server.log_directory}/access.log']
    os.write(fd, f'{connection_info[0]} - - {data} "{str(req)}" {resp.status} {len(resp.body)}\r\n'.encode())


def get_access_log_file_descriptor(server):
    log_path = f'{server.log_directory}/access.log'
    if not os.path.exists(server.log_directory):
        Path(server.log_directory).mkdir(parents=True, exist_ok=True)
        os.mknod(log_path)
    if not os.path.exists(log_path):
        os.mknod(log_path)

    fd = os.open(log_path, os.O_WRONLY)
    os.lseek(fd, 0, 2)
    return fd

