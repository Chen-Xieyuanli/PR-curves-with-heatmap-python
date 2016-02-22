from findDirsOfInterest import *
import re

import matplotlib.pyplot as plt
import numpy as np
import scipy
from sklearn import metrics
def calcAuc(detectionPaths,groundtruthPath):

    for detections in detectionPaths:
        #print("Finding AUC for detection %s in %s" % (detections,groundtruthPath))

        lineSplitsAllVars = detections.split("-")
        modelDsSplit = lineSplitsAllVars[0]
        modelDs = re.findall(r'\d+',modelDsSplit)
        modelDsX = modelDs[0]
        modelDsY = modelDs[1]
        print "ModelDsX: %s ModelDsY: %s\n" % (modelDsX,modelDsY)
        plotName = "mDs[%s,%s]" % (str(modelDsX),str(modelDsY))
        #plotName = "test"
        #executionString = "python calcPrRc.py -gt " + groundtruthPath + " -d " + detections + " -p 0.5 -o -ptf " + plotName + " -c detector"
        executionString = "python calcprcTL.py -gt " + groundtruthPath + " -d " + detections + " -p 0.5 -o -ptf " + plotName + " -c detector"

        print executionString
        os.system(str(executionString))

def findAllAucResultFiles():
    files = []
    for dirname, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if( "results" in filename and "detector-mDs[" in filename and "Bin" not in dirname ):

                thisFile = os.path.join(dirname, filename)
                print thisFile
                files.append(thisFile)
    return files

def generateCombinedAucFile():
    aucFiles = findAllAucResultFiles()

    outputFile = open("combinedAUC.csv", 'w')
    outputFile.write("ModelDsX;ModelDsY;AUC\n") # CSV header
    #writer = csv.writer(outputFile, delimiter=";",lineterminator="\n")

    for aucFile in aucFiles:
        f = open(aucFile, 'r')

        aucLines = f.readlines()
        for aucLine in aucLines:
            if("AUC" in aucLine):
                modelDs = re.findall(r'\d+',aucFile)
                modelDsX = modelDs[0]
                modelDsY = modelDs[1]

                aucFound = re.findall(r'\d+',aucLine)

                outLine = "%s;%s;%s.%s\n" % (modelDsX,modelDsY,aucFound[0],aucFound[1])
                outputFile.write(outLine)
    outputFile.close()

def genereateHeatMap():
    inputFile = open("combinedAUC.csv", 'r')
    data = np.zeros((26,26))
    header = inputFile.readline()
    for line in inputFile:
        lineSplit = line.split(";")
        modelDsX = int(lineSplit[0])
        modelDsY = int(lineSplit[1])
        foundAUC = float(lineSplit[2])
        print "modelDsX: %s modelDsY: %s AUC: %s" % (modelDsX,modelDsY,foundAUC)
        data[ (modelDsY) , (modelDsX) ] = foundAUC

    #data = np.random.rand(4, 4)
    fig, ax = plt.subplots()
    # http://matplotlib.org/examples/color/colormaps_reference.html
    heatmap = ax.pcolor(data, cmap=plt.cm.jet)
    #heatmap = ax.pcolor(data, cmap=plt.cm.Blues)
    minXVal = 999
    maxXVal = 0
    minYVal = 999
    maxYVal = 0

    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            if (data[y,x]>0.0):
                plt.text(x + 0.5, y + 0.5, '%.2f%%' % data[y,x],
                 horizontalalignment='center',
                 verticalalignment='center',
                 )
                if( minXVal > x):
                    minXVal = x
                if( minYVal > y ):
                    minYVal = y
                if( maxXVal < x):
                    maxXVal = x
                if( maxYVal < y ):
                    maxYVal = y

    column_labels = list(range(0, maxXVal+1))
    row_labels = list(range(0, maxYVal+1))


    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)

    # want a more natural, table-like display
    #ax.invert_yaxis()
    #ax.xaxis.tick_top()

    ax.set_xticklabels(column_labels, minor=False)
    ax.set_yticklabels(row_labels, minor=False)
    plt.colorbar(heatmap)
    plt.ylim([minYVal, maxYVal+1])
    plt.xlim([minXVal, maxXVal+1])
    fig.set_size_inches(18.5, 10.5)
    plt.xlabel('Model Dimension X-Size',fontsize=18)
    plt.ylabel('Model Dimension Y-Size',fontsize=18)
    plt.title('Area-Under-Curve Heatmap of Varying Model Dimensions for ACF Detector',fontsize=24)
    plt.savefig("heatMapPlot.png", dpi=300)
    plt.show()

def main():
    detectionPaths = findDirsOfInterest()
    groundtruthPath = "annotations/nightSeq1/frameAnnotationsBULB.csv"
    calcAuc(detectionPaths,groundtruthPath)
    generateCombinedAucFile()
    genereateHeatMap()


if __name__ == "__main__":
    main()
