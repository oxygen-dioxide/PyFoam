#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/FromTemplate.py 8448 2013-09-24T17:55:25.403256Z bgschaid  $
"""
Application class that implements pyFoamFromTemplate
"""

import sys

from optparse import OptionGroup

from .PyFoamApplication import PyFoamApplication

from PyFoam.Basics.TemplateFile import TemplateFile,TemplateFileOldFormat
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from .CommonPickledDataInput import CommonPickledDataInput
from .CommonTemplateFormat import CommonTemplateFormat
from .CommonTemplateBehaviour import CommonTemplateBehaviour

from PyFoam.ThirdParty.six import print_,iteritems

from os import path

class FromTemplate(PyFoamApplication,
                   CommonPickledDataInput,
                   CommonTemplateBehaviour,
                   CommonTemplateFormat):
    def __init__(self,
                 args=None,
                 parameters={},
                 **kwargs):
        description="""\
Generates a file from a template file. Usually the name of the
template file is the name of the file with the extension '.template'
(unless specified otherwise). The file is generated by replacing
everything in the template file that is enclosed by $ $ with
calculated expression. values are given in a Python-dictionary. Lines
in the template file that start with $$ are used as definitons for
intermediate expressions.

This format is used if the two arguments are used.  If the template
file and the data is specified via options then a more advanced
template format that allows branches and loops is used via the
template-engine pyratemp (see
http://www.simple-is-better.org/template/pyratemp.html). If data is
read from a pickled-input then it looks for the keys "template" and "values" and
uses these.

In the new format expressions are delimited by |- at the start and -|
at the end. These defaults can be changed

@param parameters: Dictionary with parameters (only usable
when called from a script)
        """

        self.parameters=parameters.copy()

        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] (<file> <vals>|)",
                                   nr=0,
                                   changeVersion=False,
                                   interspersed=True,
                                   exactNr=False,
                                   **kwargs)

    def addOptions(self):
        CommonPickledDataInput.addOptions(self)

        inputs=OptionGroup(self.parser,
                           "Inputs",
                           "Inputs for the templating process")
        self.parser.add_option_group(inputs)

        inputs.add_option("--template-file",
                          action="store",
                          default=None,
                          dest="template",
                          help="Name of the template file. Also overwrites the standard for the old format (<filename>.template). If this is set to 'stdin' then the template is read from the standard-input to allow using the pipe into it.")
        inputs.add_option("--values-string",
                          action="store",
                          default=None,
                          dest="values",
                          help="String with the values that are to be inserted into the template as a dictionaty in Python-format. If specified this is the first choice")
        inputs.add_option("--values-dictionary",
                          action="store",
                          default=None,
                          dest="valuesDict",
                          help="Name of a dictionary-file in OpenFOAM-format. If this is unspecified too then values are taken from the pickled-input")
        inputs.add_option("--no-defaults-file",
                          action="store_false",
                          default=True,
                          dest="useDefaults",
                          help="If a file with the same name as the template file but the extension '.defaults' is found then it is loaded before the other values are read. This option switches this off")

        outputs=OptionGroup(self.parser,
                           "Outputs",
                           "Outputs of the templating process")
        self.parser.add_option_group(outputs)
        outputs.add_option("--stdout",
                           action="store_true",
                           dest="stdout",
                           default=False,
                           help="Doesn't write to the file, but outputs the result on stdout")
        outputs.add_option("--dump-used-values",
                           action="store_true",
                           dest="dumpUsed",
                           default=False,
                           help="Print the used parameters")
        outputs.add_option("--output-file",
                           action="store",
                           default=None,
                           dest="outputFile",
                           help="File to which the output will be written. Only for the new format")

        CommonTemplateFormat.addOptions(self)

        CommonTemplateBehaviour.addOptions(self)

    def run(self):
        if self.opts.template=="stdin" and self.opts.pickledFileRead=="stdin":
            self.error("Can't simultanously read pickled data and the tempalte from the standard input")

        content=None
        if self.opts.template=="stdin":
            content=sys.stdin.read()
        data=None
        if self.opts.pickledFileRead:
            data=self.readPickledData()
        fName=None

        if len(self.parser.getArgs())==2:
            if self.opts.pickledFileRead:
                self.error("old-format mode does not work with pickled input")
            if self.opts.outputFile:
                self.error("--output-file is not valid for the old format")
            # old school implementation
            fName=self.parser.getArgs()[0]
            vals=eval(self.parser.getArgs()[1])
            if type(vals)==str:
                # fix a problem with certain shells
                vals=eval(vals)

            if self.opts.template==None:
                template=fName+".template"
            else:
                template=self.opts.template

            if content:
                t=TemplateFileOldFormat(content=content)
            else:
                t=TemplateFileOldFormat(name=template)
        elif len(self.parser.getArgs())==0:
            if self.opts.template==None and self.opts.outputFile!=None  and self.opts.outputFile!="stdin":
                self.opts.template=self.opts.outputFile+".template"
                self.warning("Automatically setting template to",self.opts.template)
            vals={}
            if self.opts.useDefaults and self.opts.template!=None and self.opts.template!="stdin":
                name,ext=path.splitext(self.opts.template)
                defaultName=name+".defaults"
                if path.exists(defaultName):
                    self.warning("Reading default values from",defaultName)
                    vals=ParsedParameterFile(defaultName,
                                             noHeader=True,
                                             doMacroExpansion=True).getValueDict()

            vals.update(self.parameters)

            if self.opts.values:
                vals.update(eval(self.opts.values))
            elif self.opts.valuesDict:
                vals.update(ParsedParameterFile(self.opts.valuesDict,
                                                noHeader=True,
                                                doMacroExpansion=True).getValueDict())
            elif data:
                vals.update(data["values"])
            elif len(self.parameters)==0:
                self.error("Either specify the values with --values-string or --values-dictionary or in the pickled input data")

            if self.opts.dumpUsed:
                maxLen=max([len(k) for k in vals.keys()])
                formatString=" %%%ds | %%s" % maxLen
                print_("Used values")
                print_(formatString % ("Name","Value"))
                print_("-"*(maxLen+30))
                for k,v in iteritems(vals):
                    print_(formatString % (k,v))

            if content:
                t=TemplateFile(content=content,
                               tolerantRender=self.opts.tolerantRender,
                               allowExec=self.opts.allowExec,
                               expressionDelimiter=self.opts.expressionDelimiter,
                               assignmentLineStart=self.opts.assignmentLineStart)
            elif data:
                t=TemplateFile(content=data["template"],
                               tolerantRender=self.opts.tolerantRender,
                               allowExec=self.opts.allowExec,
                               expressionDelimiter=self.opts.expressionDelimiter,
                               assignmentLineStart=self.opts.assignmentLineStart)
            elif self.opts.template:
                t=TemplateFile(name=self.opts.template,
                               tolerantRender=self.opts.tolerantRender,
                               allowExec=self.opts.allowExec,
                               expressionDelimiter=self.opts.expressionDelimiter,
                               assignmentLineStart=self.opts.assignmentLineStart)
            else:
                self.error("Template unspecified")

            if self.opts.outputFile:
                fName=self.opts.outputFile
        else:
            self.error("Either specify 2 arguments (file and values) for old format or no arguments for the new format")

        if self.opts.stdout:
            print_(t.getString(vals))
        elif fName:
            try:
                t.writeToFile(fName,vals)
            except (NameError,SyntaxError):
                e = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
                print_("While processing file",fName)
                raise e
        else:
            self.error("No destination for the output specified")

# Should work with Python3 and Python2
