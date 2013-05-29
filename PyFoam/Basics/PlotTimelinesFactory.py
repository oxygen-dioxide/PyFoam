#  ICE Revision: $Id: PlotTimelinesFactory.py 12747 2013-01-03 23:06:57Z bgschaid $
"""Creates subclasses of GeneralPlotTimelines"""

from PyFoam.Basics.GnuplotTimelines import GnuplotTimelines
from PyFoam.Basics.MatplotlibTimelines import MatplotlibTimelines
from PyFoam.Basics.QwtPlotTimelines import QwtPlotTimelines
from PyFoam.Basics.DummyPlotTimelines import DummyPlotTimelines

from .CustomPlotInfo import CustomPlotInfo


from PyFoam import configuration
from PyFoam.Error import error

lookupTable = { "gnuplot" : GnuplotTimelines ,
                "matplotlib" : MatplotlibTimelines,
                "qwtplot" : QwtPlotTimelines,
                "dummy" : DummyPlotTimelines  }

def createPlotTimelines(timelines,
                        custom,
                        implementation=None,
                        showWindow=True,
                        registry=None):
    """Creates a plotting object
    @param timelines: The timelines object
    @type timelines: TimeLineCollection
    @param custom: specifies how the block should look like
    @param implementation: the implementation that should be used
    """
    if implementation==None:
        implementation=configuration().get("Plotting","preferredImplementation")

    if implementation not in lookupTable:
        error("Requested plotting implementation",implementation,
              "not in list of available implementations",list(lookupTable.keys()))

    return lookupTable[implementation](timelines,
                                       custom,
                                       showWindow=showWindow,
                                       registry=registry)

def createPlotTimelinesDirect(name,
                              timelines,
                              persist=None,
                              raiseit=True,
                              with_="lines",
                              alternateAxis=[],
                              forbidden=[],
                              start=None,
                              end=None,
                              logscale=False,
                              ylabel=None,
                              y2label=None,
                              implementation=None):
    """Creates a plot using some prefefined values
    @param timelines: The timelines object
    @type timelines: TimeLineCollection
    @param persist: Gnuplot window persistst after run
    @param raiseit: Raise the window at every plot
    @param with_: how to plot the data (lines, points, steps)
    @param alternateAxis: list with names that ought to appear on the alternate y-axis
    @param forbidden: A list with strings. If one of those strings is found in a name, it is not plotted
    @param start: First time that should be plotted. If undefined everything from the start is plotted
    @param end: Last time that should be plotted. If undefined data is plotted indefinitly
    @param logscale: Scale the y-axis logarithmic
    @param ylabel: Label of the y-axis
    @param y2label: Label of the alternate y-axis
    @param implementation: the implementation that should be used
    """

    ci=CustomPlotInfo(name=name)
    ci.persist=persist
    ci.raiseit=raiseit
    ci.with_=with_
    ci.alternateAxis=alternateAxis
    ci.forbidden=forbidden
    ci.start=start
    ci.end=end
    ci.logscale=logscale
    ci.ylabel=ylabel
    ci.y2label=y2label

    return createPlotTimelines(timelines,ci,implementation=implementation)

# Should work with Python3 and Python2
