from threading import Thread
from time import time

class ContinuousThread(Thread):
    def __init__(self, game, timeout=10, target=None, group=None, name=None, args=(), kwargs={}):
        self._timeout = timeout
        self._target = target
        self._args = args
        self._kwargs = kwargsw
        Thread.__init__(self, args=args, kwargs=kwargs, group=group, target=target, name=name)

    def run(self):
        depth = 1

        timeout = self._timeout**(0.5)
        end_time = time() + timeout
        
        while time() < end_time:
            self._kwargs['depth'] = depth
            self._most_recent_val = self._target(*self._args, **self._kwargs)    
            depth += 1

    def get_most_recent_val(self):
        try:
            return self._most_recent_val
            
        except AttributeError:
            first_legal_move = game.get_legal_moves(yield_first=True)
            return first_legal_move
    
def run_search_function(game, search_fn, timeout=10):
    eval_t = ContinuousThread(game, timeout=timeout, target = search_fn, kwargs={'depth': depth})

    eval_t.setDaemon(True)
    eval_t.start()
    
    eval_t.join(timeout)

    return eval_t.get_most_recent_val()

class memoize(object):
    def __init__(self, fn):
        self.fn = fn
        self.memocache = {}

    def __call__(self, *args, **kwargs):
        memokey = ( args, tuple( sorted(kwargs.items()) ) )
        if memokey in self.memocache:
            return self.memocache[memokey]
        
        else:
            val = self.fn(*args, **kwargs)
            self.memocache[memokey] = val
            return val
