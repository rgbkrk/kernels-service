#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from distutils.version import LooseVersion

import IPython

try:
    if LooseVersion(IPython.__version__) < LooseVersion('3.0'):
        raise ImportError("single kernel requires IPython ≥ 3.0, found %s" % IPython.__version__)
except TypeError:
    pass

import tornado
import tornado.options
from tornado import httpserver
from tornado import web

from tornado.log import app_log

from IPython.kernel.multikernelmanager import MultiKernelManager
from IPython.html.services.kernels.handlers import (
    KernelHandler, KernelActionHandler,
    ZMQChannelsHandler,
)
from IPython.html.services.kernels.handlers import (
    _kernel_action_regex,
)
_kernel_id_regex = r"(?P<kernel_id>\w+)"


class MicroKernelManager(MultiKernelManager):
    '''MicroKernelManager is a MultiKernelManager that returns the kernel model
    needed by the KernelHandler. This may be removed if
    https://github.com/ipython/ipython/pull/7412 lands.'''
    def kernel_model(self, kernel_id):
        """Return a dictionary of kernel information described in the
        JSON standard model."""
        self._check_kernel_id(kernel_id)
        model = {"id":kernel_id,
                 "name": self._kernels[kernel_id].kernel_name}
        return model

class WebApp(web.Application):
    def __init__(self, kernel_manager):
        handlers = [
            (r"/api/kernels/%s" % _kernel_id_regex, KernelHandler),
            (r"/api/kernels/%s/%s" % (_kernel_id_regex, _kernel_action_regex), KernelActionHandler),
            (r"/api/kernels/%s/channels" % _kernel_id_regex, ZMQChannelsHandler),
        ]

        settings = dict(
            cookie_secret=os.environ.get('COOKIE_SECRET', 'secret'),
            cookie_name='ignored',
            kernel_manager=kernel_manager,
        )

        super(WebApp, self).__init__(handlers, **settings)

def main():
    tornado.options.parse_command_line()

    kernel_manager = MicroKernelManager()

    kernel_id = os.environ.get('KERNEL_ID', '1')
    kernel_name = os.environ.get('KERNEL_NAME', None)
    # Examples: python3, ir

    kernel_manager.start_kernel(kernel_name=kernel_name, kernel_id=kernel_id)

    app = WebApp(kernel_manager)
    server = httpserver.HTTPServer(app)
    server.listen(8000, '127.0.0.1')
    app_log.info("Serving at http://127.0.0.1:8000")
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        app_log.info("Interrupted...")
    finally:
        kernel_manager.shutdown_all()


if __name__ == '__main__':
    main()

