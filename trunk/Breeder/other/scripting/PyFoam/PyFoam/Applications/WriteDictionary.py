#  ICE Revision: $Id: WriteDictionary.py 9861 2009-01-05 16:22:37Z bgschaid $ 
"""
Application class that implements pyFoamWriteDictionary
"""

import sys,re

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

class WriteDictionary(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Write a value to a Foam-Dictionary.
The description of the value is word. If the value is
non-atomic (a list or a dictionary) it has to be in in Python-notation.
Parts of the expression can be accessed by using the Python-notation for accessing
sub-expressions.

Example of usage:
                            > pyFoamWriteDictionary.py --test pitzDaily/0/U "boundaryField['inlet']['type']" zeroGradient <
        """
        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <dictfile> <key> <val>",
                                   changeVersion=False,
                                   nr=3,
                                   interspersed=True)
        
    def addOptions(self):
        self.parser.add_option("--test",action="store_true",dest="test",default=False,help="Doesn't write to the file, but outputs the result on stdout")
        self.parser.add_option("--evaluate",action="store_false",dest="verbatim",default=True,help="Interpret the string as a python expression before assigning it")
        
    
    def run(self):
        fName=self.parser.getArgs()[0]
        all=self.parser.getArgs()[1]
        if all[0]=='"':
            all=all[1:]
        if all[-1]=='"':
            all=all[:-1]
        val=self.parser.getArgs()[2]

        match=re.compile("([a-zA-Z_][a-zA-Z0-9_]*)(.*)").match(all)
        if match==None:
            self.error("Expression",all,"not usable as an expression")
            
        key=match.group(1)
        sub=None
        if len(match.groups())>1:
            if match.group(2)!="":
                sub=match.group(2)

        if self.opts.verbatim:
            newValue=val
        else:
            newValue=eval(val)

        try:
            dictFile=ParsedParameterFile(fName,backup=True)
            val=dictFile[key]
        except KeyError:
            self.error("Key: ",key,"not existing in File",fName)
        except IOError,e:
            self.error("Problem with file",fName,":",e)

        if sub==None:
            dictFile[key]=newValue
        else:
            try:
                exec "dictFile[key]"+sub+"=newValue"
            except Exception,e:
                self.error("Problem with subexpression:",sys.exc_info()[0],":",e)

        if self.opts.test:
            print str(dictFile)
        else:
            dictFile.writeFile()
        