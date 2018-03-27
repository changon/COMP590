# COMP 590-80, Spring 2018 Source Code

This code is a framework for developing programming assignments / projects for COMP 590 - Special Topics on Data Compression taught at UNC, Spring 2018.

## Huffman
Refer to [BUILD.md](Huffman/BUILD.md)

## CurveFit
cd Huffman/src/
./run.sh

Change controlFile.inp to indicate the file of interest for compression. 
The overall flow is as follows:
- With some base string to indicate file of interest (from controlFile.inp), file goes from base.450p.yuv to base.residuals with compress.py (transforming data from original pixels to residual = (original - prediction) % 256). compress.py outputs the coefficients for the hypothesis/prediction function in params.out
- Then the base.residuals file is encoded (and decoded) by apps/VideoFit.java producing base-KMPcompressed.dat and base-KMPdecoded.dat. base-KMPdecoded.dat is equivalent to base.residuals
- Finally decompress.py (better named transform.py) takes the residual values and fitted coefficients (via params.out) to recover the original pixel values in base-decoded.450p.yuv. This is equivalent to base.450p.yuv

Change which entropy technique you want to use in VideoFit.java.
Add whatever hypothesis function or change the windowSize in compress.py/decompress.py
