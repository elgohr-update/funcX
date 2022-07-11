import platform

"""
Warning: based on practice, MacSafeQueue causes assertion error.
'Assertion failed: dummy == 0 (src/signaler.cpp:396)'
Use the default queue does not present a problem. 
So remove the MacSafeQueue, use multiprocessing.queue
"""

# if platform.system() == "Darin":
#     from parsl.multiprocessing import MacSafeQueue as mpQueue
# else:
from multiprocessing import Queue as mpQueue

__all__ = ("mpQueue",)
