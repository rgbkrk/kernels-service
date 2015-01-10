#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from distutils.version import LooseVersion

import IPython
from IPython.html.utils import url_path_join

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

from IPython.html.services.kernels.kernelmanager import MappingKernelManager
from IPython.html.services.kernels.handlers import (
    KernelHandler, KernelActionHandler,
    ZMQChannelsHandler,
)
from IPython.html.services.kernels.handlers import (
    _kernel_action_regex,
    _kernel_id_regex,
)

def fix_base_path(base_path):
    if not base_path.startswith('/'):
        base_path = '/' + base_path
    if not base_path.endswith('/'):
        base_path = base_path + '/'
    return base_path


class WebApp(web.Application):
    def __init__(self, kernel_manager, settings):
        base_path = settings['base_path']

        handlers = [
            (url_path_join(base_path, r"/api/kernels/%s" % _kernel_id_regex), KernelHandler),
            (url_path_join(base_path, r"/api/kernels/%s/%s" % (_kernel_id_regex, _kernel_action_regex)), KernelActionHandler),
            (url_path_join(base_path, r"/api/kernels/%s/channels" % _kernel_id_regex), ZMQChannelsHandler),
        ]


        super(WebApp, self).__init__(handlers, **settings)

def main():
    tornado.options.define('base_path', default='/',
            help="Base path for the server (e.g. /singlecell)"
    )
    tornado.options.define('port', default=8000,
            help="Port to serve on, defaults to 8000"
    )

    tornado.options.parse_command_line()
    opts = tornado.options.options

    kernel_manager = MappingKernelManager()

    kernel_name = os.environ.get('KERNEL_NAME', None)

    # Examples: python3, ir
    kernel_id = kernel_manager.start_kernel(kernel_name=kernel_name)

    base_path = fix_base_path(opts.base_path)

    # Loosey goosey
    headers = {
            "Access-Control-Allow-Origin": "*",
            "Content-Security-Policy": "",
    }

    allow_origin='*'
    allow_origin_pat=''

    settings = dict(
        cookie_secret=os.environ.get('COOKIE_SECRET', 'secret'),
        cookie_name='ignored',
        kernel_manager=kernel_manager,
        base_path=base_path,
        headers=headers,
        allow_origin=allow_origin,
        allow_origin_pat=allow_origin_pat,
    )

    app = WebApp(kernel_manager, settings)
    server = httpserver.HTTPServer(app)
    server.listen(opts.port)
    app_log.info("Serving at http://127.0.0.1:{}{}api/kernels/{}".format(opts.port, base_path, kernel_id))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        app_log.info("Interrupted...")
    finally:
        kernel_manager.shutdown_all()


if __name__ == '__main__':
    main()

