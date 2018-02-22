import numpy as np
import matplotlib.pyplot as plt
import pcl
import sys
import os.path as path
import argparse


### TODO
# implement command line args!
#inputfile = "test2.csv"     # the input test data

parser = argparse.ArgumentParser(description='Generate Pointclouds out of VR-3000 csv data')
parser.add_argument('--infile', type=argparse.FileType('r', encoding='ISO-8859-1'), 
                      required=True, dest="infile")
parser.add_argument('--outfile', 
                      required=True, dest="outfile")
parser.add_argument('--outdir', 
                      required=False, dest="outdir")
args = parser.parse_args()
inputfile = args.infile
outputfile = args.outfile
outputdir = "."
if (args.outdir):
    print("bla",args.outdir)
    outputdir = args.outdir
print("input file: {}".format(inputfile))
print("output file: {}".format(outputfile))
headerLines = 22
resolutionX = 24
resolutionY = 18
matrix = []                 # the complete scan as a matrix

with inputfile as fin:
    for _ in range(headerLines):
        next(fin)
    for line in fin:        # iterate over every line in the file
        tmpElementsPerLine = []     # this is a temporary array used to store all the actual data (per line)
        for element in line.strip().split(";"):     # every data point in the file looks like this value,value
                                                    # only the first element ist needed
            if element == '':                       # if there is no data, add a zero
                tmpElementsPerLine.append(0)
            else:
                try:        # try to extract the first value per data point and convert it to a float
                    tmpElementsPerLine.append(float(element.split(",")[0]))
                except:
                    print("could not convert element to float, skipping")
                    tmpElementsPerLine.append(0)
        matrix.append(tmpElementsPerLine)
matrix = np.array(matrix)
print("read in {} lines with {} pixels".format(len(matrix), len(matrix[0,:])))
# scaling  
     
pointCloud = []     #  the actual point cloud, containing only valid coordinates
for row in range(len(matrix)):     # the x coordinate cooresponds to the row position
    for col in range(len(matrix[row,:])):      # the y coordinate corresponds to the col position
        if matrix[row,col] != 0:        # skip all zero values
            # here scaling
            pointCloud.append([(float(row)/1024)*resolutionX, (float(col)/768)*resolutionY, matrix[row,col]/1000])  # append the coordinates in the pointCloud list
pointCloud = np.array(pointCloud, dtype=np.float32)
# done! all relevant coordinates are now stored in the pointCloud list
print("overall point cloud has {} elements".format(len(pointCloud)))
pclCloud = pcl.PointCloud(pointCloud)
pcl.save(pclCloud, path.join(outputdir, outputfile))





