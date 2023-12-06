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
#test
