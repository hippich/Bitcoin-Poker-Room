#!/usr/bin/env python
# coding: utf-8

import BaseHTTPServer
import optparse
import sys
import time
import urllib2

import oauth2


def build_request(url, key, secret, body=''):
    """Returns a signed HMAC_SHA1 oauth2.Request object."""
    consumer = oauth2.Consumer(key=key, secret=secret)
    params = {
        'oauth_version': "1.0",
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'oauth_consumer_key': consumer.key
    }

    method = 'GET'
    if body is not '':
        method = 'POST'

    req = oauth2.Request(method=method, url=url, body=body,
                         parameters=params)
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)
    return req


def __perform_api_request(request):
    url = request.to_url()
    body = request.body

    response_code = None
    response_data = ''
    response_headers = {}
    try:
        request = urllib2.Request(url)
        if body is not '':
            headers = {'Content-Type': 'application/json',
                       'Content-Length': str(len(body))}
            request = urllib2.Request(url, body, headers)
        response = urllib2.urlopen(request)
        response_code = response.code
        response_headers = response.info()
        response_data = response.read()
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'Failed to perform request: ', e.reason
            return
        elif hasattr(e, 'code'):
            response_code = e.code
            response_headers = e.info()
            response_data = e.read()

    status = BaseHTTPServer.BaseHTTPRequestHandler.responses[response_code][0]
    print 'Status:', response_code, status
    for header in response_headers:
        print header, ':', response_headers[header]
    print
    print response_data


if __name__ == '__main__':
    usage = '%prog [--sign] [-k|--key <API_KEY>] [-s|--secret <SECRET>] '\
            '[-b|--body <BODY>] <URL>'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-k', '--key', dest='key', metavar='API_KEY',
                      help='Required')
    parser.add_option('-s', '--secret', dest='secret', metavar='SECRET',
                      help='Required')
    parser.add_option('-b', '--body', dest='body', default='', metavar='BODY',
                      help='If specified, a POST request will be '
                           'performed with BODY as the request body.')
    parser.add_option('--sign', action='store_true', dest='sign',
                      help='Generates a signed request URL. Does not perform '
                           'the request.')
    options, args = parser.parse_args()

    key = options.key
    secret = options.secret
    body = options.body

    if len(args) < 1 or key is None or secret is None:
        parser.print_help()
        sys.exit(1)

    url = args[0]

    request = build_request(url, key, secret, body)

    print '\n', urllib2.unquote(request.to_url()), '\n'

    if not options.sign:
        __perform_api_request(request)
