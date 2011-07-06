#!/usr/bin/env python
# coding: utf-8


import sys
sys.path.insert(0, ".")
sys.path.insert(0, "..")

import optparse
import random
import string

from pokernetwork import apiserver, pokerdatabase, pokernetworkconfig

API_KEY_LENGTH = 50
API_SECRET_LENGTH = 50
ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits


def _generate_random_string(length, alphabet):
    return ''.join(random.choice(alphabet) for x in range(length))


def _load_config(configpath):
    config = pokernetworkconfig.Config([''])
    config.load(configpath)
    if not config.header:
        raise RuntimeError('Could not load config: %s' % configpath)
    return config


def generate_key_secret_pair():
    key = _generate_random_string(API_KEY_LENGTH, ALPHABET)
    secret = _generate_random_string(API_SECRET_LENGTH, ALPHABET)
    return key, secret


if __name__ == '__main__':
    usage = """%prog [OPTIONS] EMAIL SERVER_CONFIG
    Generates an API key and secret for a given user EMAIL, and saves the result
    to the pokerserver database as specified in SERVER_CONFIG"""
    parser = optparse.OptionParser(usage=usage)
    options, args = parser.parse_args()
    try:
        email = args[0]
        configpath = args[1]
    except Exception, e:
        parser.print_help()
        sys.exit(1)

    config = _load_config(configpath)
    db = pokerdatabase.PokerDatabase(config)

    api_user_store = apiserver.APIUserStore(db)

    key, secret = generate_key_secret_pair()
    api_user_store.add_user(email, key, secret)

    print """\
    The following API user has been added:

    email: %s
    key: %s
    secret: %s

    Please store this information in a safe location.""" % (email, key, secret)
