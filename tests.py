import asyncio
import unittest
import req_parser
import run_server
import req_handler
import os
from subprocess import check_output, STDOUT


if __name__ == '__main__':
    unittest.main()


class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = run_server.HTTPServer()

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


class TestHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = run_server.HTTPServer(root_directory='./static/test_dir')
        os.mknod('static/test_dir/abc.txt')

    @classmethod
    def tearDownClass(cls):
        os.remove('static/test_dir/abc.txt')
        os.remove('static/test_dir/posted_doc.txt')

    def test_get_existing_file(self):
        test_string = 'test_string'
        with open('static/test_dir/abc.txt', 'w') as f:
            f.write(test_string)
        req = req_parser.Request('GET', '/abc.txt', 'HTTP/1.1', {})
        response = asyncio.run(req_handler.handle_get_request(self.server, req))
        self.assertEqual(test_string, response.body.decode('utf-8'))

    def test_get_non_existing_file(self):
        with self.assertRaises(req_parser.HTTPError):
            req = req_parser.Request('GET', '/blabla.txt', 'HTTP/1.1', {})
            response = asyncio.run(req_handler.handle_get_request(self.server, req))
            self.assertEqual(404, response.status)

    def test_get_dir(self):
        req = req_parser.Request('GET', '/', 'HTTP/1.1', {})
        response = asyncio.run(req_handler.handle_request(self.server, req))
        self.assertIn('abc.txt', response.body.decode('utf-8'))

    def test_post_request(self):
        req = req_parser.Request('POST','/posted_doc.txt', 'HTTP/1.1', {'Content-Length': '6'}, b'Hello!')
        response = asyncio.run(req_handler.handle_request(self.server, req))
        self.assertEqual('Created', response.description)
        with open('static/test_dir/posted_doc.txt') as f:
            self.assertEqual('Hello!', f.read())

    def test_handle_error(self):
        e = req_parser.HTTPError(404, 'Not Found')
        response = req_handler.handle_error(e)
        self.assertEqual(e.status, response.status)
        self.assertEqual(e.description, response.description)

    def test_internal_error(self):
        response = req_handler.handle_error(123)
        self.assertEqual(500, response.status)
        self.assertEqual(b'Internal Server Error', response.description)

# class TestWholeServer(unittest.TestCase):
#     # execute run_server.py before running
#     def test_simple_req(self):
#         request = 'GET /script.js HTTP/1.1\r\nHost: localhost\r\n\r\n'
#         server_response = check_output(f'echo \'{request}\' | nc -Nw1 localhost 8000', stderr=STDOUT, shell=True)
#         with open('static/server1/script.js') as f:
#             fc = f.read()
#
#         self.assertEqual(server_response.decode('utf-8').split('\r\n\r\n')[1], fc)
