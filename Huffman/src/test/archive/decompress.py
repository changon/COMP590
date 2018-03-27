# take kmp huffman decoded file (residuals and transform to original video)
import struct

def lin_combo(x, b0, b1, b2):
	return b0+b1*x[0]+b2*x[1]

base = ""
controlDir = "/Users/Raphael/source/COMP590/code_base/comp590sp18/Huffman/src/"
with open(controlDir+"controlFile.inp", "r") as controlF:
        base = controlF.readline().replace('\n','')

weights = []
with open(controlDir+"params.out", "r") as paramF:
	params = paramF.readlines()
for strVal in params:
	strVal = strVal.replace('\n','')
	weights.append(float(strVal))

# fileName="/Users/kmp/tmp/" + base + ".450p.yuv"
#ofileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + "Truncated-decoded.450p.yuv"
ofileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + "-decoded.450p.yuv"
#ifileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + ".residuals"
ifileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + "-KMPdecoded.dat"
#fileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + ".450p.yuv";
ofile = open(ofileName, 'wb')
ifile = open(ifileName, 'rb')

# read in coefficients
#weights = [ 4.01811148, -0.27018482,  1.23870014] # for 3 frames
#weights = [ 3.79699158, -0.28099678, 1.25129243]

windowSize = 2
num_frames=150
height = 450
width = 800

#verify that we get back original with this formula
pixelCount = 0
for frameNumber in range(0, num_frames):
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
			prediction = lin_combo(xPixels, weights[0], weights[1], weights[2])
			residual = ifile.read(1)
			residual = struct.unpack('B', residual)[0]
			#residual = reses[pixelCount]
			original = (residual + int(prediction)) % 256
			rowOfPixels.append(original)
			#print(original-yval[pixelCount])
			byteOut = struct.pack("=B", original)
			ofile.write(byteOut)
			pixelCount += 1
ifile.close()
ofile.close()
