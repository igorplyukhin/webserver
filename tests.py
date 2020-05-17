import unittest
import req_parser
import run_server
from functools import lru_cache
import os
from subprocess import Popen, PIPE, check_output
import subprocess


class TestParser(unittest.TestCase):
    def setUp(self):
        self.server = run_server.HTTPServer()

    def test_simple(self):
        raw_req = [b'GET / HTTP/1.1\r\n', b'Host: localhost\r\n']
        parsed_req = req_parser.parse_request(self.server, raw_req)
        self.assertEqual(parsed_req.method, "GET")
        self.assertEqual(parsed_req.target, "/")
        self.assertEqual(parsed_req.version, 'HTTP/1.1')
        self.assertEqual(len(parsed_req.headers), len(raw_req) - 1)

    def test_missing_host(self):
        with self.assertRaises(req_parser.HTTPError) as err:
            raw_req = [b'GET / HTTP/1.1\r\n']
            parsed_req = req_parser.parse_request(self.server, raw_req)
        self.assertEqual(err.exception.status, 400)

    def test_too_long_req_line(self):
        with self.assertRaises(req_parser.HTTPError) as err:
            raw_req = [b'GET / HTTP/1.1 abab a\r\n', b'Host: localhost\r\n']
            parsed_req = req_parser.parse_request(self.server, raw_req)

        self.assertEqual(err.exception.status, 400)

    def test(self):
        s='./static/server1/script.js'
        import os
        import time

        start = time.time()
        d = {}
        d[s] = os.open(s, os.O_RDONLY)

        for i in range(10000):
            if s in d:
                os.read(d[s], os.path.getsize(s))

        os.close(d[s])

        end = time.time()
        print(end - start)

        start = time.time()


        for i in range(10000):
            with open(s, 'r') as f:
                f.read()

        end = time.time()
        print(end - start)

        start = time.time()
        for i in range(10000):
            read_file(s)

        print(read_file.cache_info())
        end = time.time()
        print(end - start)

    def test_a(self):
        request = 'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n'
        server_response = check_output(f'echo \'{request}\' | nc -Nw1 localhost 8000',
                                       stderr=subprocess.STDOUT, shell=True)
        print(server_response.decode('utf-8'))

        pass


@lru_cache(1000)
def read_file(file_path):
    with open(file_path, 'r') as f:
        a = f.read()
    return a



if __name__ == '__main__':
    unittest.main()
