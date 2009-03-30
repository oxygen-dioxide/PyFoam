#  ICE Revision: $Id: Error.py 9616 2008-11-03 09:16:25Z bgschaid $ 
"""Standardized Error Messages"""

import traceback
import sys

from PyFoam.Basics.TerminalFormatter import TerminalFormatter

defaultFormat=TerminalFormatter()
defaultFormat.getConfigFormat("error")
defaultFormat.getConfigFormat("warning",shortName="warn")

def getLine(up=0):
     try:  # just get a few frames
         f = traceback.extract_stack(limit=up+2)
         if f:
            return f[0]
     except:
         if __debug__:
             traceback.print_exc()
             pass
         return ('', 0, '', None)

def __common(format,standard,*text):
    """Common function for errors and Warnings"""
    info=getLine(up=2)
    if format:
         print >>sys.stderr,format,
    print >>sys.stderr, "PyFoam",standard.upper(),"on line",info[1],"of file",info[0],":",
    for t in text:
         print >>sys.stderr,t,
    print >>sys.stderr,defaultFormat.reset
    
def warning(*text):
    """Prints a warning message with the occuring line number
    @param text: The error message"""
    __common(defaultFormat.warn,"Warning",*text)
    
def error(*text):
    """Prints an error message with the occuring line number and aborts
    @param text: The error message"""
    __common(defaultFormat.error,"Fatal Error",*text)
    sys.exit(-1)
    
def debug(*text):
    """Prints a debug message with the occuring line number
    @param text: The error message"""
    __common(None,"Debug",*text)
    
class PyFoamException(Exception):
     """The simplest exception for PyFoam"""

     def __init__(self,descr):
          self.descr=descr

     def __str__(self):
          return "Problem in PyFoam: '"+self.descr+"'"
          