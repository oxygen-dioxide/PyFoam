#  ICE Revision: $Id: PlotRunner.py 10071 2009-03-02 09:39:46Z bgschaid $ 
"""
Class that implements pyFoamPlotRunner
"""

from PyFoamApplication import PyFoamApplication

from PyFoam.Execution.GnuplotRunner import GnuplotRunner

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.Error import warning

from CommonStandardOutput import CommonStandardOutput
from CommonPlotLines import CommonPlotLines
from CommonParallel import CommonParallel
from CommonRestart import CommonRestart
from CommonPlotOptions import CommonPlotOptions
from CommonClearCase import CommonClearCase
from CommonReportUsage import CommonReportUsage
from CommonSafeTrigger import CommonSafeTrigger
from CommonWriteAllTrigger import CommonWriteAllTrigger
from CommonLibFunctionTrigger import CommonLibFunctionTrigger
from CommonServer import CommonServer

from os import path

class PlotRunner(PyFoamApplication,
                 CommonPlotOptions,
                 CommonPlotLines,
                 CommonSafeTrigger,
                 CommonWriteAllTrigger,
                 CommonLibFunctionTrigger,
                 CommonClearCase,
                 CommonServer,
                 CommonReportUsage,
                 CommonParallel,
                 CommonRestart,
                 CommonStandardOutput):
    def __init__(self,args=None):
        description="""
        runs an OpenFoam solver needs the usual 3 arguments (<solver>
        <directory> <case>) and passes them on (plus additional arguments).
        Output is sent to stdout and a logfile inside the case directory
        (PyFoamSolver.logfile) Information about the residuals is output as
        graphs
        
        If the directory contains a file customRegexp this is automatically
        read and the regular expressions in it are displayed
        """
        CommonPlotOptions.__init__(self,persist=True)
        CommonPlotLines.__init__(self)
        PyFoamApplication.__init__(self,
                                   exactNr=False,
                                   args=args,
                                   description=description)
        
    def addOptions(self):
        CommonClearCase.addOptions(self)

        CommonPlotOptions.addOptions(self)
        
        self.parser.add_option("--steady-run",
                               action="store_true",
                               default=False,
                               dest="steady",
                               help="This is a steady run. Stop it after convergence")
        
        CommonReportUsage.addOptions(self)
        CommonStandardOutput.addOptions(self)
        CommonParallel.addOptions(self)
        CommonRestart.addOptions(self)
        CommonPlotLines.addOptions(self)
        CommonSafeTrigger.addOptions(self)
        CommonWriteAllTrigger.addOptions(self)
        CommonLibFunctionTrigger.addOptions(self)
        CommonServer.addOptions(self)
        
    def run(self):
        self.processPlotOptions()
        
        cName=self.parser.casePath()
        self.checkCase(cName)

        self.processPlotLineOptions(autoPath=cName)
        
        sol=SolutionDirectory(cName,archive=None)
        
        self.clearCase(sol)

        lam=self.getParallel()
        
        self.setLogname()
        
        run=GnuplotRunner(argv=self.parser.getArgs(),
                          smallestFreq=self.opts.frequency,
                          persist=self.opts.persist,
                          plotLinear=self.opts.linear,
                          plotCont=self.opts.cont,
                          plotBound=self.opts.bound,
                          plotIterations=self.opts.iterations,
                          plotCourant=self.opts.courant,
                          plotExecution=self.opts.execution,
                          plotDeltaT=self.opts.deltaT,
                          customRegexp=self.plotLines(),
                          writeFiles=self.opts.writeFiles,
                          hardcopy=self.opts.hardcopy,
                          hardcopyFormat=self.opts.hardcopyformat,
                          server=self.opts.server,
                          lam=lam,
                          raiseit=self.opts.raiseit,
                          steady=self.opts.steady,
                          progress=self.opts.progress,
                          restart=self.opts.restart,
                          logname=self.opts.logname,
                          noLog=self.opts.noLog)

        self.addSafeTrigger(run,sol,steady=self.opts.steady)
        self.addWriteAllTrigger(run,sol)
        self.addLibFunctionTrigger(run,sol)        
        
        run.start()

        self.reportUsage(run)
