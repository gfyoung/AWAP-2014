from threading import Thread
from time import time

class ContinuousThread(Thread):
    def __init__(self, timeout=5, target=None, group=None, name=None, args=(), kwargs={}):
        self._timeout = timeout
        self._target = target
        self._args = args
        self._kwargs = kwargs
        Thread.__init__(self, args=args, kwargs=kwargs, group=group, target=target, name=name)

    def run(self):
        depth = 1

        timeout = self._timeout**(1/2.0)
        end_time = time() + timeout
        
        while time() < end_time:
            self._kwargs['depth'] = depth
            self._most_recent_val = self._target(*self._args, **self._kwargs)
            depth += 1

    def get_most_recent_val(self):
        """ Return the most-recent return value of the thread function """
        try:
            return self._most_recent_val
        except AttributeError:
            print "Error: You ran the search function for so short a time that it couldn't even come up with any answer at all!  Returning a random column choice..."
            import random
            return random.randint(0, 6)
    
def run_search_function(board, search_fn, eval_fn, timeout = 5):
    eval_t = ContinuousThread(timeout=timeout, target = search_fn, kwargs={ 'grid': grid,
                                                                          'eval_fn': eval_fn })

    eval_t.setDaemon(True)
    eval_t.start()
    
    eval_t.join(timeout)

    return int(eval_t.get_most_recent_val())


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
