#  ICE Revision: $Id: ConvergenceRunner.py 7858 2007-09-03 09:47:29Z bgschaid $ 
"""Stop solver at convergence"""

from AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.SteadyConvergedLineAnalyzer import SteadyConvergedLineAnalyzer

class ConvergenceRunner(AnalyzedRunner):
    """It is assumed that the provided solver is a steady state
    solver. After all the linear solvers have initial residuals below
    their limits the run is assumed to be convergent and the run is
    stopped by setting

    stopAt nextWrite;
    writeInterval 1;

    in the controlDict"""
    
    def __init__(self,analyzer,argv=None,silent=False,logname="PyFoamSolve",server=False,lam=None,restart=False):
        """See AnalyzedRunner"""
        AnalyzedRunner.__init__(self,analyzer,argv,silent,logname,server=server,lam=lam,restart=restart)
        
        self.analyzer.addAnalyzer("Convergence",SteadyConvergedLineAnalyzer())
        
    def lineHandle(self,line):
        """Not to be called: Stops the solver"""
        AnalyzedRunner.lineHandle(self,line)

        if not self.analyzer.goOn():
            self.stopGracefully()
            
        