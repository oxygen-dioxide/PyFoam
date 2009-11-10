#  ICE Revision: $Id: MeshUtilityRunner.py 10473 2009-05-25 08:00:21Z bgschaid $ 
"""
Application class that implements pyFoamMeshUtilityRunner
"""

from os import listdir,path,system

from PyFoamApplication import PyFoamApplication

from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from CommonLibFunctionTrigger import CommonLibFunctionTrigger
from CommonServer import CommonServer

class MeshUtilityRunner(PyFoamApplication,
                        CommonServer,
                        CommonLibFunctionTrigger):
    def __init__(self,args=None):
        description="""
Runs an OpenFoam utility that manipulates meshes.  Needs the usual 3
arguments (<solver> <directory> <case>) and passes them on (plus additional arguments).

Output is sent to stdout and a logfile inside the case directory
(PyFoamMeshUtility.logfile)

Before running it clears all timesteps but the first.

After the utility ran it moves all the data from the polyMesh-directory
of the first time-step to the constant/polyMesh-directory

ATTENTION: This utility erases quite a lot of data without asking and
should therefor be used with care
        """
        
        PyFoamApplication.__init__(self,
                                   exactNr=False,
                                   args=args,
                                   description=description)
        
    def addOptions(self):
        CommonLibFunctionTrigger.addOptions(self)
        CommonServer.addOptions(self,False)
        
    def run(self):
        cName=self.parser.casePath()

        self.checkCase(cName)
        
        sol=SolutionDirectory(cName,archive=None)

        print "Clearing out old timesteps ...."
            
        sol.clearResults()
            
        run=BasicRunner(argv=self.parser.getArgs(),
                        server=self.opts.server,
                        logname="PyFoamMeshUtility")
        
        self.addLibFunctionTrigger(run,sol)        

        self.addToCaseLog(cName,"Starting")
        
        run.start()

        sol.reread(force=True)
        
        self.addToCaseLog(cName,"Ending")

        if sol.latestDir()!=sol.initialDir():
            for f in listdir(path.join(sol.latestDir(),"polyMesh")):
                system("mv -f "+path.join(sol.latestDir(),"polyMesh",f)+" "+sol.polyMeshDir())

            print "\nClearing out new timesteps ...."
            
            sol.clearResults()
        else:
            print "\n\n  No new timestep. Utility propably failed"
