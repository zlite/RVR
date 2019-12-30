# RVR demo with Intel Realsense 415 depth sensor


# First import the library	
import pyrealsense2 as rs	
import time	
import sys	
import os	
import asyncio	

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))	

from sphero_sdk import SerialAsyncDal	
from sphero_sdk import SpheroRvrAsync	
from sphero_sdk.common.enums.drive_enums import DriveFlagsBitmask	

ROIx1 = 0
ROIx2 = 640
ROIy1 = 240
ROIy2 = 300
yrange = ROIy2-ROIy1
xrange = ROIx2-ROIx1
xincrement = 5
binsize = 10
bins = round(xrange/(binsize * xincrement)) # should be 13 bins in this case
epoch = 0
scan = [[],[]]
xstack = []
xbins = []
xbinsold = []
speed = 64 # Valid speed values are 0-255	
heading = 10 # Valid heading values are 0-359	
reverse = False


loop = asyncio.get_event_loop()	scan = [[],[]]
rvr = SpheroRvrAsync(	xstack = []
    dal=SerialAsyncDal(	xbins = []
        loop	xbinsold = []
    )	
)	

def setup():
    global scan, xstack, xbins, xbinsold
    await rvr.wake()	
    await rvr.reset_yaw()	
    print("rvr ready!")
    scan = [[0] * (xrange) for i in range((yrange))] # set up the array with all zeros
    for i in range(xrange): # set up an empty list of length xrange
        xstack.append(0)
    for i in range(bins): # set up an empty list of bin values for current and old values
        xbins.append(0)
        xbinsold.append(0)


async def main():
    global current_key_code, speed, heading, flags, reverse
    global epoch, xbinsold, ystack, xbins, xbinsold, scan
	
    while True:	
        frames = pipeline.wait_for_frames()	
        depth = frames.get_depth_frame()	def main():
        if not depth: continue  # just do the loop again until depth returns true

        # Get the data
        for y in range(yrange):
            for x in range(0,xrange,xincrement):
                scan[y][x] = depth.get_distance(x, y)

        # Start averaging and binning:
        # First, average vertically   
        for x in range(0,xrange,xincrement):
            xstack[x] = 0
            for y in range(yrange):  # sum up all the y's in each x stack
                xstack[x] = xstack[x] + scan[y][x]
            xstack[x] = round(xstack[x]/yrange,2)  # take average across the y's

        # then, sum and average across each horizontal bin
        for i in range(bins):
            xbins[i] = 0
            for j in range(binsize):
                xbins[i] = xbins[i] + xstack[i*binsize + j*xincrement]  # sum the bin
            xbins[i] = round(xbins[i]/binsize,2) # average the bin
        print("Xbins unsmoothed", xbins)  
        if (epoch != 0):
            for i in range(bins):
                xbins[i] = round((xbins[i]+xbinsold[i])/2,2)   # bayesian smooothing
            print("Xbins smoothed", xbins)  
        xbinsold = list(xbins) # copy latest bins into oldbins for bayesian smoothing
        if epoch == 0:
            epoch = 1
 
	
        # flags = 0	
        # if reverse:	
        #     flags = DriveFlagsBitmask.drive_reverse	
        # else:	
        #     flags=DriveFlagsBitmask.none.value	
        # await rvr.drive_with_heading(speed, heading, flags)	
        # # sleep the infinite loop for a 10th of a second to avoid flooding the serial port.	
        # await asyncio.sleep(0.1)	

setup()

try:	
    # Create a pipeline	
    pipeline = rs.pipeline()	
    pipeline.start()	

    # Create a config and configure the pipeline to stream	
    #  different resolutions of color and depth streams	
    config = rs.config()	
    config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)	
    print("Starting...")	
    loop.run_until_complete(	
        main()	
        )	
except KeyboardInterrupt:	
        print("Keyboard Interrupt...")	
finally:	
        print("Press any key to exit.")
        exit(1)
