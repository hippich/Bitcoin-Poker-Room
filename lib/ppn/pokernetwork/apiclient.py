#!/usr/bin/env python
# coding: utf-8

import optparse
import sys
import time
import urllib2

import oauth2


class RequestError(Exception):
    pass


def build_request(url, consumer, method='GET'):
    """Returns a signed HMAC_SHA1 oauth2.Request object."""
    params = {
        'oauth_version': "1.0",
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'oauth_consumer_key': consumer.key
    }

    req = oauth2.Request(method=method, url=url, parameters=params)
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)
    return req


def perform_api_request(url, key, secret):
    consumer = oauth2.Consumer(key=key, secret=secret)
    request = build_request(url, consumer)
    request_url = request.to_url()

    print 'REQUEST:', urllib2.unquote(request_url)

    response_code = 200
    response_data = None
    try:
        u = urllib2.urlopen(request_url)
        response_data = u.read()
    except urllib2.HTTPError, e:
        response_code = e.code
        response_data = e.read()
    except urllib2.URLError, e:
        raise RequestError(e)

    print 'RESPONSE: [%d] %s' % (response_code, response_data)


if __name__ == '__main__':
    usage = '%prog [OPTIONS] URL'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-k', '--key', dest='key', metavar='API_KEY',
                      help='required')
    parser.add_option('-s', '--secret', dest='secret', metavar='SECRET',
                      help='required')
    options, args = parser.parse_args()
    try:
        url = args[0]
        key = options.key
        secret = options.secret
    except Exception, e:
        parser.print_help()
        print e
        sys.exit(1)

    perform_api_request(url, key, secret)
