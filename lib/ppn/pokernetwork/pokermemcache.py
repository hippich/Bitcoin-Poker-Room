#
# -*- py-indent-offset: 4; coding: iso-8859-1 -*-
#
# Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#

# borrowed from memcache.py
import types

class MemcachedStringEncodingError(Exception):
    pass

def check_key(key, key_extra_len=0):
    """Checks sanity of key.  Fails if:
        Key length is > SERVER_MAX_KEY_LENGTH (Raises MemcachedKeyLength).
        Contains control characters  (Raises MemcachedKeyCharacterError).
        Is not a string (Raises MemcachedStringEncodingError)
    """
    if type(key) == types.TupleType: key = key[1]
    if not isinstance(key, str):
        raise MemcachedStringEncodingError, ("Keys must be str()'s, not"
                "unicode.  Convert your unicode strings using "
                "mystring.encode(charset)!")

memcache_singleton = {}
memcache_expiration_singleton = {}

class MemcacheMockup:
    class Client:
        def __init__(self, addresses, *args, **kwargs):
            self.addresses = addresses
            self.cache = memcache_singleton
            self.expiration = memcache_expiration_singleton

        def get(self, key):
            check_key(key)
            if self.cache.has_key(key):
                return self.cache[key]
            else:
                return None

        def get_multi(self, keys):
            r = {}
            for key in keys:
                if self.cache.has_key(key):
                    r[key] = self.cache[key]
            return r
        
        def set(self, key, value, time = 0):
            check_key(key)
            self.cache[key] = value
            self.expiration[key] = time

        def set_multi(self, kwargs, time = 0):
            self.cache.update(kwargs)
            for k in kwargs: self.expiration[k] = time
            return []

        def add(self, key, value, time = 0):
            if self.cache.has_key(key):
                return 0
            else:
                self.cache[key] = value
                self.expiration[key] = time                
                return 1

        def replace(self, key, value, time = 0):
            if self.cache.has_key(key):
                self.cache[key] = value
                self.expiration[key] = time
                return 1
            else:
                return 0
            
        def delete(self, key):
            check_key(key)
            try:
                del self.cache[key]
                return 1
            except:
                return 0

        def delete_multi(self, keys):
            for key in keys:
                if self.cache.has_key(key):
                    del self.cache[key]
            return 1

try:
    import memcache #pragma: no cover
except:
    memcache = MemcacheMockup #pragma: no cover

