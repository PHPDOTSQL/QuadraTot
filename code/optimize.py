#! /usr/bin/env python

'''

@date: 4 October 2010

'''

"""
Uses random movements and manual optimization to choose the parameters
of the robots' motion.

"""

import math, pdb
import random
from copy import copy
from Robot import runRobotWith, cropPositions
from SineModel import sineModel

def initialState(ranges):
    """ 
    Given the ranges of the different parameters, chooses random values for
    each parameter. The ranges of parameters are in a list of tuples.

    """
    parameters = []  # List of the chosen values for the parameters
    for rang in ranges:
        # Chooses random values for each parameter (initial state)
        if isinstance(rang[0], bool):  # If range is (true, false),
				       # choose true or false
            parameters.append(random.uniform(0,1) > .5)
        else:
            parameters.append(random.uniform(rang[0], rang[1]))
    return parameters

def neighbor(ranges, parameters):
    """
    Given a list of parameters, picks a random parameter to change, randomly
    changes it, and returns a new list.

    """
    ret = copy(parameters)
    print '  ** Neighbor old', ret
    index = random.randint(0, len(parameters) - 1)

    print ranges
    if isinstance(ranges[index][0], bool):
        ret[index] = (random.uniform(0,1) > .5)
    else:
        ret[index] = random.uniform(ranges[index][0], ranges[index][1])

    print '  ** Neighbor new', ret
    return ret

def slightNeighbor(ranges, parameters):
    """
    Given a list of parameters, picks a random parameter to change, and
    decreases or increases it slightly.

    """
    ret = copy(parameters)
    print '  ** Neighbor old', ret
    index = random.randint(0, len(parameters) - 1)

    print ranges
    if isinstance(ranges[index][0], bool):
        ret[index] = (random.uniform(0,1) > .5)
    else:
        if random.randint(0, 1) == 0:  # decrease slightly
	    ret[index] = ret[index] - (.1 * (ranges[index][1] - ranges[index][0]))
        else:  # increase slightly
	    ret[index] = ret[index] - (.1 * (ranges[index][1] - ranges[index][0]))

    print '  ** Neighbor new', ret
    return ret

def doRun():
    # Parameters are: amp, tau, scaleInOut, flipFB, flipLR
    
    android = Robot()
    # TODO: motion = Motion()
    # TODO: Move ranges below 
    ranges = [(0, 400),
              (.5, 8),
              (-2, 2),
              (False, True),
              (False, True)]

    ranges = [(0, 400),
              (.5, 8),
              (-2, 2),
              (-1, 1),
              (-1, 1)]
    currentState = initialState(ranges)
    statesSoFar = set()  # Keeps track of the states tested so far
    
    bestDistance = -1e100

    for ii in range(10000):
	if currentState not in statesSoFar:  # Make sure this state is new
	    stateSoFar.add(currentState)
            print
            print 'Iteration', ii, 'params', currentState
        
            motionModel = lambda time: sineModel(time,
                                                 parameters = currentState,
                                                 croppingFunction = cropPositions)

            android.run(motionModel)

            currentDistance = float(raw_input("Enter distance walked by Android: "))

            if currentDistance >= bestDistance:  # Is this a new best?
                bestState = copy(currentState)  # Save new neighbor to best found
                bestDistance = copy(currentDistance)

            print "best so far", bestState, bestDistance  # Prints best state and distance so far

        currentState = neighbor(ranges, bestState)  # Pick some neighbor

    return bestState  # Return the best solution found (a list of params)

def main():
    doRun()

if __name__ == '__main__':
    main()