"""D/AprSenseService( 6949): countableFrame -> FrameInfo{streamType=1024, resolution=1157628624,
pixelFormat=6, stride=0, frameNum=255, exposure=0, intArg3=0, intArg4=0,intArg5=0, intArg6=0,
intArg7=0, timeStamp=0, platformTS=1543980791005394, mByteBuffer=null}frame ->
com.segway.robot.sdk.vision.internal.framebuffer.RecyclableFrame@1f7b5a87 """

import os
import sys
import string

file = open("/Users/gaominghui/Desktop/logcats/1205/countableFrame4.log", 'r', encoding="UTF-8")
line = file.readline()
pts1024 = []
pts2048 = []
while line:
    if 'platformTS' in line:
        if 'streamType=1024' in line:
            pts1024.append(line[line.find('platformTS') + 11:line.find(", mBy")])
            print("pts 1024", line[line.find('platformTS') + 11:line.find(", mBy")])
        if 'streamType=2048' in line:
            pts2048.append(line[line.find('platformTS') + 11:line.find(", mBy")])
            # print("pts 2048", line[line.find('platformTS') + 11:line.find(", mBy")])
    line = file.readline()
print(" type 1024 platformTs len :", len(pts1024))
print(" type 2048 platformTs len :", len(pts2048))

# find the duplicated value in pts1024
for index in range(len(pts1024)):
    val = pts1024[index]
    count = 0
    for pts in pts1024:
        if pts == val:
            count = count + 1
    if count > 1:
        print("repeat ", val)

print("finish check 1024.")

for index in range(len(pts2048)):
    val = pts2048[index]
    count = 0
    for pts in pts2048:
        if pts == val:
            count = count + 1
    if count > 1:
        print("repeat ", val)

print("finish check 2048.")

