   #!/usr/bin/python3

import sys
from daqhats import hat_list, HatIDs, mcc118
import csv
import time
import board
import busio
#import adafruit_adx134x
# get hat list of MCC daqhat boards
board_list = hat_list(filter_by_id = HatIDs.ANY)
if not board_list:
    print("No boards found")
    sys.exit()

# Read and display every channel
for entry in board_list:

    if entry.id == HatIDs.MCC_118:
        print("Board {}: MCC 118".format(entry.address))
        board = mcc118(entry.address)
        while True:
            for channel in range(board.info().NUM_AI_CHANNELS):
                value = board.a_in_read(channel)
                print("Ch {0}: {1:.3f}".format(channel, value))
            time.sleep(0.1)