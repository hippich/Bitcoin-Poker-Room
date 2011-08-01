from twisted.internet import reactor, defer

class PokerLockMockup:
    def __init__(self, params):
        pass
    def isAlive(self):
        return True
    def close(self):
        pass
    def start(self):
        pass
    def acquire(self, name, timeout):
        d = defer.Deferred()
        reactor.callLater(0.1, lambda: d.callback(name))
        return d
    def release(self, name):
        pass

from pokernetwork import pokercashier
pokercashier.PokerLock = PokerLockMockup
