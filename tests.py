import asyncio
import unittest
import req_parser
import run_server


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
        import os
        import time

        start = time.time()
        d = os.open('./static/server1/script.js', os.O_RDONLY)
        print(d)
        for i in range(1000):
            with open(d, 'r') as f:
                f.read()

        end = time.time()
        print(end - start)

        start = time.time()
        for i in range(1000):
            with open('./static/server1/hamming.html', 'r') as f:
                f.read()

        end = time.time()
        print(end - start)


if __name__ == '__main__':
    unittest.main()
