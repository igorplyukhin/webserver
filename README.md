Webserver ![Python 3.8](https://img.shields.io/badge/python-3.8-blue) ![Build](https://img.shields.io/badge/build-passing-brightgreen) ![Top Language](https://img.shields.io/github/languages/top/igorplyukhin/webserver)
=================================================================================================================================================================================

asynchronous multiprocessor webserver serving static requests

**Features**
- Asyncio realisation
- Keep-alive support
- Static requests + opened files descriptors cache
- Logging
- Virtual servers
- Configuration file
- Proxy pass support

**Reqiurements**
- Unix-like system
- `sudo apt install tree`
- python3.8
- `pip install lru-dict`
dict --user

**Usage**
`python3.8 run_server.py`
