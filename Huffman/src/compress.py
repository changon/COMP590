# work off of byte values here

import random
import struct # for byte -> unsigned 8 bit
import numpy as np
from scipy.optimize import curve_fit

def linear_fx(x, b0, b1):
	return b0 + b1*x

def lin_combo(x, b0, b1, b2): # generalize based on window size
	return b0+b1*x[0]+b2*x[1]

# going through particular fits, call method via string name. dictionary method!
# https://stackoverflow.com/questions/7936572/python-call-a-function-from-string-name

#x = np.array([1,2,3,4])
#y = np.array([1,2,3,4])

#params = curve_fit(linear_fx, x, y)
#print(params[0])

################################# real program ##################

## encode. read in data into here by bytes, formulate data set (x and y values), train params.

xval = []
yval = []

windowSize=2

width = 800
height = 450
num_frames = 150

print("curve fitting")

base = ""

# read in base
controlDir = "/Users/Raphael/source/COMP590/code_base/comp590sp18/Huffman/src/"
with open(controlDir+"controlFile.inp", 'r') as controlF:
	base = controlF.readline().replace('\n','')

# fileName="/Users/kmp/tmp/" + base + ".450p.yuv"
#fileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + "Truncated" + ".450p.yuv";
fileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + ".450p.yuv";

ifile = open(fileName, 'rb')

# read in data/formulate training data
frames = []
for frameNumber in range(0, num_frames):
	frame = []
	for y_i in range(0, height):
		rowOfPixels = []
		xPixels = []
		for x_i in range(0, width):
			# get past windowSize values
			if x_i > windowSize:
				for i in range(1, windowSize+1):
					xPixels.append(rowOfPixels[x_i-i])
			elif x_i <= windowSize: #0,1...windowSize-1
				for i in range(1, windowSize+1):
					if i < x_i: # o.w. we go futher than we have pixels
						xPixels.append(rowOfPixels[x_i-i])
					else:
						xPixels.append(0)
			xPixels.reverse()
			xval.append(np.array(xPixels)) # add training data x			
			xPixels=[] # reset pixels
			byteValue = ifile.read(1)
		# conver to 8 bit unsigned here
			byteValue = struct.unpack('B', byteValue)[0]
			rowOfPixels.append(byteValue)
			yval.append(rowOfPixels[x_i]) # add training data y
		frame.append(rowOfPixels)
	frames.append(frame)

ifile.close()

# automation with hypothesis and windowSize? build function writer

## converts to long list? extends out the pairs in each slot? why?
#xs = np.array(xval) # np.array xPixels (each elt. of xval)
x1s =[]
x2s = []
for i in range(0, len(xval)):
	x1s.append(xval[i][0])
	x2s.append(xval[i][1])

x1s = np.array(x1s)
x2s = np.array(x2s)
ys = np.array(yval)
p0 = random.uniform(0,5), random.uniform(0,5), random.uniform(0,5)
p0 = 1,1,1
params = curve_fit(lin_combo, (x1s, x2s), ys, p0)
print(params[0])

## rewrite data as residuals from curve guess and get prob model from that in java program. store coefficients in java program memory. argument for function fit type?
# go through each and write residuals via unsigned 8 bit.

print("writing residuals")

outFilename = "/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + ".residuals"
#outFile = open(outFilename, 'w')
outFile = open(outFilename, 'wb')

reses = []
pixelCount = 0
for frameNumber in range(0, num_frames):
	for y_i in range(0, height):
		for x_i in range(0, width):
			prediction = lin_combo((x1s[pixelCount], x2s[pixelCount]), params[0][0], params[0][1], params[0][2])
			residual = (ys[pixelCount] - int(prediction))
			residual = residual % 256
			reses.append(residual)
			byteVal = struct.pack("=B", residual)
			outFile.write(byteVal)
			pixelCount += 1
			#outFile.write(str(residual))
outFile.close()

paramOutFile = controlDir + "params.out"
paramf = open(paramOutFile, 'w')
for p in range(0, params[0].size):
	outPstr = str(params[0][p])
	if p < params[0].size-1:
		outPstr += "\n"
	paramf.write(outPstr)
paramf.close()

######################## DECODING test ################
#
## fileName="/Users/kmp/tmp/" + base + ".450p.yuv"
#ofileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + "Truncated-decoded.450p.yuv"
#ifileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + ".residuals"
##fileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + ".450p.yuv";
#ofile = open(ofileName, 'wb')
#ifile = open(ifileName, 'rb')
#
##verify that we get back original with this formula
#pixelCount = 0
#for frameNumber in range(0, num_frames):
#	for y_i in range(0, height):
#		for x_i in range(0, width):
#			prediction = lin_combo(xval[pixelCount], params[0][0],params[0][1],params[0][2])
#			residual = ifile.read(1)
#			residual = struct.unpack('B', residual)[0]
#			#residual = reses[pixelCount]
#			original = (residual + int(prediction)) % 256
#			print(original-yval[pixelCount])	
#			byteOut = struct.pack("=B", original)
#			ofile.write(byteOut)
#			pixelCount += 1
#ifile.close()
#ofile.close()
#
# https://stackoverflow.com/questions/10133194/reverse-modulus-operator
			# get back by x = (residual + int(prediction)) mod 256
			#print(residual)
			#print(type(residual))
 
## decode. use params to guess next data point, add residual to guess and that is our new pixel. write it out.


## curve fit across all frames or one frame at a time?
