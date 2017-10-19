from __future__ import print_function
import os
import sys
import glob
import binascii
from notebook.utils import url_unescape

try:
    from six import iteritems
    import flask
    found_flask = True
except ImportError:
    found_flask = False


def get_cookie():
    cookie_name = ""
    try:
        session = int(os.environ['SESSION'])
        pwfile = glob.glob('/var/run/Xvnc/passwd-*')[0]
        with open(pwfile, 'rb') as f:
            token = "%d:%s" % (session, binascii.hexlify(f.read()))

        fn = os.path.join(os.environ['SESSIONDIR'], 'resources')
        with open(fn, 'r') as f:
            res = f.read()
        for line in res.split('\n'):
            if line.startswith('hub_url'):
                url = line.split()[1]
                host = url[url.find('//') + 2:]
                cookie_name = 'weber-auth-' + host.replace('.', '-')
                break
    except:
        # not a hub
        return "", ""
    return cookie_name, token


def _get_session():
    try:
        session = os.environ['SESSION']
        sessiondir = os.environ['SESSIONDIR']
    except:
        return "", ""
    return session, sessiondir


def get_proxy_addr():
    session, sessiondir = _get_session()
    if session == "":
        return "/", ""
    fn = os.path.join(sessiondir, 'resources')
    with open(fn, 'r') as f:
        res = f.read()
    for line in res.split('\n'):
        if line.startswith('hub_url'):
            url = line.split()[1]
        elif line.startswith('filexfer_port'):
            fxp = str(int(line.split()[1]) % 1000)
        elif line.startswith('filexfer_cookie'):
            fxc = line.split()[1]
    url_path = "/weber/%s/%s/%s/" % (session, fxc, fxp)
    proxy_url = "https://proxy." + url.split('//')[1] + url_path
    print("Connect to %s" % proxy_url, file=sys.stderr)
    return url_path, proxy_url


if found_flask:
    class HubAuth(object):
        def __init__(self, app, cookie):
            self.app = app
            self.cookie_name = cookie[0]
            self.token = cookie[1]
            self._index_view_name = app.config['routes_pathname_prefix']
            self._overwrite_index()
            self._protect_views()
            self._index_view_name = app.config['routes_pathname_prefix']

        def _overwrite_index(self):
            original_index = self.app.server.view_functions[self._index_view_name]

            def wrap_index(*args, **kwargs):
                if self.is_authorized():
                    return original_index(*args, **kwargs)
                else:
                    return self.login_request()
            self.app.server.view_functions[self._index_view_name] = wrap_index

        def _protect_views(self):
            # TODO - allow users to white list in case they add their own views
            for view_name, view_method in iteritems(self.app.server.view_functions):
                if view_name != self._index_view_name:
                    self.app.server.view_functions[view_name] = \
                        self.auth_wrapper(view_method)

        def is_authorized(self):
            if self.cookie_name not in flask.request.cookies:
                return False

            cookie = flask.request.cookies[self.cookie_name]
            cookie = url_unescape(cookie)
            for item in cookie.split(','):
                if item == self.token:
                    return True
            return False

        def login_request(self):
            return flask.Response(
                'Access Forbidden',
                status=403)

        def auth_wrapper(self, f):
            def wrap(*args, **kwargs):
                if not self.is_authorized():
                    return flask.Response(status=403)
                response = f(*args, **kwargs)
                return response
            return wrap

    def check_access(app):
        cookie = get_cookie()
        if cookie[0] == "":
            return
        HubAuth(app, get_cookie())
