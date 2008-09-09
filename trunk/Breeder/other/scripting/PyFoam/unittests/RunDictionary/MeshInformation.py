import unittest

from PyFoam.RunDictionary.MeshInformation import MeshInformation
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Execution.UtilityRunner import UtilityRunner

from PyFoam.Error import PyFoamException

from PyFoam.FoamInformation import oldAppConvention as oldApp

from os import path,environ,system

theSuite=unittest.TestSuite()

class MeshInformationTest(unittest.TestCase):
    def setUp(self):
        self.dest="/tmp/TestDamBreak"
        SolutionDirectory(path.join(environ["FOAM_TUTORIALS"],"interFoam","damBreak"),archive=None,paraviewLink=False).cloneCase(self.dest)

        if oldApp():
            pathSpec=[path.dirname(self.dest),path.basename(self.dest)]
        else:
            pathSpec=["-case",self.dest]
            
        run=UtilityRunner(argv=["blockMesh"]+pathSpec,silent=True,server=False)
        run.start()
        
    def tearDown(self):
        system("rm -rf "+self.dest)
    
    def testBoundaryRead(self):
        mesh=MeshInformation(self.dest)
        self.assertEqual(mesh.nrOfFaces(),9176)
        self.assertEqual(mesh.nrOfPoints(),4746)
        self.assertEqual(mesh.nrOfCells(),2268)
        try:
            self.assertEqual(mesh.nrOfCells(),2268)
        except:
            if not oldApp():
                self.fail()
                
theSuite.addTest(unittest.makeSuite(MeshInformationTest,"test"))
