from __future__ import with_statement
'''
Implements a basic future.
Provided that it is accessed by the set and get methods,
this enforces write-once semantics.

TODO: implement a faster C version
@author: Tim Armstrong
'''
import threading

class FutureSetTwiceException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class Future:
    def __init__(self, function=None):
        """
        Function is a 0-arg function that will be executed
        to get result if not filled
        """
        self.__data = None
        self.__isset = False
        self.__function = function # will be set to None once run
        self.__cond = threading.Condition()
        self.__merged = []
    
    def __repr__(self):
        with self.__cond:
            if self.__isset:
                return "<future: %s>" % repr(self.__data)
            else:
                return "<future: unset, fn %s>" % repr(self.__function)    
            self.__cond.release()
        
    def get(self):
        """
        Get the value of a future.  If it is
        not available, block until it is
        """
        with self.__cond:
            if self.__function is None:
                # wait for it to be filled
                while not self.__isset:
                    self.__cond.wait()
                res = self.__data
            else:
                # run the function and
                # fill ourselves
                fun = self.__function
                self.__function = None
                # release lock to run function
                self.__cond.release()
                try:
                    res = fun()
                finally:
                    self.__cond.acquire()
                self.__data = res
                self.__isset = True
                self.__cond.notifyAll()
            return res
    
    def set(self,data):
        """
        Sets the value of a future.  This is only allowed
        to be done once
        """

        with self.__cond:
            if self.__isset:
                raise FutureSetTwiceException("A thread attempted to set a filled"
                                + "future a second time")
            self.__isset = True
            self.__data = data
            for f in self.__merged:
                f.set(data)
            self.__cond.notifyAll()
            
            
    def merge_future(self, other):
        """
        Make the value of this future automatically propagate to another future.
        """
        assert(not other.isSet())
        with self.__cond:
            if self.__isset:
                other.set(self.__data)
            else:
                self.__merged.append(other)

    def isSet(self):
        with self.__cond:
            res = self.__isset
        return res
