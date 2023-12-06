from daqhats import mcc118, OptionFlags, HatIDs, HatError
import numpy as np
import pandas as pd
import time
#Preset constants
address = 0 #Where the MCC118 is located on rpi
sample_rate = 2000 #20 kS/s
duration = 10 #Duration in seconds that is to be measured
samples_per_channel = sample_rate * duration
channels = [0,1,2,3]
channel_names = ["Z-Voltage", "X-Voltage", "Y-Voltage", "Temperature"]

#Creatimh an instance of MCC
hat = mcc118(address)

#Configuring scan options
options = OptionFlags.CONTINUOUS

#Buffering for data
buffer = []

#Starting scan
hat.a_in_scan_start(len(channels),samples_per_channel,sample_rate, options)

#Recording the time
start_time = time.time()

try:
    while(time.time()- start_time) < duration:

        curr_readings = hat.a_in_scan_read(samples_per_channel,0)
        buffer.extend(curr_readings.data)
    #Trimmig the buffer to actual number of samples read
    complete_sets = len(buffer)//len(channels)
    trimmed_buffer = buffer[:complete_sets * len(channels)]

    df = pd.DataFrame(np.array(trimmed_buffer).reshape(-1,len(channels)),columns = channel_names)

    #Conversion to m/s^2
    conv2std = 1000/400*9.80665     #400 for 2g range, 100 for 8g range
    df['Z Vib'] = (df['Z-Voltage']-0.9)* conv2std
    df['X Vib'] = (df['X-Voltage']-0.9)* conv2std
    df['Y Vib'] = (df['Y-Voltage']-0.9)* conv2std
    df['Temp'] = (df['Temperature']*1000 -967)/3 +25.0

    #DataFrame creation to store the values
   # df = pd.DataFrame(np.array(trimmed_buffer).reshape(-1,len(channels)),columns = channel_names)
    converted_df = df[['Z Vib','X Vib','Y Vib','Temp']]
    converted_df.to_csv('ADXL_Data2_0.csv',index = False)

except KeyboardInterrupt:
    # When Ctrl + C is pressed
    print("Exiting loop.")

except HatError as e:
    #Issues with daqhat library
    print(f"Error:{e}")

finally:
    #Stop the scan if it was started
    hat.a_in_scan_stop()

    #Release the scan buffer
    hat.a_in_scan_cleanup()