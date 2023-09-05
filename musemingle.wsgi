import sys
import os

sys.path.insert(0, '/home/ubuntu/musemingle')

from musemingle import create_app


class ApplicationWrapper:
    def __init__(self):
        self.app = create_app()

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)

application = ApplicationWrapper()
