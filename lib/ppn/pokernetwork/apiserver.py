#!/usr/bin/env python
# coding: utf-8

from contextlib import closing
from functools import wraps
import json
import warnings

import oauth2

from twisted.python import log
from twisted.web import http, resource


class APIUserStore(object):
    SCHEMA = """CREATE TABLE IF NOT EXISTS `api_users` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `email` varchar(255) NOT NULL,
      `api_key` varchar(255) NOT NULL,
      `secret` varchar(255) NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `key_secret` (`api_key`,`secret`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    def __init__(self, db):
        self.db = db
        self.__create_table_if_not_exists()

    def __create_table_if_not_exists(self):
        with closing(self.db.cursor()) as cursor:
            # MySQLdb raises a warning when api_users already exists:
            # "Warning: Table 'api_users' already exists
            # cursor.execute(self.SCHEMA)"
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', "Table '\w+' already exists")
                cursor.execute(self.SCHEMA)
                self.db.commit()

    def get_secret(self, api_key):
        """
        Returns the secret corresponding to `key` or None if `key` is not found.
        """
        with closing(self.db.cursor()) as cursor:
            cursor.execute('SELECT secret FROM api_users WHERE api_key=%s',
                           (api_key,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None

    def get_users(self):
        """
        Returns a list of dictionaries containing the following keys: id,
        email, key, secret.
        """
        with closing(self.db.cursor()) as cursor:
            cursor.execute('SELECT id, email, api_key, secret FROM api_users')
            return cursor.fetchall()

    def add_user(self, email, api_key, secret):
        with closing(self.db.cursor()) as cursor:
            cursor.execute('INSERT INTO api_users (email, api_key, secret) '
                           'VALUES (%s, %s, %s)', (email, api_key, secret))
            self.db.commit()

    def remove_users_by_email(self, email):
        with closing(self.db.cursor()) as cursor:
            cursor.execute('DELETE FROM api_users WHERE email=%s', (email,))
            self.db.commit()

    def remove_user_by_key(self, api_key):
        with closing(self.db.cursor()) as cursor:
            cursor.execute('DELETE FROM api_users WHERE api_key=%s',
                           (api_key,))
            self.db.commit()


def _JSON_response(request, status_code=http.OK, response_dict={}):
    request.setResponseCode(status_code)
    result_string = json.dumps(response_dict, separators=(',', ':'))
    request.setHeader('Content-Type', 'application/json; charset=UTF-8')
    request.setHeader('Cache-Control', 'no-store')
    request.setHeader('Pragma', 'no-cache')
    return result_string


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
        headers = dict(request.requestHeaders.getAllRawHeaders())

        args = {}
        for key, values in request.args.iteritems():
            if len(values) > 1:
                # error: argument keys cannot be repeated!
                raise KeyError('request argument %s cannot be repeated' % key)
            args[key] = values[0]

        oauth_request = oauth2.Request.from_request(request.method, url,
                                                    headers=headers,
                                                    parameters=args)

        key = args['oauth_consumer_key']
        secret = self.secret_store.get_secret(key)
        if secret is None:
            raise oauth2.Error('Invalid Consumer Key')

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
            except (oauth2.MissingSignature, ValueError, KeyError):
                status = http.BAD_REQUEST
                return _JSON_response(request, status, {'error': 'bad_request'})
            except oauth2.Error:
                status = http.UNAUTHORIZED
                return _JSON_response(request, status, {'error':
                                                        'unauthorized'})
            except:
                log.err()
                status = http.INTERNAL_SERVER_ERROR
                return _JSON_response(request, status,
                                      {'error': 'internal_server_error'})
        return wrapper

    @_oauth_protect
    def render(self, request):
        """Render code used from
        http://twistedmatrix.com/trac/browser/tags/releases/twisted-11.0.0/twisted/web/resource.py
        """
        m = getattr(self, 'render_' + request.method, None)
        if not m:
            allowedMethods = (getattr(self, 'allowedMethods', 0) or
                              resource._computeAllowedMethods(self))

            status = http.NOT_ALLOWED
            description = 'Unsupported method. Allowed methods: %s' \
                              % str(allowedMethods)
            json = {'error': 'method_not_allowed',
                    'error_description': description}
            request.setHeader('Allow', ', '.join(allowedMethods))
            return _JSON_response(request, status, json)
        return m(request)


def get_json_request_body(request):
    """
    Deserializes the request's body into a Python object. See the documentation
    for json.loads: http://docs.python.org/library/json.html
    """
    return json.loads(request.content.read())


class RefreshTableConfig(OAuthResource):
    isLeaf = True

    def __init__(self, api_service, secret_store):
        OAuthResource.__init__(self, secret_store)
        self.api_service = api_service

    def render_GET(self, request):
        self.api_service.refresh_table_config()
        return _JSON_response(request)


class BroadcastMessageToPlayerSerial(OAuthResource):
    def __init__(self, player_serial, api_service, secret_store):
        OAuthResource.__init__(self, secret_store)
        self.api_service = api_service
        self.player_serial = player_serial

    def render_POST(self, request):
        json_request_body = get_json_request_body(request)
        message = json_request_body['message']
        success = self.api_service.broadcast_to_player(message,
                                                       self.player_serial)
        if success:
            return _JSON_response(request)
        description = 'Could not broadcast message to player with serial %s'\
                            % self.player_serial
        response = {'error': 'bad_request', 'error_description': description}
        return _JSON_response(request, http.BAD_REQUEST, response)


class BroadcastMessageToPlayer(OAuthResource):
    def __init__(self, api_service, secret_store):
        OAuthResource.__init__(self, secret_store)
        self.api_service = api_service

    def getChild(self, name, request):
        player_serial = int(name)
        return BroadcastMessageToPlayerSerial(player_serial, self.api_service,
                                              self.secret_store)


class BroadcastMessage(OAuthResource):
    def __init__(self, api_service, secret_store):
        OAuthResource.__init__(self, secret_store)
        self.api_service = api_service
        self.putChild('player', BroadcastMessageToPlayer(api_service,
                                                         secret_store))

    def render_POST(self, request):
        json_request_body = get_json_request_body(request)
        message = json_request_body['message']
        self.api_service.broadcast_to_all(message)
        return _JSON_response(request)


class Root(resource.Resource):
    def __init__(self, api_service, secret_store):
        resource.Resource.__init__(self)
        self.putChild('refresh_table_config',
                      RefreshTableConfig(api_service, secret_store))
        self.putChild('broadcast',
                      BroadcastMessage(api_service, secret_store))

