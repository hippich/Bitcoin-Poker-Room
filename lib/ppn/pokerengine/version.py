# -*- python -*-
#
# Copyright (C) 2006 - 2010 Loic Dachary <loic@dachary.org>
# Copyright (C) 2005, 2006 Mekensleep
#
# Mekensleep
# 26 rue des rosiers
# 75004 Paris
#       licensing@mekensleep.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors:
#  Loic Dachary <loic@dachary.org>
#
# 
from types import StringType
import re
from pokerengine import version_number

class Version:

    verbose = 0
    
    version_re = re.compile(r'^(\d+)\.(\d+)\.(\d+)$',
                            re.VERBOSE)


    upgrade_re = re.compile(r'.*?(\d+\.\d+\.\d+)-(\d+\.\d+\.\d+)',
                            re.VERBOSE)

    def __init__ (self, vstring=None):
        if vstring:
            self.parse(vstring)

    def __repr__ (self):
        return "%s ('%s')" % (self.__class__.__name__, str(self))

    def __str__ (self):
        return "%d.%d.%d" % self.version

    def __hash__(self):
        return hash(str(self))

    def __cmp__ (self, other):
        if isinstance(other, StringType):
            other = Version(other)

        return cmp(self.version, other.version)

    def __add__(self, num):
        ver = Version()
        ver.version = (self.version[0], self.version[1], self.version[2] + num)
        return ver
        
    def __iadd__(self, num):
        self.version = (self.version[0], self.version[1], self.version[2] + num)
        return self
        
    def sub(ver, num):
        version = list(ver.version)
        if version[2] - num < 0:
            if version[1] - num < 0:
                if version[0] - num < 0:
                    raise UserWarning, "cannot subtract %d from version %s" % ( num, str(ver) )
                else:
                    version[0] -= num
            else:
                version[1] -= num
        else:
            version[2] -= num
        ver.version = tuple(version)
        return ver

    sub = staticmethod(sub)

    def __isub__(self, num):
        return Version.sub(self, num)
        
    def __sub__(self, num):
        return Version.sub(Version(str(self)), num)

    def major(self):
        return self.version[0]
    
    def medium(self):
        return self.version[1]
    
    def minor(self):
        return self.version[2]

    def parse(self, vstring):
        match = Version.version_re.match(vstring)
        if not match:
            raise ValueError, "invalid version number '%s'" % vstring

        (major, medium, minor) = match.groups()

        self.version = tuple(map(int, [major, medium, minor]))

    def upgradeChain(self, desired_version, strings):
        current_version = self
        upgrade_matrix = {}
        for string in strings:
            match = Version.upgrade_re.match(string)
            if match:
                ( version_from, version_to ) = map(Version, match.groups())
                if ( ( version_from >= current_version and version_from < desired_version )
                     and ( version_to > current_version and version_to <= desired_version ) ):
                    upgrade_matrix.setdefault(version_from, {})
                    if upgrade_matrix[version_from].has_key(version_to):
                        if Version.verbose >= 0: print "Version: duplicate upgrade string (%s => %s) keep %s, ignore %s" % ( version_from, version_to, upgrade_matrix[version_from][version_to], string)
                    else:
                        upgrade_matrix[version_from][version_to] = string
        #
        # Each time a version requires an upgrade (presumably for database or configuration
        # file changes), a string of the kind upgrade-1.0.1-1.0.2 indicates
        # the availability of an upgrade from version 1.0.1 to version 1.0.2.
        #
        # When switching from version 1.0.0 to version 1.0.6,
        # upgradeChain return upgrade-1.0.1-1.0.2 meaning that this
        # upgrade must be applied. If there also is an
        # upgrade-1.0.3-1.0.5, upgradeChain will return ( upgrade-1.0.1-1.0.2, upgrade-1.0.3-1.0.5 )
        # meaning that both upgrades must be applied in that order.
        #
        # If there was a string upgrade-0.9.0-1.0.0 or
        # upgrade-3.0.0-3.1.0 in the list of available upgrades, they
        # would be ignored.
        #
        # If there are more than one upgrade from a given version (for instance
        # upgrade-1.0.0-1.0.1 and upgrade-1.0.0-1.0.4), the one that allows to
        # upgrade to the highest version is preferred.
        #
        chain = []
        while current_version != desired_version:
            candidate_versions = filter(lambda version: version >= current_version, upgrade_matrix.keys())
            if candidate_versions:
                candidate_version = min(candidate_versions)
                upgrades = upgrade_matrix[candidate_version]
                current_version = max(upgrades.keys())
                chain.append(upgrades[current_version])
            else:
                #
                # There is not necessarily an upgrade file reaching the desired version,
                # for instance if there was no change.
                #
                break
        return chain

version = Version(version_number)
