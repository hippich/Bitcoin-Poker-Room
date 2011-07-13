#!/usr/bin/env python
# coding: utf-8

import time

import oauth2
from twisted.internet.defer import succeed
from twisted.trial import unittest
from twisted.web import http, server
from twisted.web.test.test_web import DummyRequest

from pokernetwork.apiserver import OAuthResource


class DummyHTTPHeaders:
    def getAllRawHeaders(self):
        return []


class OAuthRequest(DummyRequest):
    def __init__(self):
        DummyRequest.__init__(self, [''])
        self.requestHeaders = DummyHTTPHeaders()


    def URLPath(self):
        return self.uri


def _build_oauth2_request(url, key, secret, method='GET'):
    """
    Returns an HMAC_SHA1 signed oauth2.Request object."""
    consumer = oauth2.Consumer(key=key, secret=secret)
    params = {
        'oauth_version': "1.0",
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'oauth_consumer_key': consumer.key
    }
    signed_request = oauth2.Request(method=method, url=url, parameters=params)
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    signed_request.sign_request(signature_method, consumer, None)
    return signed_request


def _build_dummy_request(key, secret, method='GET'):
    dummy_request = OAuthRequest()
    oauth2_request = _build_oauth2_request(dummy_request.uri, key, secret,
                                           method)
    print 'OAuth2 signed URL:\n', oauth2_request.to_url()
    for arg, value in oauth2_request.iteritems():
        dummy_request.addArg(arg, value)
    print 'Dummy URLPath:\n', dummy_request.URLPath()
    return dummy_request


class MockAPISecretStore(object):
    def __init__(self, secrets):
        self.secrets = secrets


    def get_secret(self, key):
        if key in self.secrets:
            return self.secrets[key]
        return None


class MockOAuthResource(OAuthResource):
    def __init__(self, secret_store):
        OAuthResource.__init__(self, secret_store)

    def render_GET(self, request):
        request.setResponseCode(http.OK)
        return "success"


def _render(resource, request):
    result = resource.render(request)
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return succeed(None)
    elif result is server.NOT_DONE_YET:
        if request.finished:
            return succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))


class OAuthResourceTests(unittest.TestCase):
    def setUp(self):
        self.key = 'some_key'
        self.secret = 'some_secret'
        secret_store = MockAPISecretStore({self.key: self.secret})
        self.resource = MockOAuthResource(secret_store)


    def _test_request(self, request, expected_status_code):
        d = _render(self.resource, request)

        def rendered(ignored):
            self.assertEquals(request.responseCode, expected_status_code)

        d.addCallback(rendered)
        return d


    def test_successful_oauth_request(self):
        request = _build_dummy_request(self.key, self.secret)
        return self._test_request(request, http.OK)


    def test_bad_oauth_request(self):
        return self._test_request(OAuthRequest(), http.BAD_REQUEST)


    def test_unauthorized_oauth_request_bad_secret(self):
        request = _build_dummy_request(self.key, 'bad_secret')
        return self._test_request(request, http.UNAUTHORIZED)


    def test_unauthorized_oauth_request_bad_key(self):
        request = _build_dummy_request('bad_key', self.secret)
        self.resource.render(request)
        self.assertEquals(request.responseCode, http.UNAUTHORIZED)

