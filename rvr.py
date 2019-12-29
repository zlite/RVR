## License: Apache 2.0. See LICENSE file in root directory.	
## Copyright(c) 2019 Intel Corporation. All Rights Reserved.	


#####################################################	# Test suite for binning
##                   Frame Queues                  ##	
#####################################################	


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


ROIx1 = 0	ROIx1 = 0
ROIx2 = 640	ROIx2 = 640
@@ -26,132 +10,65 @@
xrange = ROIx2-ROIx1	xrange = ROIx2-ROIx1
xincrement = 5	xincrement = 5
binsize = 10	binsize = 10
bins = round(xrange/(binsize * xincrement))	bins = round(xrange/(binsize * xincrement))  # should be 13 bins in this case

epoch = 0
loop = asyncio.get_event_loop()	scan = [[],[]]
rvr = SpheroRvrAsync(	xstack = []
    dal=SerialAsyncDal(	xbins = []
        loop	xbinsold = []
    )	
)	

def setup():
async def main():	    global scan, ystack, xbins, xbinsold
    global current_key_code	
    global speed	
    global heading	
    global flags	
    global reverse	

    speed = 64 # Valid speed values are 0-255	
    heading = 10 # Valid heading values are 0-359	
    reverse = False	
    await rvr.wake()	
    await rvr.reset_yaw()	
    print("rvr ready!")	
    # issue the driving command	
    scan = [[],[]]	
    scan = [[0] * (xrange) for i in range((yrange))] # set up the array with all zeros	    scan = [[0] * (xrange) for i in range((yrange))] # set up the array with all zeros
    ystack = []	    print ("Creating fake data with a gradient")
    for x in range(0,xrange,xincrement):   # simulating grabbing every fifth pixel
        for y in range(yrange):
            scan[y][x] = round((x+y)/100,2)
    for i in range(xrange): # set up an empty list of length xrange	    for i in range(xrange): # set up an empty list of length xrange
        ystack.append(0)	        xstack.append(0)
    xbins = []	
    xbinsold = []	
    for i in range(bins): # set up an empty list of bin values for current and old values	    for i in range(bins): # set up an empty list of bin values for current and old values
        xbins.append(0)	        xbins.append(0)
        xbinsold.append(0)	        xbinsold.append(0)
    while True:	
        frames = pipeline.wait_for_frames()	
        depth = frames.get_depth_frame()	def main():
        if not depth: continue  # just do the loop again until depth returns true	    global epoch, xbinsold, ystack, xbins, xbinsold, scan
        # start = time.time()	
        for y in range(yrange):	    # Start averaging and binning:
            for x in range(0,xrange,xincrement):	    # First, average vertically   
                scan[y][x] = depth.get_distance(x, y)	    for x in range(0,xrange,xincrement):
        # finish = round(time.time() - start,2)	        xstack[x] = 0
        # print("Gathering data: ", finish)	        for y in range(yrange):  # sum up all the y's in each x stack
        # start = time.time()	            xstack[x] = xstack[x] + scan[y][x]
        # Now start averaging and binning:	        xstack[x] = round(xstack[x]/yrange,2)  # take average across the y's
        # First, average vertically	
        for x in range(0,xrange,xincrement):	
            ystack[x] = 0	    # then, sum and average across each horizontal bin
            for y in range(yrange):	    for i in range(bins):
                ystack[x] = ystack[x] + scan[y][x]	        xbins[i] = 0
            ystack[x] = round(ystack[x]/yrange,2)  # take average across the y's	        for j in range(binsize):
#        print("Ystack", ystack)	            xbins[i] = xbins[i] + xstack[i*binsize + j*xincrement]  # sum the bin
        # finish = round(time.time() - start,2)	        xbins[i] = round(xbins[i]/binsize,2) # average the bin
        # print("Vertical averaging: ", finish)	    print("Xbins unsmoothed", xbins)  
        # start = time.time()	    if (epoch != 0):
        # then, sum and average across each horizontal bin	
        for i in range(bins):	        for i in range(bins):
            xbins[i] = 0	            xbins[i] = round((xbins[i]+xbinsold[i])/2,2)   # bayesian smooothing
            for j in range(binsize):	        print("Xbins smoothed", xbins)  
                xbins[i] = xbins[i] + ystack[i*binsize + j*xincrement]  # sum the bin	    xbinsold = list(xbins) # copy latest bins into oldbins for bayesian smoothing
#                print(i*binsize+j)	
            xbins[i] = round(xbins[i]/binsize,2) # average the bin	
        # finish = round(time.time() - start,2)	    if (epoch == 0):
        # print("Binning: ", finish)	        print ("Creating new fake data with a different gradient")
        print("Xbins", xbins)	        for x in range(0,xrange,xincrement):   # simulating grabbing every fifth pixel
        xbinsold = xbins # copy latest bins into oldbins for bayesian smoothing	            for y in range(yrange):

                scan[y][x] = round((x+y)/75,2)
        # for y in range(y):	        epoch = 1
        #     for x in range(x,3):	
        #         dist = depth.get_distance(x, y)	setup()
        #         if depth1 < dist and dist < depth2:	main()
        #             print("x", end = '')	main()
        #         else:	
        #             print(" ", end = '')	
        #     print("\n")	
#        time.sleep(0.1)	
            # for x in range(width):	
            #     scan[x] = round(depth.get_distance(x, y),2)	
            # average = 0	
            # count = 0	
            # zonecount = 0	
            # zone = []	
            # for x in range(len(scan)):	
            #     average = average + scan[x]	
            #     count = count + 1	
            #     if count == batch:	
            #         average = round(average/batch,2)	
            #         zone.append(average)	
            #         zonecount = zonecount + 1	
            #         count = 0	
            #         average = 0	
            # zonecount = int(len(scan)/batch)	
            # # for x in range(zonecount):	
            # #     print(zone[x])	
#            print("Scan: ", scan)	
#            print ("Zones: ", zone)	
#            print("Longest range zone", zone.index(max(zone)))	
#            time.sleep(1)	
        #         if depth.get_distance(x, y) > dist:	
        #             max_depth = x	
        # print(max_depth)	
        # flags = 0	
        # if reverse:	
        #     flags = DriveFlagsBitmask.drive_reverse	
        # else:	
        #     flags=DriveFlagsBitmask.none.value	
        # await rvr.drive_with_heading(speed, heading, flags)	
        # # sleep the infinite loop for a 10th of a second to avoid flooding the serial port.	
        # await asyncio.sleep(0.1)	


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
# finally:	
#         print("Press any key to exit.")	
#         exit(1)
