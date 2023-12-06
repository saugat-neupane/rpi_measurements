#! /usr/bin/python3
import math
import numpy as np
import spidev
import time
import pandas as pd
import RPi.GPIO as GPIO

## global variables
vibX = vibY = vibZ = []
# Register addresses from ADXL355 Datasheet
x_start_add = 0x08			
status_add = 0x04
power_ctrl_add = 0x2D
range_add = 0x2C
drdy_pin = 16				# DRDY connected to GPIO Pin 16

# Filter settings

# Data Ready Interrupt service routine
def drdy_callback():
	# Data is ready, initiate SPI read of 3 bytes per axis
	values = spi.xfer([x_start_add, 0x00, 0x00, 0x00])						# Send starting address then read 3 bytes (x axis data)
	concat_bytes = (vales[1] << 12) | (values[2] << 4) | (values[3] >> 4)	# combine 3 bytes into one 20-bit literal
	Xval = float(concat_bytes + 0b01)										# Take two's complement and convert to float
	vibX.append(Xval)														# Append to vibX list


if __name__ == '__main__':
	# Configure spi, open bus 0, chip select 0
	spi = spidev.SpiDev()
	spi.open(0, 0)
	spi.mode = 0b00				# Set mode to [CPOL | CPHA] to [0 | 0]
	spi.max_speed_hz = 2E6 		# Set frequency to 2 MHz, will read all 9 bytes of data in 1/4 of time ADXL takes to write (1/4000 Hz)		
	# Set chip select pin high, may have to use GPIO library instead of SPI library 	
	
	## Send configuration messages
	spi.writebytes([(range_add << 1) & 0xFF, 0x43])					# Write 0x43 to range register, sets interrupts to active high, and range to +- 8g
	
	## Configure GPIO
	GPIO.setmode(GPIO.BCM)
# Filter settings

# Data Ready Interrupt service routine
def drdy_callback():
	# Data is ready, initiate SPI read of 3 bytes pe
	GPIO.setup(drdy_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.add_event_detect(drdy_pin, GPIO.RISING, callback = drdy_callback)

	# Enable measurement mode, start global timer
	spi.writebytes([(power_ctrl_add << 1) & 0xFF, 0x00])				# Write 0x00 to power control register, enables measurement mode
	
	minutes = 1
	t_end = time.time() + 60*minutes;								# Compute end time		

	# Send message to ADXL to go into standby mode
	while true:
		if(time.time() > t_end):
			spi.writebytes([(power_ctrl_add << 1) & 0xFF, 0x01])				# Write 0x00 to power control register, enables stand by mode
			GPIO.remove_event_detect(drdy_pin)									# Disable GPIO interrupt and callback
			spi.close()
			break

# convert Xval to numpy array and generate plot
# Save vibration data to CSV
#test(ADDITIONAL CODE)

from daqhats import mcc118, OptionFlags, HatIDs, HatError
import numpy as np
import pandas as pd
import time
import spidev
import RPi.GPIO as GPIO

# Constants for MCC 118
address = 0  # Replace with your MCC 118 address
sample_rate = 20000  # 20 kS/s
duration = 20  # Duration in seconds for which to measure
samples_per_channel = sample_rate * duration  # Total samples per channel
channels = [0, 1, 2, 3]  # Channels connected to the accelerometer and temperature sensor
channel_names = ['X Voltage', 'Y Voltage', 'Z Voltage', 'Temp Voltage']  # Channel headings

# Constants for ADXL355
x_start_add = 0x08
status_add = 0x04
power_ctrl_add = 0x2D
range_add = 0x2C
drdy_pin = 16  # DRDY connected to GPIO Pin 16

# Initialize lists to store vibration data
vibX = []  # List to store X-axis vibration data

# Create an instance of the MCC 118 HAT device at the specified address
hat = mcc118(address)

# Configure scan options for MCC 118
options = OptionFlags.CONTINUOUS

# Buffer for MCC 118 data
buffer = []

# Configure SPI for ADXL355
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0b00
spi.max_speed_hz = 2E6

# Configure GPIO for ADXL355
GPIO.setmode(GPIO.BCM)
GPIO.setup(drdy_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Data Ready Interrupt service routine for ADXL355
def drdy_callback():
    values = spi.xfer([x_start_add, 0x00, 0x00, 0x00])
    concat_bytes = (values[1] << 12) | (values[2] << 4) | (values[3] >> 4)
    Xval = float(concat_bytes + 0b01)
    vibX.append(Xval)

# Start the scan for MCC 118
hat.a_in_scan_start(channels, samples_per_channel, sample_rate, options)

# Record the start time
start_time = time.time()

# Read and display the accelerometer and temperature values
try:
    while (time.time() - start_time) < duration:
        # Check if the desired duration has passed for MCC 118
        current_readings = hat.a_in_scan_read(samples_per_channel, 0)
        buffer.extend(current_readings.data)
        
        # Check if data is ready for ADXL355
        if GPIO.input(drdy_pin):
            drdy_callback()

    # Trim the buffer to include only complete sets of channel data for MCC 118
    complete_sets = len(buffer) // len(channels)
    trimmed_buffer = buffer[:complete_sets * len(channels)]

    # Create a DataFrame to hold the data for MCC 118
    df_mcc118 = pd.DataFrame(np.array(trimmed_buffer).reshape(-1, len(channels)), columns=channel_names)

    # Conversion from voltage to standard m/s^2 for MCC 118
    conv2std = 1000/400*9.80665  # 400 for 2g range, 100 for 8g range
    df_mcc118['Z Vib'] = (df_mcc118['Z Voltage'] - 0.9) * conv2std
    df_mcc118['Y Vib'] = (df_mcc118['Y Voltage'] - 0.9) * conv2std
    df_mcc118['X Vib'] = (df_mcc118['X Voltage'] - 0.9) * conv2std
    df_mcc118['Temp'] = (df_mcc118['Temp Voltage'] * 1000 - 967) / 3 + 25.0

    # Save the DataFrame with the converted values to a CSV file for MCC 118
    df_mcc118.to_csv('mcc118_data_converted.csv', index=False)

    # Convert ADXL355 data to numpy array and save to CSV
    df_adxl355 = pd.DataFrame({'X Vib': np.array(vibX)})
    df_adxl355.to_csv('adxl355_data.csv', index=False)

except KeyboardInterrupt:
    # User pressed CTRL+C to exit
    print("Exiting loop.")

except HatError as e:
    # Handle any DAQ HAT library errors.
    print(f"Error: {e}")

finally:
    # Stop the scan if it was started for MCC 118
    hat.a_in_scan_stop()
    # Release the scan buffer for MCC 118
    hat.a_in_scan_cleanup()
    # Disable GPIO interrupt and callback for ADXL355
    GPIO.remove_event_detect(drdy_pin)
    # Close SPI for ADXL355
    spi.close()

