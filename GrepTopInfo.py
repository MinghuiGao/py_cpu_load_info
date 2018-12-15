import numpy as np

file = open("/Users/gaominghui/Desktop/logcats/1210/rk3399/glog/fe_only.log", 'r', encoding="UTF-8")
line = file.readline()
visionCpu = []
visionChecker = []

while line:
    if '{eservice.vision}' in line:
        fields = line.split(" ")
        visionCpu.append(fields[17])
    if '{nservicechecker}' in line:
        fileds = line.split(" ")
        visionChecker.append(fileds[17])

    line = file.readline()

print(visionChecker)

for f in visionCpu:
    print(f)

cpuUsageF = np.array(visionCpu).astype(np.float)

average = np.mean(cpuUsageF)
print(average)

maxUsage = np.max(cpuUsageF)
minUsage = np.min(cpuUsageF)

print("max:", maxUsage, "min:", minUsage)


def analysisVision(cpuUsage):
    cpuUsageF = np.array(cpuUsage).astype(np.float)
    average = np.mean(cpuUsageF)
    maxUsage = np.max(cpuUsageF)
    minUsage = np.min(cpuUsageF)
    return [average, maxUsage, minUsage]
