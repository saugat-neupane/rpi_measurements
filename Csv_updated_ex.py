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
        count=0
        row = []
        #with open('data.txt','w') as f:    #If measuring per second its min*sec, change accordingly(Multiply by 10 if interval is 0.1)
        with open("data.csv",'w') as file:
            writer = csv.writer(file)
            writer.writerow(['Ch:0', 'Ch:1', 'Ch:2', 'Ch:7'])
            while count < (60):
                for channel in [0,1,2,7]:#range(board.info().NUM_AI_CHANNELS):
                    values = board.a_in_read(channel)
                    #file.write("Ch {0}: {1:.3f}\n".format(channel,values))
                    #writer.writerow([values])
                    #row.append(values)
                    writer.writerow([f'Ch:{channel}',values])
                    print(f"Ch {channel}: {values:.3f}")
                    #print("Ch {0}: {1:.3f}\n".format(channel,values))
                time.sleep(0.1)
                file.write("")
                count+=1



    ## Additional stuff

#interval =0.1
#duration = 20
#num_readings = int(duration/interval)

#Reading the values at several points
##   acceleration = accelerometer.acceleration
  #  print("Acceleration: X = %.2f, Y = %.2f, X = %, 2f" % (acceleration[0], acceleration[1], acceleration[2]))
   # print('a')
    #time.sleep(interval)
#    print('b')