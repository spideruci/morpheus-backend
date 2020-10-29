from datetime import datetime
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def timer(f):
    if not timer.enabled:
        return f

    @wraps(f)
    def __timer(*args, **kwargs):
        start = datetime.now()
        result = f(*args, **kwargs)
        end = datetime.now()
        
        diff = end - start
        logger.debug(f'Execution time of {f.__name__}: {diff}')
        return result
    
    return __timer

timer.enabled=False