class PokerAuth:
    def __init__(self, db, settings):
        self.gotcha = 1

def get_auth_instance(db, settings):
    return PokerAuth(db, settings)
