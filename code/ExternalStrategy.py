#! /usr/bin/env python


from numpy import array, ix_, vstack, linspace, hstack, ones, mean
from time import sleep
import os

from Robot import MIN_INNER, MAX_INNER, MIN_OUTER, MAX_OUTER, NORM_CENTER
from Strategy import Strategy, OneStepStrategy
from util import matInterp, prettyVec
from SineModel import SineModel5
import subprocess as sp
from asyncproc import Process


class NEATStrategy(OneStepStrategy):
    '''
    A strategy that calls a NEAT executable to determine a gait
    '''

    def __init__(self, *args, **kwargs):
        super(NEATStrategy, self).__init__([], [])

        ##############################
        #   HyperNEAT Parameters
        ##############################
        
        self.executable = '/home/team/s/h2_synced/HyperNEAT_v2_5/out/Hypercube_NEAT'
        #self.motionFile = '/home/team/s/h2_synced/HyperNEAT_v2_5/out/spiderJointAngles.txt'
        self.motionFile = 'spiderJointAngles.txt'
        self.datFile    = '/home/team/s/h2_synced/HyperNEAT_v2_5/out/SpiderRobotExperiment.dat'

        self.avgPoints       = 4                         # Average over this many points
        self.junkPoints      = 1000
        # How many lines to expect from HyperNEAT file
        self.expectedLines   = self.junkPoints + 12 * 40 * self.avgPoints
        self.motorColumns    = [0,1,4,5,2,3,6,7]         # Order of motors in HyperNEAT file
        self.generationSize  = 9
        self.initNeatFile    = kwargs.get('initNeatFile', None)   # Pop file to start with, None for restart
        self.prefix          = 'delme'
        self.nextNeatFile    = '%s_pop.xml' % self.prefix
        
        #self.proc = sp.Popen((self.executable,
        #                      '-O', 'delme', '-R', '102', '-I', self.datFile),
        #                     stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE)
        #os.system('%s -O delme -R 102 -I %s' % (self.executable, self.datFile))
        if self.initNeatFile is None:
            self.proc = Process((self.executable,
                                 '-O', self.prefix, '-R', '102', '-I',
                                 self.datFile))
        else:
            print 'Starting with neatfile', self.initNeatFile
            self.proc = Process((self.executable,
                                 '-O', self.prefix, '-R', '102', '-I',
                                 self.datFile, '-X', self.nextNeatFile, '-XG', '1'))
            
        #'%s -O delme -R 102 -I %s' % (self.executable, self.datFile))

        self.nRuns = 0


    def __del__(self):
        print 'Waiting for %s to exit...' % self.executable,
        code = self.proc.wait()
        print 'done.'


    def getNext(self):
        '''Get the next point to try.  This reads from the file
        self.motionFile'''

        #print 'TRYING READ STDOUT'
        #stdout = self.proc.stdout.read()
        #print 'TRYING READ STDERR'
        #stderr = self.proc.stderr.read()

        #print 'STDOUT:'
        #print stdout
        #print 'STDERR:'
        #print stderr

        if self.nRuns == self.generationSize:
            print 'Restarting process after %d runs, push enter when ready...' % self.generationSize
            raw_input()
            #sleep(10)
            print 'Continuing with neatfile', self.nextNeatFile
            self.proc = Process((self.executable,
                                 '-O', self.prefix, '-R', '102', '-I',
                                 self.datFile, '-X', self.nextNeatFile, '-XG', '1'))
            self.nRuns = 0

        #print 'On iteration', self.nRuns+1

        while True:

            out = self.proc.read()
            if out != '':
                #print 'Got stdout:'
                #print out
                pass
            out = self.proc.readerr()
            if out != '':
                #print 'Got stderr:'
                #print out
                pass

            try:
                ff = open(self.motionFile, 'r')
            except IOError:
                print 'File does not exist yet'
                sleep(.2)
                continue

            lines = ff.readlines()
            nLines = len(lines)
            if nLines < self.expectedLines:
                print 'Oops, only %d of %d lines!' % (nLines, self.expectedLines)
                ff.close()
                sleep(.5)
                continue
            break

        self.nRuns += 1

        for ii,line in enumerate(lines[self.junkPoints:]):
            #print 'line', ii, 'is', line
            nums = [float(xx) for xx in line.split()]
            if ii == 0:
                rawPositions = array(nums)
            else:
                rawPositions = vstack((rawPositions, array(nums)))

        # swap and scale rawPositions appropriately
        rawPositions = rawPositions.T[ix_(self.motorColumns)].T  # remap to right columns

        #print 'First few lines of rawPositions are:'
        #for ii in range(10):
        #    print prettyVec(rawPositions[ii,:], prec=2)
        
        # Average over every self.avgPoints
        for ii in range(self.expectedLines/self.avgPoints):
            temp = mean(rawPositions[ii:(ii+self.avgPoints),:], 0)
            if ii == 0:
                positions = temp
            else:
                positions = vstack((positions, temp))

        #print 'First few lines of positions are:'
        #for ii in range(10):
        #    print prettyVec(positions[ii,:], prec=2)
        
        # scale from [-1,1] to [0,1]
        positions += 1
        positions *= .5
        # scale from [0,1] to appropriate ranges
        innerIdx = [0, 2, 4, 6]
        outerIdx = [1, 3, 5, 7]
        for ii in innerIdx:
            positions[:,ii] *= (MAX_INNER - MIN_INNER)
            positions[:,ii] += MIN_INNER
        for ii in outerIdx:
            positions[:,ii] *= (MAX_OUTER - MIN_OUTER)
            positions[:,ii] += MIN_OUTER
        # append a column of 512s
        positions = hstack((positions,
                            NORM_CENTER * ones((positions.shape[0],1))))
        times = linspace(0,12,positions.shape[0])
        
        # return function of time
        return lambda time: matInterp(time, times, positions)


    def updateResults(self, dist):
        '''This must be called for the last point that was handed out!

        This communicates back to the running subprocess.
        '''

        dist = float(dist)

        # MAKE SURE TO CALL super().updateResults!
        super(NEATStrategy, self).updateResults(dist)

        # Send fitness to process
        #out,err = proc.communicate('%f\n' % dist)

        print 'Sending to process: %f' % dist
        self.proc.write('%f\n' % dist)

        #print 'TRYING READ STDOUT'
        #stdout = self.proc.stdout.read()
        #print 'TRYING READ STDOUT'
        #stderr = self.proc.stderr.read()
        #
        #print 'Got stdout:'
        #print stdout
        #print 'Got stderr:'
        #print stderr

        out = self.proc.read()
        if out != '':
            #print 'Got stdout:'
            #print out
            pass
        out = self.proc.readerr()
        if out != '':
            #print 'Got stderr:'
            #print out
            pass

    def logHeader(self):
        return '# NEATStrategy starting\n'



def main():
    pass



if __name__ == '__main__':
    main()

