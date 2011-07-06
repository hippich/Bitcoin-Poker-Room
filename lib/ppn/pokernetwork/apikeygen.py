#!/usr/bin/env python
# coding: utf-8

import optparse
import random
import string
import sqlite3
import sys

from pokernetwork import apiserver

API_KEY_LENGTH = 50
API_SECRET_LENGTH = 50
ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits


def _generate_random_string(length, alphabet):
    return ''.join(random.choice(alphabet) for x in range(length))


def generate_key_secret_pair():
    key = _generate_random_string(API_KEY_LENGTH, ALPHABET)
    secret = _generate_random_string(API_SECRET_LENGTH, ALPHABET)
    return key, secret


if __name__ == '__main__':
    usage = """%prog [OPTIONS] SQLITE_DATABASE
    Generates an API key and secret, and saves them to SQLITE_DATABASE"""
    parser = optparse.OptionParser(usage=usage)
    options, args = parser.parse_args()
    try:
        sqlite_database = args[0]
    except Exception, e:
        parser.print_help()
        sys.exit(1)

    key, secret = generate_key_secret_pair()

    db = sqlite3.connect(sqlite_database)

    secret_store = apiserver.OAuthSecretStore(db)
    secret_store.save_secret(key, secret)

    print """\
    The following API key and secret pair have been saved to %s:

    API key: %s
    API secret: %s

    Please store in a safe location.""" % (sqlite_database, key, secret)
