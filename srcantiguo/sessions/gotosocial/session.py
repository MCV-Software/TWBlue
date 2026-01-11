from sessions.mastodon import session

class Session(session.Session):
    # disable version check so Mastodon.py won't throw exceptions.
    version_check_mode = "none"
    name = "GoToSocial"

    def get_lists(self):
        """ Gets the lists that the user is subscribed to and stores them in the database. Returns None."""
        self.db["lists"] = []

    def get_muted_users(self):
        self.db["muted_users"] = []
