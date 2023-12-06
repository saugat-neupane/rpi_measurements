from daqhats import mcc118, OptionFlags, HatIDs, HatError
import numpy as np
import pandas as pd
import time
#Preset constants
address = 0
sample_rate = 2000 #20 kS/s
duration = 10
samples_per_channel = sample_rate * duration
channels = [0,1,2,3]
channel_names = ["Z-accel", "X-accel", "Y-accel", "Temperature"]

#Instantiating the MCC
hat = mcc118(address)

#Configuring scan options
options = OptionFlags.CONTINUOUS

#Buffering for data
buffer = np.zeros(samples_per_channel * len(channels))

#Starting scan
hat.a_in_scan_start(len(channels),samples_per_channel,sample_rate, options)
#Recording the time
start_time = time.time()

try:
    while(time.time()- start_time) < duration:

        curr_readings = hat.a_in_scan_read(samples_per_channel,0)
        buffer = np.append(buffer, curr_readings.data)
    #Trimmig the buffer to actual number of samples read
    buffer = buffer[:int((time.time()-start_time) *sample_rate *len(channels))]

    #Conversion to m/s^2
    buffer[:3]*= 9.80665

    #DataFrame creation to store the values
    df = pd.DataFrame(buffer.reshape(-1, len(channels)), columns = channel_names)

    df.to_csv('ADXL Data.csv',index = False)

except KeyboardInterrupt:
    # When Ctrl + C is pressed
    print("Exiting loop.")

except HatError as e:
    #Issues withj daqhat library
    print(f"Error:{e}")

finally:
    #STop the scan if it was started
    hat.a_in_scan_stop()

    #Release the scan buffer
    hat.a_in_scan_cleanup()