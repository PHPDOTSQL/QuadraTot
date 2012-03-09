#! /usr/bin/env python

# WARNING: These are all fake!

MIN_INNER = 150
MAX_INNER = 770
MIN_OUTER = 30
#MAX_OUTER = 940
#MAX_OUTER = 800 # changing because Robot hits antenna
MAX_OUTER = 680  # changing because screws still interfere

POS_FLAT      = [512] * 9
POS_READY     = [770,  40] * 4 + [512]
POS_HALFSTAND = [700, 100] * 4 + [512]
POS_STAND     = [512, 150] * 4 + [512]

POS_CHECK_1   = [770, 200] * 4 + [512]
POS_CHECK_2   = [670, 300] * 4 + [512]
POS_CHECK_3   = [670, 300] * 4 + [512-70]




if __name__ == '__main__':
    toprint = ('MIN_INNER', 'MAX_INNER',
               'MIN_OUTER', 'MAX_OUTER',
               'POS_FLAT', 'POS_READY', 'POS_HALFSTAND', 'POS_STAND')

    #pdb.set_trace()
    for var in toprint:
        print '%14s = %s' % (var, repr(eval(var)))
