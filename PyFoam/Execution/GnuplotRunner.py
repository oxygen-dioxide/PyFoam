#  ICE Revision: $Id: GnuplotRunner.py 9416 2008-09-22 08:00:13Z bgschaid $ 
"""Runner that outputs the residuals of the linear solver with Gnuplot"""

from StepAnalyzedCommon import StepAnalyzedCommon
from BasicRunner import BasicRunner
from BasicWatcher import BasicWatcher

from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.LogAnalysis.RegExpLineAnalyzer import RegExpLineAnalyzer
from PyFoam.LogAnalysis.SteadyConvergedLineAnalyzer import SteadyConvergedLineAnalyzer
from PyFoam.Basics.GnuplotTimelines import GnuplotTimelines
from PyFoam.Basics.TimeLineCollection import signedMax

from os import path

class GnuplotCommon(StepAnalyzedCommon):
    """Class that collects the Gnuplotting-Stuff for two other classes"""
    def __init__(self,
                 fname,
                 smallestFreq=0.,
                 persist=None,
                 splitThres=2048,
                 plotLinear=True,
                 plotCont=True,
                 plotBound=True,
                 plotIterations=False,
                 plotCourant=False,
                 plotExecution=False,
                 plotDeltaT=False,
                 hardcopy=False,
                 customRegexp=None,
                 writeFiles=False,
                 raiseit=False,
                 progress=False,
                 start=None,
                 end=None):
        """
        TODO: Docu
        """
        StepAnalyzedCommon.__init__(self,
                                    fname,
                                    BoundingLogAnalyzer(doTimelines=True,
                                                        doFiles=writeFiles,
                                                        progress=progress),
                                    smallestFreq=smallestFreq)
        
        self.plots={}
        
        if plotLinear:
            self.plots["linear"]=GnuplotTimelines(self.getAnalyzer("Linear").lines,
                                                  persist=persist,
                                                  raiseit=raiseit,
                                                  forbidden=["final","iterations"],
                                                  start=start,
                                                  end=end,
                                                  logscale=True)
            self.getAnalyzer("Linear").lines.setSplitting(splitThres=splitThres,splitFun=max)
        
            self.plots["linear"].title("Residuals")

        if plotCont:
            self.plots["cont"]=GnuplotTimelines(self.getAnalyzer("Continuity").lines,
                                                persist=persist,
                                                alternateAxis=["Global"],
                                                raiseit=raiseit,
                                                start=start,
                                                end=end)
            self.plots["cont"].set_string("ylabel \"Cumulative\"")
            self.plots["cont"].set_string("y2label \"Global\"")
            self.getAnalyzer("Continuity").lines.setSplitting(splitThres=splitThres)

            self.plots["cont"].title("Continuity")
 
        if plotBound:
            self.plots["bound"]=GnuplotTimelines(self.getAnalyzer("Bounding").lines,
                                                 persist=persist,
                                                 raiseit=raiseit,
                                                 start=start,
                                                 end=end)
            self.getAnalyzer("Bounding").lines.setSplitting(splitThres=splitThres,splitFun=signedMax)
            self.plots["bound"].title("Bounded variables")

        if plotIterations:
            self.plots["iter"]=GnuplotTimelines(self.getAnalyzer("Iterations").lines,
                                                persist=persist,
                                                with="steps",
                                                raiseit=raiseit,
                                                start=start,
                                                end=end)
            self.getAnalyzer("Iterations").lines.setSplitting(splitThres=splitThres)

            self.plots["iter"].title("Iterations")

        if plotCourant:
            self.plots["courant"]=GnuplotTimelines(self.getAnalyzer("Courant").lines,
                                                   persist=persist,
                                                   raiseit=raiseit,
                                                   start=start,
                                                   end=end)
            self.getAnalyzer("Courant").lines.setSplitting(splitThres=splitThres)

            self.plots["courant"].title("Courant")
 
        if plotDeltaT:
            self.plots["deltaT"]=GnuplotTimelines(self.getAnalyzer("DeltaT").lines,
                                                  persist=persist,
                                                  raiseit=raiseit,
                                                  start=start,
                                                  end=end,
                                                  logscale=True)
            self.getAnalyzer("DeltaT").lines.setSplitting(splitThres=splitThres)

            self.plots["deltaT"].title("DeltaT")
 
        if plotExecution:
            self.plots["execution"]=GnuplotTimelines(self.getAnalyzer("Execution").lines,
                                                     persist=persist,
                                                     with="steps",
                                                     raiseit=raiseit,
                                                     start=start,
                                                     end=end)
            self.getAnalyzer("Execution").lines.setSplitting(splitThres=splitThres)

            self.plots["execution"].title("Execution Time")

        if customRegexp:
            self.plotCustom=[]
            for i in range(len(customRegexp)):
                name="Custom%02d" % i
                expr=customRegexp[i]
                titles=[]
                theTitle="Custom %d" % i
                options = { "persist" : persist,
                            "raiseit" : raiseit,
                            "start"   : start,
                            "end"     : end }
                
                if expr[0]=="{":
                    data=eval(expr)
                    expr=data["expr"]
                    if "name" in data:
                        name+="_"+data["name"]
                        name=name.replace(" ","_").replace(path.sep,"Slash")
                        theTitle+=" - "+data["name"]
                    if "titles" in data:
                        titles=data["titles"]
                    for o in ["alternateAxis","logscale","with","ylabel","y2label"]:
                        if o in data:
                            options[o]=data[o]

                self.addAnalyzer(name,
                                 RegExpLineAnalyzer(name.lower(),
                                                    expr,titles=titles,
                                                    doTimelines=True,
                                                    doFiles=writeFiles))
                plotCustom=GnuplotTimelines(*[self.getAnalyzer(name).lines],
                                            **options)
                self.getAnalyzer(name).lines.setSplitting(splitThres=splitThres)
                plotCustom.title(theTitle)
                self.plots["custom%04d" % i]=plotCustom

            
            self.reset()
            
        self.hardcopy=hardcopy
           
    def timeHandle(self):
        for p in self.plots:
            self.plots[p].redo()
            
    def stopHandle(self):
        self.timeHandle()
        if self.hardcopy:
            for p in self.plots:
                self.plots[p].hardcopy(filename=p+".ps",color=True)
            
class GnuplotRunner(GnuplotCommon,BasicRunner):
    def __init__(self,
                 argv=None,
                 smallestFreq=0.,
                 persist=None,
                 plotLinear=True,
                 plotCont=True,
                 plotBound=True,
                 plotIterations=False,
                 plotCourant=False,
                 plotExecution=False,
                 plotDeltaT=False,
                 customRegexp=None,
                 hardcopy=False,
                 writeFiles=False,
                 server=False,
                 lam=None,
                 raiseit=False,
                 steady=False,
                 progress=False,
                 restart=False,
                 logname=None):
        """@param smallestFreq: smallest Frequency of output
        @param persist: Gnuplot window persistst after run
        @param steady: Is it a steady run? Then stop it after convergence"""
        BasicRunner.__init__(self,
                             argv=argv,
                             silent=progress,
                             server=server,
                             lam=lam,
                             restart=restart,
                             logname=logname)
        GnuplotCommon.__init__(self,
                               "Gnuplotting",
                               smallestFreq=smallestFreq,
                               persist=persist,
                               plotLinear=plotLinear,
                               plotCont=plotCont,
                               plotBound=plotBound,
                               plotIterations=plotIterations,
                               plotCourant=plotCourant,
                               plotExecution=plotExecution,
                               plotDeltaT=plotDeltaT,
                               customRegexp=customRegexp,
                               hardcopy=hardcopy,
                               writeFiles=writeFiles,
                               raiseit=raiseit,
                               progress=progress)
        self.steady=steady
        if self.steady:
            self.steadyAnalyzer=SteadyConvergedLineAnalyzer()
            self.addAnalyzer("Convergence",self.steadyAnalyzer)

    def lineHandle(self,line):
        """Not to be called: Stops the solver"""
        GnuplotCommon.lineHandle(self,line)

        if self.steady:
            if not self.steadyAnalyzer.goOn():
                self.stopGracefully()
                
    def stopHandle(self):
        """Not to be called: Restores controlDict"""
        GnuplotCommon.stopHandle(self)
        BasicRunner.stopHandle(self)
             
class GnuplotWatcher(GnuplotCommon,BasicWatcher):
    def __init__(self,
                 logfile,
                 smallestFreq=0.,
                 persist=None,
                 silent=False,
                 tailLength=1000,
                 sleep=0.1,
                 plotLinear=True,
                 plotCont=True,
                 plotBound=True,
                 plotIterations=False,
                 plotCourant=False,
                 plotExecution=False,
                 plotDeltaT=False,
                 customRegexp=None,
                 writeFiles=False,
                 hardcopy=False,
                 raiseit=False,
                 progress=False,
                 start=None,
                 end=None):
        """@param smallestFreq: smallest Frequency of output
        @param persist: Gnuplot window persistst after run"""
        BasicWatcher.__init__(self,
                              logfile,
                              silent=(silent or progress),
                              tailLength=tailLength,
                              sleep=sleep)
        GnuplotCommon.__init__(self,
                               logfile,
                               smallestFreq=smallestFreq,
                               persist=persist,
                               plotLinear=plotLinear,
                               plotCont=plotCont,
                               plotBound=plotBound,
                               plotIterations=plotIterations,
                               plotCourant=plotCourant,
                               plotExecution=plotExecution,
                               plotDeltaT=plotDeltaT,
                               customRegexp=customRegexp,
                               hardcopy=hardcopy,
                               writeFiles=writeFiles,
                               raiseit=raiseit,
                               progress=progress,
                               start=start,
                               end=end)
        
    def startHandle(self):
        self.bakFreq=self.freq
        self.freq=3600
        
    def tailingHandle(self):
        self.freq=self.bakFreq
        self.oldtime=0
        
        