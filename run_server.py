#!/usr/bin/env python3.8
import asyncio
import req_parser
import req_handler
import resp_sender


class HTTPServer:
    def __init__(self, host="localhost", port=8000, server_name="localhost", root_directory='./static/server1'):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.root_directory = root_directory

    async def run_server(self):
        server = await asyncio.start_server(self.serve_client, self.host, self.port)
        await server.serve_forever()

    async def serve_client(self, reader, writer):
        try:
            client_info = writer.get_extra_info('peername')
            print(f'Client {client_info} connected')
            while True:
                try:
                    raw_request = await req_parser.read_request(reader)
                    request = req_parser.parse_request(self, raw_request)
                    response = req_handler.handle_request(self, request)
                    print(request)
                    print(response)
                    resp_sender.send_response(writer, response)
                except asyncio.exceptions.TimeoutError:
                    print(f'connection {client_info} closed by timeout')
                    break
                except ConnectionAbortedError:
                    print(f'connection {client_info} reset by peer')
                    break
                except ConnectionResetError:
                    print(f'Keep-alive connection{client_info} closed')
                    break
                except req_parser.HTTPError as error:
                    response = req_handler.handle_error(error)
                    resp_sender.send_response(writer, response)
        finally:
            await writer.drain()
            writer.close()
            await writer.wait_closed()


if __name__ == '__main__':
    s = HTTPServer('localhost', 8000, 'localhost')
    try:
        asyncio.run(s.run_server())
    except KeyboardInterrupt:
        pass
