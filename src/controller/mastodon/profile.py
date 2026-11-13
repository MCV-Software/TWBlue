"""Profile coordination for Mastodon and inherited GoToSocial sessions."""
import logging
import requests
from .profile_format import format_profile
from sessions.mastodon.profile_policy import available_profile_actions

log = logging.getLogger(__name__)


def download_image(url):
    if not url:
        return None
    try:
        with requests.get(url, timeout=10) as response:
            return response.content if response.status_code == 200 else None
    except requests.RequestException:
        log.debug('Could not download profile image', exc_info=True)
        return None


class ProfileController:
    def __init__(self, session, view, execute, dispatch, download=download_image):
        self.session, self.view = session, view
        self.execute, self.dispatch, self.download = execute, dispatch, download
        self.closed = False
        self._acting = False

    def load(self, identifier):
        if self.closed:
            return
        def deliver(user, data, error):
            if self.closed:
                return
            if error:
                self.view.show_error(error)
            elif user:
                self.view.show_profile(user, data, self)
            else:
                self.view.show_error(RuntimeError('User profile not found.'))
        def query():
            try:
                user = self.session.get_profile(identifier)
                data = format_profile(user)
                data.actions, data.follow_requested = self._profile_state(identifier)
            except Exception as error:
                self.dispatch(deliver, None, None, error)
            else:
                self.dispatch(deliver, user, data, None)
        self.execute(query)

    def _actions(self, identifier):
        return self._profile_state(identifier)[0]

    def _profile_state(self, identifier):
        own = self.session.get_own_account_id()
        if str(identifier) == str(own):
            return frozenset(), False
        relationship = self.session.get_profile_relationship(identifier)
        requested = relationship.get('requested', False) if isinstance(relationship, dict) else getattr(relationship, 'requested', False)
        return available_profile_actions(identifier, own, relationship), bool(requested)

    def load_relationship(self, identifier):
        def deliver(actions, requested, error):
            if not self.closed:
                self.view.show_follow_requested(requested)
                self.view.show_profile_actions(actions)
                if error:
                    self.view.show_relationship_error(error)
        def query():
            try:
                actions, requested = self._profile_state(identifier)
            except Exception as error:
                self.dispatch(deliver, frozenset(), False, error)
            else:
                self.dispatch(deliver, actions, requested, None)
        if not self.closed:
            self.execute(query)

    def act(self, command, identifier):
        if self.closed or self._acting:
            return
        self._acting = True
        self.view.show_action_loading(command)
        def deliver(error):
            self._acting = False
            if not self.closed:
                self.view.finish_user_action(error)
                if error is None:
                    self.load(identifier)
        def query():
            error = None
            try:
                if command not in self._actions(identifier):
                    raise RuntimeError('This action is not available.')
                self.session.perform_user_action(command, identifier)
            except Exception as exc:
                error = exc
            self.dispatch(deliver, error)
        self.execute(query)

    def load_images(self, header, avatar):
        def deliver(images):
            if not self.closed:
                self.view.show_images(*images)
        def query():
            self.dispatch(deliver, (self.download(header), self.download(avatar)))
        if not self.closed:
            self.execute(query)

    def close(self):
        self.closed = True
        self.view = None
