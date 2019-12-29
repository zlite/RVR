
# Test suite for binning


ROIx1 = 0
ROIx2 = 640
ROIy1 = 240
ROIy2 = 300
yrange = ROIy2-ROIy1
xrange = ROIx2-ROIx1
xincrement = 5
binsize = 10
bins = round(xrange/(binsize * xincrement))  # should be 13 bins in this case
epoch = 0
scan = [[],[]]
xstack = []
xbins = []
xbinsold = []


def setup():
    global scan, ystack, xbins, xbinsold

    scan = [[0] * (xrange) for i in range((yrange))] # set up the array with all zeros
    print ("Creating fake data with a gradient")
    for x in range(0,xrange,xincrement):   # simulating grabbing every fifth pixel
        for y in range(yrange):
            scan[y][x] = round((x+y)/100,2)
    for i in range(xrange): # set up an empty list of length xrange
        xstack.append(0)
    for i in range(bins): # set up an empty list of bin values for current and old values
        xbins.append(0)
        xbinsold.append(0)


def main():
    global epoch, xbinsold, ystack, xbins, xbinsold, scan

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

    
    if (epoch == 0):
        print ("Creating new fake data with a different gradient")
        for x in range(0,xrange,xincrement):   # simulating grabbing every fifth pixel
            for y in range(yrange):
                scan[y][x] = round((x+y)/75,2)
        epoch = 1

setup()
main()
main()



