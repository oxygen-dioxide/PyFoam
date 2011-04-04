#  ICE Revision: $Id:$
"""Working with a directory of timelines

Currently not optimal as it reads the files more often than necessary"""

from os import path,listdir
from glob import glob
from PyFoam.Error import error
import math

from PyFoam.Basics.SpreadsheetData import SpreadsheetData

class TimelineDirectory(object):
    """A directory of sampled times"""

    def __init__(self,case,dirName="probes",writeTime=None):
        """@param case: The case directory
        @param dirName: Name of the directory with the timelines
        @param writeTime: The write time-directory where the data in question is to be plotted"""

        self.dir=path.join(case,dirName)
        self.writeTimes=[]

        nearest=None
        
        for d in listdir(self.dir):
            if path.isdir(path.join(self.dir,d)):
                try:
                    v=float(d)
                    self.writeTimes.append(d)
                    if writeTime:
                        if nearest==None:
                            nearest=d
                        else:
                            if abs(float(writeTime)-v)<abs(float(writeTime)-float(nearest)):
                                nearest=d
                except ValueError,e:
                    pass

        self.writeTimes.sort(self.sorttimes)
        if nearest==None:
            self.usedTime=self.writeTimes[0]
        else:
            self.usedTime=nearest

        self.dir=path.join(self.dir,self.usedTime)

        self.values=[]
        self.vectors=[]
        for v in listdir(self.dir):
            self.values.append(v)
            if TimelineValue(self.dir,v,self.usedTime).isVector:
                self.vectors.append(v)
                
        self.allPositions=None
        
    def __iter__(self):
        for t in self.values:
            yield TimelineValue(self.dir,t,self.usedTime)

    def __getitem__(self,value):
        if value in self:
            return TimelineValue(self.dir,value,self.usedTime)
        else:
            raise KeyError,value

    def __contains__(self,value):
        return value in self.values
    
    def __len__(self):
        return len(self.values)

    def sorttimes(self,x,y):
        """Sort function for the solution files"""
        if(float(x)==float(y)):
            return 0
        elif float(x)<float(y):
            return -1
        else:
            return 1

    def positions(self):
        """Returns all the found positions"""

        if self.allPositions==None:
            positions=[]
            first=True
            
            for t in self:
                for v in t.positions:
                    if v not in positions:
                        if first:
                            positions.append(v)
                        else:
                            error("Found positions",t.positions,"are inconsistent with previous",positions)
                if first:
                    self.positionIndex=t.positionIndex
                first=False
            self.allPositions=positions
            
        return self.allPositions

    def timeRange(self):
        """Return the range of possible times"""
        minTime=1e80
        maxTime=-1e80

        for v in self:
            mi,ma=v.timeRange()
            minTime=min(mi,minTime)
            maxTime=max(ma,maxTime)

        return minTime,maxTime
    
    def getDataLocation(self,value=None,position=None,vectorMode=None):
        """Get Timeline sets
        @param value: name of the value. All
        if unspecified
        @param position: name of the position of the value. All
        if unspecified"""
        
        if value==None:
            value=self.values
        if position==None:
            position=self.positions()
            
        sets=[]
        
        for v in value:
            for p in position:
                fName=path.join(self.dir,v)
                if not "positionIndex" in self:
                    self.positions()
                pos=self.positionIndex[self.positions().index(p)]
                if v in self.vectors:
                    fName="< tr <%s -d '()'" %fName
                    pos=pos*3
                    if vectorMode=="x":
                        pass
                    elif vectorMode=="y":
                        pos+=1
                    elif vectorMode=="z":
                        pos+=2
                    elif vectorMode=="mag":
                        pos+=2
                        pos="(sqrt($%d*$%d+$%d*$%d+$%d*$%d))" % (pos,pos,
                                                                 pos+1,pos+1,
                                                                 pos+2,pos+2)
                    else:
                        error("Unsupported vector mode",vectorMode)
                        
                sets.append((fName,v,p,pos,TimelineValue(self.dir,v,self.usedTime)))
                
        return sets

    def getData(self,times,value=None,position=None):
        """Get data that mstches the given times most closely
        @param times: a list with times
        @param value: name of the value. All
        if unspecified
        @param position: name of the position of the value. All
        if unspecified"""
        
        if value==None:
            value=self.values
        if position==None:
            position=self.positions()
            
        sets=[]
        posIndex=[]
        for p in position:
            posIndex.append(self.positions().index(p))
            
        for v in value:
            val=TimelineValue(self.dir,v,self.usedTime)
            data=val.getData(times)
            for i,t in enumerate(times):
                used=[]
                for p in posIndex:
                    used.append(data[i][p])
                
                sets.append((v,t,used))
                
        return sets

class TimelineValue(object):
    """A file with one timelined value"""

    def __init__(self,sDir,val,time):
        """@param sDir: The timeline-dir
        @param val: the value
        @param time: the timename"""

        self.val=val
        self.time=time
        self.file=path.join(sDir,val)
        poses=[]

        self.isVector=False
        
        data=open(self.file)
        l1=data.readline()
        if len(l1)<1 or l1[0]!='#':
            error("Data file",self.file,"has no description of the fields")
        l2=data.readline()

        self._isProbe=True
        if l2[0]!='#':
            # Not a probe-file. The whole description is in the first line
            poses=l1[1:].split()[1:]
            firstData=l2
            self._isProbe=False
        else:
            # probe-file so we need one more line
            l3=data.readline()
            x=l1[1:].split()[1:]
            y=l2[1:].split()[1:]
            z=l3[1:].split()[1:]
            for i in range(len(x)):
                poses.append("(%s %s %s)" % (x[i],y[i],z[i]))
            data.readline()
            firstData=data.readline()
                
        self.positions=[]
        self.positionIndex=[]
        if len(poses)+1==len(firstData.split()):
            #scalar
            for i,v in enumerate(firstData.split()[1:]):
                if abs(float(v))<1e40:
                    self.positions.append(poses[i])
                    self.positionIndex.append(i)
        else:
            self.isVector=True
            for i,v in enumerate(firstData.split()[2::3]):
                if abs(float(v))<1e40:
                    self.positions.append(poses[i])
                    self.positionIndex.append(i)

        self.cache={}

    def __repr__(self):
        if self.isVector:
            vect=" (vector)"
        else:
            vect=""
            
        return "TimelineData of %s%s on %s at t=%s " % (self.val,vect,str(self.positions),self.time)

    def isProbe(self):
        """Is this a probe-file"""
        return self._isProbe

    def timeRange(self):
        """Range of times"""
        lines=open(self.file).readlines()
        for l in lines:
            v=l.split()
            if v[0][0]!='#':
                minRange=float(v[0])
                break
        lines.reverse()
        for l in lines:
            v=l.split()
            if len(v)>=len(self.positions)+1:
                maxRange=float(v[0])
                break

        return minRange,maxRange
    
    def getData(self,times):
        """Get the data values that are nearest to the actual times"""
        dist=len(times)*[1e80]
        data=len(times)*[len(self.positions)*[1e80]]
        
        lines=open(self.file).readlines()
        
        for l in lines:
            v=l.split()
            if v[0][0]!='#':
                try:
                    time=float(v[0])
                    vals=v[1:]
                    for i,t in enumerate(times):
                        if abs(t-time)<dist[i]:
                            dist[i]=abs(t-time)
                            data[i]=vals
                except ValueError:
                    pass
        result=[]
        for d in data:
            tmp=[]
            for v in d:
                if abs(float(v))<1e40:
                    tmp.append(float(v))
            result.append(tmp)

        return result

    def __call__(self):
        """Return the data as a SpreadsheetData-object"""
        
        lines=open(self.file).readlines()
        data=[]
        for l in lines:
            v=l.split()
            if v[0][0]!='#':
                data.append(map(lambda x:float(x.replace('(','').replace(')','')),v))
        names=["time"]
        if self.isVector:
            for p in self.positions:
                names+=[p+" x",p+" y",p+" z"]
        else:
            names+=self.positions

        return SpreadsheetData(data=data,
                               names=names,
                               title="%s_t=%s" % (self.val,self.time))
