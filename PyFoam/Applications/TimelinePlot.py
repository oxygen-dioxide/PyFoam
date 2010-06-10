#  ICE Revision: $Id: TimelinePlot.py 11144 2009-12-22 10:10:52Z bgschaid $ 
"""
Application class that implements pyFoamTimelinePlot.py
"""

import sys,string
from os import path
from optparse import OptionGroup

from PyFoamApplication import PyFoamApplication
from PyFoam.RunDictionary.TimelineDirectory import TimelineDirectory

from PyFoam.Error import error,warning

from PlotHelpers import cleanFilename

class TimelinePlot(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Searches a directory for timelines that were generated by some functionObject
and generates the commands to gnuplot it
        """
        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <casedir>",
                                   nr=1,
                                   changeVersion=False,
                                   interspersed=True)
        
    def addOptions(self):
        data=OptionGroup(self.parser,
                          "Data",
                          "Select the data to plot")
        self.parser.add_option_group(data)
        
        data.add_option("--values",
                        action="append",
                        default=None,
                        dest="values",
                        help="The values for which timelines should be plotted. All if unset")
        data.add_option("--positions",
                        action="append",
                        default=None,
                        dest="positions",
                        help="The positions for which timelines should be plotted. Either strings or integers (then the corresponding column number will be used). All if unset")
        data.add_option("--write-time",
                        default=None,
                        dest="writeTime",
                        help="If more than one time-subdirectory is stored select which one is used")
        data.add_option("--directory-name",
                        action="store",
                        default="probes",
                        dest="dirName",
                        help="Alternate name for the directory with the samples (Default: %default)")
        
        time=OptionGroup(self.parser,
                         "Time",
                         "Select the times to plot")
        self.parser.add_option_group(time)
        
        time.add_option("--time",
                        action="append",
                        type="float",
                        default=None,
                        dest="time",
                        help="The times that are plotted (can be used more than once). Has to be specified for bars")
        time.add_option("--min-time",
                        action="store",
                        type="float",
                        default=None,
                        dest="minTime",
                        help="The smallest time that should be used for lines")
        time.add_option("--max-time",
                        action="store",
                        type="float",
                        default=None,
                        dest="maxTime",
                        help="The biggest time that should be used for lines")


        plot=OptionGroup(self.parser,
                           "Plot",
                           "How data should be plotted")
        self.parser.add_option_group(plot)

        plot.add_option("--basic-mode",
                        type="choice",
                        dest="basicMode",
                        default=None,
                        choices=["bars","lines"],
                        help="Whether 'bars' of the values at selected times or 'lines' over the whole timelines should be plotted")
        plot.add_option("--collect-lines-by",
                        type="choice",
                        dest="collectLines",
                        default="values",
                        choices=["values","positions"],
                        help="Collect lines for lineplotting either by 'values' or 'positions'. Default: %default")

        output=OptionGroup(self.parser,
                           "Output",
                           "Where data should be plotted to")
        self.parser.add_option_group(output)
        
        output.add_option("--gnuplot-file",
                          action="store",
                          dest="gnuplotFile",
                          default=None,
                          help="Write the necessary gnuplot commands to this file. Else they are written to the standard output")
        output.add_option("--picture-destination",
                          action="store",
                          dest="pictureDest",
                          default=None,
                          help="Directory the pictures should be stored to")
        output.add_option("--name-prefix",
                          action="store",
                          dest="namePrefix",
                          default=None,
                          help="Prefix to the picture-name")
        output.add_option("--clean-filename",
                          action="store_true",
                          dest="cleanFilename",
                          default=False,
                          help="Clean filenames so that they can be used in HTML or Latex-documents")
        
        data.add_option("--info",
                        action="store_true",
                        dest="info",
                        default=False,
                        help="Print info about the sampled data and exit")

    def setFile(self,fName):
        if self.opts.namePrefix:
            fName=self.opts.namePrefix+"_"+fName
        if self.opts.pictureDest:
            fName=path.join(self.opts.pictureDest,fName)

        name=fName
        if self.opts.cleanFilename:
            name=cleanFilename(fName)
        return 'set output "%s"\n' % name
        
    def run(self):
        timelines=TimelineDirectory(self.parser.getArgs()[0],dirName=self.opts.dirName,writeTime=self.opts.writeTime)
        
        if self.opts.info:
            print "Write Times    : ",timelines.writeTimes
            print "Used Time      : ",timelines.usedTime
            print "Values         : ",timelines.values
            print "Positions      : ",timelines.positions()
            print "Time range     : ",timelines.timeRange()
            sys.exit(0)

        if self.opts.values==None:
            self.opts.values=timelines.values
        else:
            for v in self.opts.values:
                if v not in timelines.values:
                    self.error("The requested value",v,"not in possible values",timelines.values)
        if self.opts.positions==None:
            self.opts.positions=timelines.positions()
        else:
            pos=self.opts.positions
            self.opts.positions=[]
            for p in pos:
                try:
                    p=int(p)
                    if p<0 or p>=len(timelines.positions()):
                        self.error("Time index",p,"out of range for positons",timelines.positions())
                    else:
                        self.opts.positions.append(timelines.positions()[p])
                except ValueError:
                    if p not in timelines.positions():
                        self.error("Position",p,"not in",timelines.positions())
                    else:
                        self.opts.positions.append(p)
                        
        result="set term png nocrop enhanced \n"
        
        if self.opts.basicMode==None:
            self.error("No mode selected. Do so with '--basic-mode'")
        elif self.opts.basicMode=='bars':
            if self.opts.time==None:
                self.error("No times specified for bar-plots")
            self.opts.time.sort()
            minTime,maxTime=timelines.timeRange()
            usedTimes=[]
            hasMin=False
            for t in self.opts.time:
                if t<minTime:
                    if not hasMin:
                        usedTimes.append(minTime)
                        hasMin=True
                elif t>maxTime:
                    usedTimes.append(maxTime)
                    break
                else:
                    usedTimes.append(t)
            data=timelines.getData(usedTimes,
                                   value=self.opts.values,
                                   position=self.opts.positions)
            #            print data
            result+="set style data histogram\n"
            result+="set style histogram cluster gap 1\n"
            result+="set style fill solid border -1\n"
            result+="set boxwidth 0.9\n"
            result+="set xtics border in scale 1,0.5 nomirror rotate by 90  offset character 0, 0, 0\n"
            # set xtic rotate by -45\n"
            result+="set xtics ("
            for i,p in enumerate(self.opts.positions):
                if i>0:
                    result+=" , "
                result+='"%s" %d' % (p,i)
            result+=")\n"
            for tm in usedTimes:
                if abs(float(tm))>1e20:
                    continue
                result+=self.setFile("%s_writeTime_%s_Time_%s.png"  % (self.opts.dirName,timelines.usedTime,tm))
                result+='set title "Directory: %s WriteTime: %s Time: %s"\n' % (self.opts.dirName,timelines.usedTime,tm)
                result+= "plot "
                first=True
                for val in self.opts.values:
                    if first:
                        first=False
                    else:
                        result+=", "
                    result+='"-" title "%s" ' % val 
                result+="\n"
                for v,t,vals in data:
                    if t==tm:
                        for v in vals:
                            result+="%g\n" % v
                        result+="e\n"
        elif self.opts.basicMode=='lines':
            #            print self.opts.positions
            plots=timelines.getDataLocation(value=self.opts.values,
                                            position=self.opts.positions)
            #            print plots
            minTime,maxTime=timelines.timeRange()
            if self.opts.minTime:
                minTime=self.opts.minTime
            if self.opts.maxTime:
                maxTime=self.opts.maxTime
            result+= "set xrange [%g:%g]\n" % (minTime,maxTime)
            if self.opts.collectLines=="values":
                for val in self.opts.values:
                    result+=self.setFile("%s_writeTime_%s_Value_%s.png"  % (self.opts.dirName,timelines.usedTime,val))
                    result+='set title "Directory: %s WriteTime: %s Value: %s"\n' % (self.opts.dirName,timelines.usedTime,val)
                    result+= "plot "
                    first=True
                    for f,v,p,i in plots:
                        if v==val:
                            if first:
                                first=False
                            else:
                                result+=" , "
                            result+= ' "%s" using 1:%d title "%s" with lines ' % (f,i+2,p)
                    result+="\n"
            elif self.opts.collectLines=="positions":
                for pos in self.opts.positions:
                    result+=self.setFile("%s_writeTime_%s_Position_%s.png"  % (self.opts.dirName,timelines.usedTime,pos))
                    result+='set title "Directory: %s WriteTime: %s Position: %s"\n' % (self.opts.dirName,timelines.usedTime,pos)
                    result+= "plot "
                    first=True
                    for f,v,p,i in plots:
                        if p==pos:
                            if first:
                                first=False
                            else:
                                result+=" , "
                            result+= ' "%s" using 1:%d title "%s" with lines ' % (f,i+2,v)
                    result+="\n"
                
            else:
                self.error("Unimplemented collection of lines:",self.opts.collectLines)
        else:
            self.error("Not implemented basicMode",self.opts.basicMode)
        
        dest=sys.stdout
        if self.opts.gnuplotFile:
            dest=open(self.opts.gnuplotFile,"w")
            
        dest.write(result)