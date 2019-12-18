## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2019 Intel Corporation. All Rights Reserved.

#####################################################
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

ROIx1 = 200
ROIx2 = 400
ROIy1 = 0
ROIy2 = 10
depth1 = 0
depth2 = 1


loop = asyncio.get_event_loop()
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

async def main():
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
    scan = []
    for x in range(ROIx1,ROIx2):
        scan.append(False)
    while True:
        frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        if not depth: continue  # just do the loop again until depth returns true
        for y in range(ROIy1,ROIy2):
            for x in range(ROIx1, ROIx2):
                dist = depth.get_distance(x, y)
                if depth1 < dist and dist < depth2:
                    print("x", end = '')
                else:
                    print(" ", end = '')
            print("\n")
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
        key_helper.end_get_key_continuous()
# finally:
#         print("Press any key to exit.")
#         exit(1)
