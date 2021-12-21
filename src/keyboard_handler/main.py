import platform
import time

class KeyboardHandlerError (Exception): pass

class KeyboardHandler(object):

    def __init__(self, repeat_rate=0.0, *args, **kwargs):
        self.repeat_rate = repeat_rate #How long between accepting the same keystroke?
        self._last_key = None
        self._last_keypress_time = 0
        super(KeyboardHandler, self).__init__(*args, **kwargs)
        self.active_keys = {}
        if not hasattr(self, 'replacement_mods'):
            self.replacement_mods = {}
        if not hasattr(self, 'replacement_keys'):
            self.replacement_keys = {}

    def register_key (self, key, function):
        if key in self.active_keys:
            raise KeyboardHandlerError("Key %s is already registered to a function" % key)
        if not callable(function):
            raise TypeError("Must provide a callable to be invoked upon keypress")
        self.active_keys[key] = function

    def unregister_key (self, key, function):
        try:
            if self.active_keys[key] != function:
                raise KeyboardHandlerError("key %s is not registered to that function" % key)
        except KeyError:
            raise KeyboardHandlerError("Key %s not currently registered" % key)
        del(self.active_keys[key])

    def unregister_all_keys(self):
        for key in list(self.active_keys):
            self.unregister_key(key, self.active_keys[key])

    def handle_key (self, key):
        if self.repeat_rate and key == self._last_key and time.time() - self._last_keypress_time < self.repeat_rate:
            return
        try:
            function = self.active_keys[key]
        except KeyError:
            return
        self._last_key = key
        self._last_keypress_time = time.time()
        return function()

    def register_keys(self, keys):
        """Given a mapping of keystrokes to functions, registers all keystrokes"""
        for k in keys:
            self.register_key(k, keys[k])

    def unregister_keys(self, keys):
        """Given a mapping of keys to their functions, unregisters all provided keys."""
        for k in keys:
            self.unregister_key(k, keys[k])

    def standardize_key(self, key):
        """Takes a keystroke and places it in a standard case and order in a list."""
        working = key.split('+')
        working = [i.lower() for i in working]
        answer = []
        if "control" in working:
            answer.append("control")
        if "win" in working:
            answer.append("win")
        if "alt" in working:
            answer.append("alt")
        if "shift" in working:
            answer.append("shift")
        if working[-1] not in answer:
            answer.append(working[-1])
        return answer

    def standardize_keymap(self, keymap):
        """Given a keymap, returns the keymap standardized."""
        full = {}
        for i in keymap:
            answer = ""
            new = self.standardize_key(keymap[i])
            for (c, j) in enumerate(new):
                if c < len(new)-1:
                    answer = "%s%s+" % (answer, j)
                else:
                    answer = "%s%s" % (answer, j)
            full[i] = answer
        return full
