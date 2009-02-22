#  ICE Revision: $Id: LinearSolverLineAnalyzer.py 8144 2007-11-05 09:18:04Z bgschaid $ 
"""Analyze information from the linear solver"""

import re

linearRegExp="^(.+):  Solving for (.+), Initial residual = (.+), Final residual = (.+), No Iterations (.+)$"
    
# from FileLineAnalyzer import FileLineAnalyzer
# from TimeLineLineAnalyzer import TimeLineLineAnalyzer

from GeneralLineAnalyzer import GeneralLineAnalyzer

class GeneralLinearSolverLineAnalyzer(GeneralLineAnalyzer):
    """Parses for information about the linear solver

    Files of the form linear_<var> are written, where <var> is the
    variable for which the solver was used"""
    
    def __init__(self,doTimelines=True,doFiles=True):
        GeneralLineAnalyzer.__init__(self,titles=["Initial","Final","Iterations"],doTimelines=doTimelines,doFiles=doFiles)
        self.exp=re.compile(linearRegExp)

        if self.doTimelines:
            self.lines.setDefault(1.)
            self.lines.setExtend(True)

    def addToFiles(self,match):
        solver=match.groups()[0]
        name=match.groups()[1]
        rest=match.groups()[2:]
        self.files.write("linear_"+name,self.getTime(),rest)

    def addToTimelines(self,match):
        name=match.groups()[1]
        resid=match.groups()[2]
        final=match.groups()[3]
        iter=match.groups()[4]
        
        self.lines.setValue(name,resid)

        self.lines.setAccumulator(name+"_final","last")
        self.lines.setValue(name+"_final",final)

        self.lines.setAccumulator(name+"_iterations","sum")
        self.lines.setValue(name+"_iterations",iter)
        
class GeneralLinearSolverIterationsLineAnalyzer(GeneralLinearSolverLineAnalyzer):
    """Parses information about the linear solver and collects the iterations"""
    
    def __init__(self,doTimelines=True,doFiles=True):
        GeneralLinearSolverLineAnalyzer.__init__(self,doTimelines=doTimelines,doFiles=doFiles)

    def addToFiles(self,match):
        pass
    
    def addToTimelines(self,match):
        name=match.groups()[1]
        iter=match.groups()[4]
        
        self.lines.setAccumulator(name,"sum")
        self.lines.setValue(name,iter)


class LinearSolverLineAnalyzer(GeneralLinearSolverLineAnalyzer):
    """Parses for information about the linear solver

    Files of the form linear_<var> are written, where <var> is the
    variable for which the solver was used"""
    
    def __init__(self):
        GeneralLinearSolverLineAnalyzer.__init__(self,doTimelines=False)

class TimeLineLinearSolverLineAnalyzer(GeneralLinearSolverLineAnalyzer):
    """Parses for imformation about the linear solver and collects the residuals in timelines"""
    
    def __init__(self):
        GeneralLinearSolverLineAnalyzer.__init__(self,doFiles=False)

class TimeLineLinearIterationsSolverLineAnalyzer(GeneralLinearSolverIterationsLineAnalyzer):
    """Parses for information about the linear solver and collects the iterations in timelines"""
    
    def __init__(self):
        GeneralLinearSolverIterationsLineAnalyzer.__init__(self,doFiles=False)
