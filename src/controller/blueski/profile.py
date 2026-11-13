"""Coordinate profile queries without depending on wx or SDK clients."""
import logging
import requests
from controller.blueski.profile_format import format_profile
from sessions.blueski.profile_policy import available_profile_actions

log = logging.getLogger(__name__)


def download_image(url):
    if not url:
        return None
    try:
        with requests.get(url, timeout=10) as response:
            return response.content if response.status_code == 200 else None
    except requests.RequestException:
        log.debug('Profile image download failed', exc_info=True)
        return None


class ProfileController:
    def __init__(self, session, view, execute, dispatch, download=download_image):
        self.session = session
        self.view = view
        self.execute = execute
        self.dispatch = dispatch
        self._closed = False
        self._generation = 0
        self.download = download
        self._acting = False

    def load_images(self, banner, avatar):
        generation = self._generation
        def deliver(images):
            if not self._closed and generation == self._generation:
                self.view._draw_images(*images)
        def query():
            images = (self.download(banner), self.download(avatar))
            self.dispatch(deliver, images)
        if not self._closed:
            self.execute(query)

    def own_did(self):
        return self.session.get_own_did()

    def available_actions(self, profile):
        if not profile:
            return frozenset()
        return available_profile_actions(profile.get('did'), self.own_did(), profile.get('viewer') or {})

    def act(self, command, did, viewer, identifier):
        if self._closed or self._acting:
            return
        allowed = {'follow_user', 'unfollow_user', 'mute_user', 'unmute_user',
                   'block_user', 'unblock_user'}
        self._acting = True
        self.view.show_action_loading(command)

        def deliver(error):
            self._acting = False
            if self._closed:
                return
            self.view.finish_user_action(error)
            if error is None:
                self.load(identifier)

        def query():
            error = None
            try:
                if command not in allowed:
                    raise RuntimeError('This action is not supported yet.')
                if not did:
                    raise RuntimeError('User identifier (DID) not available for this action.')
                argument = did
                if command in {'unfollow_user', 'unblock_user'}:
                    key = 'following' if command == 'unfollow_user' else 'blocking'
                    argument = viewer.get(key)
                    if not argument:
                        raise RuntimeError('Follow information not available.' if key == 'following'
                                           else 'Block information not available.')
                if not getattr(self.session, command)(argument):
                    raise RuntimeError('Action failed.')
            except Exception as exc:
                error = exc
            self.dispatch(deliver, error)
        self.execute(query)

    def load(self, identifier):
        if self._closed:
            return
        self._generation += 1
        generation = self._generation
        self.view.show_profile_loading()

        def deliver(method, value):
            if not self._closed and generation == self._generation:
                if method == '_apply_profile_data':
                    self.view.show_profile_actions(self.available_actions(value))
                getattr(self.view, method)(value)

        def query():
            try:
                raw = self.session.get_profile(identifier)
                profile = format_profile(raw) if raw else None
            except Exception as error:
                log.exception('Error loading profile for %s', identifier)
                self.dispatch(deliver, '_apply_profile_error', error)
            else:
                self.dispatch(deliver, '_apply_profile_data', profile)

        self.execute(query)

    def close(self):
        self._closed = True
        self.view = None
