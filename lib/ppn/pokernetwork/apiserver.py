#!/usr/bin/env python
# coding: utf-8

from contextlib import closing
from functools import wraps
import json

import oauth2

from twisted.python import log
from twisted.web import http, resource


def _JSON_response(request, status_code, json_obj):
    request.setResponseCode(status_code)
    result_string = json.dumps(json_obj)
    request.setHeader('Content-Length', str(len(result_string)))
    request.setHeader('Content-Type', 'application/json; charset=UTF-8')
    return result_string


class OAuthSecretStore(object):
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.__create_table()

    def __create_table(self):
        with closing(self.db_conn.cursor()) as cursor:
            cursor.execute('CREATE TABLE IF NOT EXISTS oauth_secrets '
                '(key TEXT NOT NULL UNIQUE, secret TEXT NOT NULL UNIQUE)')
            self.db_conn.commit()

    def get_secret(self, key):
        """
        Returns the secret corresponding to `key` or None if `key` is not found.
        """
        with closing(self.db_conn.cursor()) as cursor:
            cursor.execute('SELECT secret FROM oauth_secrets WHERE key=?',
                           (key,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None

    def save_secret(self, key, secret):
        with closing(self.db_conn.cursor()) as cursor:
            cursor.execute('INSERT INTO oauth_secrets (key, secret) VALUES '
                           '(?, ?)', (key, secret))
            self.db_conn.commit()


class OAuthResource(resource.Resource):
    """
    Represents a 2-legged OAuth 1.0 protected Resource. When using 2-legged
    OAuth, you do not need to provide an OAuth access token to access
    a resource.

    Each request must be properly signed using the `HMAC-SHA1` signature method.

    See the OAuth 1.0 Protocol spec: http://tools.ietf.org/html/rfc5849
    """
    oauth_server = oauth2.Server(
        signature_methods={'HMAC-SHA1': oauth2.SignatureMethod_HMAC_SHA1()})


    def __init__(self, secret_store):
        resource.Resource.__init__(self)
        self.secret_store = secret_store

    def _validate_request(self, request):
        """
        Validates a 2-legged OAuth 1.0 twisted.web.http.Request object.

        Parameters are accepeted as GET/POST arguments, or in the Authorization
        header.
        """
        url = str(request.URLPath())
        headers = dict(request.requestHeaders.getAllRawHeaders()),

        args = {}
        for key, values in request.args.iteritems():
            if len(values) > 1:
                # error: argument keys cannot be repeated!
                raise KeyError('request argument %s cannot be repeated' % key)
            args[key] = values[0]

        oauth_request = oauth2.Request.from_request(request.method, url,
                                                    headers=headers,
                                                    parameters=args)
        try:
            key = args['oauth_consumer_key']
            secret = self.secret_store.get_secret(key)
        except:
            raise oauth2.Error('Unauthorized')

        consumer = oauth2.Consumer(key=key, secret=secret)
        self.oauth_server.verify_request(oauth_request, consumer, None)

    def _oauth_protect(render_method):
        """Decorates this Resource's render method to protect against
        unauthorized access."""
        @wraps(render_method)
        def wrapper(self, request):
            try:
                self._validate_request(request)
                return render_method(self, request)
            except oauth2.Error:
                status = http.UNAUTHORIZED
                return _JSON_response(request, http.UNAUTHORIZED,
                                      {'error': 'unauthorized',
                                       'status': status})
            except:
                log.err()
                status = http.INTERNAL_SERVER_ERROR
                return _JSON_response(request, status,
                                      {'error': 'internal_server_error',
                                       'status': status})
        return wrapper

    @_oauth_protect
    def render(self, request):
        """Render code used from
        http://twistedmatrix.com/trac/browser/tags/releases/twisted-11.0.0/twisted/web/resource.py
        """
        m = getattr(self, 'render_' + request.method, None)
        if not m:
            from twisted.web.error import UnsupportedMethod
            allowedMethods = (getattr(self, 'allowedMethods', 0) or
                              resource._computeAllowedMethods(self))
            raise UnsupportedMethod(allowedMethods)
        return m(request)


class RefreshTableConfig(OAuthResource):
    isLeaf = True

    def __init__(self, api_service, secret_store):
        OAuthResource.__init__(self, secret_store)
        self.api_service = api_service

    def render_GET(self, request):
        self.api_service.refresh_table_config()
        return ''


class Root(resource.Resource):
    def __init__(self, api_service, secret_store):
        resource.Resource.__init__(self)
        self.putChild('refresh_table_config',
                      RefreshTableConfig(api_service, secret_store))


if __name__ == '__main__':
    from twisted.web.server import Site
    from twisted.internet import reactor
    class SecretStore:
        def get_secret(self, key):
            return 'some_secret'
    secret_store = SecretStore()
    factory = Site(Root(None, secret_store))
    reactor.listenTCP(8880, factory)
    reactor.run()
