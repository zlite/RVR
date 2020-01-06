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


# we set the depth resolution on the Realsense 435 device to 640x480, with 0,0 in the top left corner
ROIx1 = 0
ROIx2 = 640
ROIy1 = 220
ROIy2 = 280
yres = 480
xres = 640
yrange = ROIy2-ROIy1
xrange = ROIx2-ROIx1
xincrement = 5
binsize = 10
lastgood = 1 # this is the variable we use to pass over 0 depth pixels
bins = round(xrange/(binsize * xincrement)) # should be 13 bins in this case
epoch = 0
scan = [[],[]]
xstack = []
xbins = []
xbinsold = []
speed = 50 # Valid speed values are 0-255
heading = 0 # Valid heading values are 0-359
reverse = False
gain = 2.5


loop = asyncio.get_event_loop()
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

def setup():
    global scan, xstack, xbins, xbinsold
    print("rvr ready!")

    scan = [[0 for i in range(xres)] for j in range(yres)] # dimension the array

    for i in range(ROIx1,ROIx2): # set up an empty list of length xrange
        xstack.append(0)
    for i in range(bins): # set up an empty list of bin values for current and old values
        xbins.append(0)
        xbinsold.append(0)


async def main():

    global current_key_code, speed, heading, flags, reverse
    global epoch, xbinsold, ystack, xbins, xbinsold, scan, lastgood
    global ROIy1, ROIy2, yrange

    await rvr.wake()
    await rvr.reset_yaw()

    while True:
        frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        if not depth: continue  # just do the loop again until depth returns true

        yrange = ROIy2-ROIy1

        # Get the data
        for y in range(ROIy1,ROIy2):
            for x in range(ROIx1,ROIx2,xincrement):
                scan[y][x] = depth.get_distance(x, y)
                if scan[y][x] == 0:   # if we get zero depth noise, just replace it with the last known good depth reading
                    scan[y][x] = lastgood
                else:
                    lastgood = 0.1
#                    lastgood = scan[y][x]  # good data

        # Start averaging and binning:
        # First, average vertically
        for x in range(ROIx1,ROIx2,xincrement):
            xstack[x] = 0
            for y in range(ROIy1,ROIy2):  # sum up all the y's in each x stack
                xstack[x] = xstack[x] + scan[y][x]
            xstack[x] = round(xstack[x]/yrange,2)  # take average across the y's
            if 0 <= xstack[x] <= 0.5:  # something is close
                print("X",end = '')
            elif 0.501 <= xstack[x] <= 1.0:
                print("x",end = '')
            elif 1.001 <= xstack[x] <= 1.5:
                print("-",end = '')
            elif 1.501 <= xstack[x] <= 2.0:
                print(".",end = '')
            elif xstack[x] > 2.001:
                print(" ",end = '')
            else:
                print("Something went wrong with my printing. X =", xstack[x])
        print("\n") # start a new line

        # then, sum and average across each horizontal bin

        average = 0
        total = 0
        for i in range(bins-1):
            xbins[i] = 0
            for j in range(binsize):
                xbins[i] = xbins[i] + xstack[i*binsize*xincrement + j*xincrement]  # sum the bin
            xbins[i] = round(xbins[i]/binsize,2) # average the bin
            average = average + xbins[i]   # sum up all the x stacks
            total = total + 1
        average = round(average/total,2)    # take the average of all the xstacks
#        print("Average distance: ", average)

        # expand the ROI
        if 0.0 <= average <= 0.25:
            ROIy1 = 220
            ROIy2 = 280
            yrange = ROIy2-ROIy1
        elif 0.26 <= average <= 0.50:
            ROIy1 = 220
            ROIy2 = 280
            yrange = ROIy2-ROIy1
        elif 0.51 <= average <= 0.75:
            ROIy1 = 220
            ROIy2 = 280
            yrange = ROIy2-ROIy1
        elif 0.76 <= average <= 1.00:
            ROIy1 = 220
            ROIy2 = 280
            yrange = ROIy2-ROIy1
        else:
            ROIy1 = 220
            ROIy2 = 280
            yrange = ROIy2-ROIy1
        if (epoch != 0):
            for i in range(bins):
                xbins[i] = round((xbins[i]+xbinsold[i])/2,2)   # Bayesian smooothing
#            print("Xbins smoothed", xbins)
#            print("Longest range bin:", xbins.index(max(xbins)))
        xbinsold = list(xbins) # copy latest bins into oldbins for bayesian smoothing
        if epoch == 0:
            epoch = 1

        # this is the driving part

        heading = heading + int(((xbins.index(max(xbins)) - (int(bins/2)))*gain))  # if higher than 6, steer to the right in 5 degree increments; if lower, drive left

        # check the speed value, and wrap as necessary.
        if speed > 255:
            speed = 255
        elif speed < -255:
            speed = -255

        # check the heading value, and wrap as necessary.
        if heading > 359:
            heading = heading - 359
        elif heading < 0:
            heading = 359 + heading

        flags = 0
        if reverse:
            flags = DriveFlagsBitmask.drive_reverse
        else:
            flags=DriveFlagsBitmask.none.value
        await rvr.drive_with_heading(speed, heading, flags)


setup()

try:
    # Create a pipeline
    pipeline = rs.pipeline()
    pipeline.start()

    # Create a config and configure the pipeline to stream
    #  different resolutions of color and depth streams
    config = rs.config()
    config.enable_stream(rs.stream.depth, xres, yres, rs.format.z16, 30)
    print("Starting...")
    loop.run_until_complete(
        main()
        )
except KeyboardInterrupt:
        print("Keyboard Interrupt...")
# finally:
#         print("Press any key to exit.")
#         exit(1)
