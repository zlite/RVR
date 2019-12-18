depth = [3,3,3,4,4,4,5,5,5,4,4,4,3,3,3,2,2,2]
batch = 3
average = 0
count = 0
zonecount = 0
zone = []

for x in range(len(depth)):
    average = average + depth[x]
    count = count + 1
    if count == batch:      
        average = average/batch
        zone.append(average)
        zonecount = zonecount + 1
        count = 0
        average = 0
        
zonecount = int(len(depth)/batch)
for x in range(zonecount):
    print(zone[x])
print("Longest range zone", zone.index(max(zone)))
