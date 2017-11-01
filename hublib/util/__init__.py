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
            pwd = binascii.hexlify(f.read()).decode('utf-8')
            token = "%d:%s" % (session, str(pwd))

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
    print("Connect to %s?auth=%s" % (proxy_url, get_cookie()[1]), file=sys.stderr)
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

        def set_cookie(self, response, name, value):
            response.set_cookie(
                name,
                value=value,
                max_age=24 * 60 * 60 * 7,
                secure=True,
                path=self.app.config['routes_pathname_prefix']
            )

        def _overwrite_index(self):
            original_index = self.app.server.view_functions[self._index_view_name]
            
            def wrap_index(*args, **kwargs):
                res = original_index(*args, **kwargs)                
                response = flask.Response(res)
                
                if 'auth' in flask.request.args:
                    auth = flask.request.args['auth']
                    # print("compare: '%s' ****** '%s'" % (auth, self.token))
                    if auth == self.token:
                        # print("SETTING COOKIE")
                        self.set_cookie(response, self.cookie_name, auth)
                        return response
            
                # print("cookies=", flask.request.cookies)
                if self.cookie_name not in flask.request.cookies:
                    # print("%s not in cookies" % self.cookie_name)
                    return flask.Response('Access Forbidden', status=403)

                cookie = flask.request.cookies[self.cookie_name]
                cookie = url_unescape(cookie)
                for item in cookie.split(','):
                    # print("compare: '%s' ****** '%s'" % (item, self.token))
                    if item == self.token:
                        return response
                return flask.Response('Access Forbidden', status=403)
                
            self.app.server.view_functions[self._index_view_name] = wrap_index

        def _protect_views(self):
            for view_name, view_method in iteritems(self.app.server.view_functions):
                self.app.server.view_functions[view_name] = self.auth_wrapper(view_method)


        def auth_wrapper(self, f):
            def wrap(*args, **kwargs):
                # print("auth_wrapper:")
                # print("    cookies=", flask.request.cookies)
                if 'auth' in flask.request.args:
                    auth = flask.request.args['auth']
                    if auth == self.token:
                        # print("SETTING COOKIE 2")
                        response = flask.Response(f(*args, **kwargs))
                        self.set_cookie(response, self.cookie_name, auth)
                        return f(*args, **kwargs)
                if self.cookie_name not in flask.request.cookies:
                    # print("%s not in cookies" % self.cookie_name)
                    return flask.Response('Access Forbidden', status=403)

                cookie = flask.request.cookies[self.cookie_name]
                cookie = url_unescape(cookie)
                for item in cookie.split(','):
                    # print("    compare: '%s' ****** '%s'" % (item, self.token))
                    if item == self.token:
                        return f(*args, **kwargs)           
                return flask.Response('Access Forbidden', status=403)
            return wrap

    def check_access(app):
        cookie = get_cookie()
        if cookie[0] == "":
            return
        HubAuth(app, get_cookie())
