#! /usr/bin/env python

'''
Loads a gait file, executes the gait, and logs the position
'''


import sys
import pdb
import time
from SineModel import SineModel5
from Robot import Robot
from Strategy import TimedFileStrategy
from wii.WiiTrackFastClient import WiiTrackFastClient
from datetime import datetime, timedelta
from Robot import RobotFailure

def savePosition(wiiTrack, posAgeList):
    position,age = wiiTrack.getPosAge()
    #print 'savePosition:', position, age
#    pdb.set_trace()
    if position is None:
        return '-1 -1 %f' % age
    else:
        timeOfPosition = datetime.now() - timedelta(seconds = age)

        posAgeList.append((timeOfPosition, position, age))
        #print len(posAgeList)
        return ' '.join([str(x) for x in [timeOfPosition] + position + [age]])



def main():
    if len(sys.argv) < 3:
        print 'Usage: %s input_gait_file output_position_file' % sys.argv[0]
        sys.exit(1)

    gaitFile = sys.argv[1]
    posFile  = sys.argv[2]


    strategy = TimedFileStrategy(posFile = gaitFile)

    motionFunction, logInfo = strategy.getNext()

    #runman = RunManager()
    #runman.do_many_runs(strategy, SineModel5.typicalRanges)

    #timeScale = .3
    #motionFunctionScaled = scaleTime(motionFunction, timeScale)
    wiiTrack = WiiTrackFastClient("localhost", 8080)
    time.sleep(.5)
    position,age = wiiTrack.getPosAge()
    if age is None:
        raise Exception('Could not get position from wiiTrack.')

    #robot = Robot(loud = True)
    robot = Robot()


    ##############
    bucket = []

    def foo():
        savePosition(wiiTrack, bucket)

    robot.run(motionFunction, runSeconds = 10, resetFirst = True,
                               interpBegin = 2, interpEnd = 2, extraLogInfoFn = foo)

    relTimeBucket = []
    for ii, line in enumerate(bucket):
        delta = line[0] - bucket[0][0]
        if delta.microseconds/1e6 < 1:
                    relTime = delta.seconds + delta.microseconds/1e6
                    relTimeBucket.append((relTime, line[1], line[2]))
        #pdb.set_trace()
    print relTimeBucket[0]
#    if list(relTimeBucket[-1])[0]-list(relTimeBucket[0])[0] < 13.7:
 #       exit(2)
        ##############

    ff = open (posFile, 'w')
    ff.write('# time (junk junk)x9 pos.x pos.y 0 age\n')
    for ii, timePosAge in enumerate(relTimeBucket):
        timeOfPosition, position, age = timePosAge
        line = '%.3f' % timeOfPosition
        line += ' -1 -1' * 9
        line += ' %.1f %.1f %.1f' % (position[0], position[1], 0)
        line += ' %f' % age
        ff.write(line + '\n')
    ff.close()
    print 'Wrote position file:', posFile
    lines = open(posFile, 'r').readlines()
    speed = ((float(lines[1].split()[19])-float(lines[-1].split()[19]))**2+(float(lines[1].split()[20])-float(lines[-1].split()[20]))**2)**0.5/(6.25*12)
    print 'SPEED: ', speed


if __name__ == '__main__':
    main()
