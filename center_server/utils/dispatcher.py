


class DispatcherMixin():
    _actions = {}

    # chil class must have self._actions = {{action_type}: [], ...} - dict
    def dispatch_actions(self, action_type, *args, **kwargs):
        print(f'{action_type} callback with: {args} and {kwargs}')
        for action in self._actions[action_type]:
            action(*args, **kwargs)
        
    def register_event(self, action_type):
        def decorator(function):
                self._actions[action_type].append(function)
        return decorator

CLOSE_KEY = '*./,/.{quit}*'
BUFFER_SIZE = 1024