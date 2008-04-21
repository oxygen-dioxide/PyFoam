#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Error.py 2316 2007-11-09T10:40:25.919130Z bgschaid  $ 
"""Standardized Error Messages"""

import traceback
import sys

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

def __common(standard,*text):
    """Common function for errors and Warnings"""
    info=getLine(up=2)
    print >>sys.stderr, "PyFoam",standard.upper(),"on line",info[1],"of file",info[0],":",
    for t in text:
         print >>sys.stderr,t,
    print >>sys.stderr
    
def warning(*text):
    """Prints a warning message with the occuring line number
    @param text: The error message"""
    __common("Warning",*text)
    
def error(*text):
    """Prints an error message with the occuring line number and aborts
    @param text: The error message"""
    __common("Fatal Error",*text)
    sys.exit(-1)
    
def debug(*text):
    """Prints a debug message with the occuring line number
    @param text: The error message"""
    __common("Debug",*text)
    
