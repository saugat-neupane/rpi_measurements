#! /usr/bin/python3
# psuedo code
import math
import numpy as np
import spidev
import time
import pandas as pd
import RPi.GPIO as GPIO

## global variables

vibX = vibY = vibZ = []

x_start_add = 0x08
status_add = 0x04
power_ctrl_add = 0x2D
range_add = 0x2C

data_ready = 16				# DRDY connected to GPIO Pin 16
# Set up SPI clock rate
# Configure spi, open bus 0, chip select 0
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0b00				# Set mode to [CPOL | CPHA] to [0 | 0]
spi.max_speed_hz = 2E6		# Set frequency to 2 MHz, will read all 9 bytes of data in 1/4 of time ADXL takes to write (1/4000 Hz)		
# Set chip select pin high, may have to use GPIO library instead of SPI library 	

## Send configuration messages
spi.writebytes([(range_add << 1) & 0xFF, 0x43])					# Write 0x43 to range register, sets interrupts to active high, and range to +- 8g

## Configure GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(data_ready, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Enable measurement mode, start global timer
spi.writebytes([(power_ctrl_add << 1) & 0xFF, 0x00])				# Write 0x00 to power control register, enables measurement mode
minutes = 1
t_end = time.time() + 60*minutes;								# Compute end time			

# Filter settings
# Data Ready Interrupt service routine
def drdy_callback():
		# Data is ready, initiate SPI read of 3 bytes per axis
		values = spi.xfer([x_start_add, 0x00, 0x00, 0x00])					# Send starting address then read 3 bytes (x axis data)
		concat_bytes = (vales[1] << 12) | (values[2] << 4) | (values[3] >> 4)
		Xval = float(!concat_bytes + 0b01)									# Take two's complement and convert to float
        #Xval = float(concat_bytes + 0b01)	
		vibX.append(Xval)

while time.time() < t_end:
	# Check data ready interrupt
	GPIO.wait_for_edge(data_ready, GPIO.rising)
	values = spi.xfer([x_start_add, 0x00, 0x00, 0x00])					# Send starting address then read 3 bytes (x axis data)
	concat_bytes = (vales[1] << 12) | (values[2] << 4) | (values[3] >> 4)
	#Xval = float(!concat_bytes + 0b01)									# Take two's complement and convert to float
    Xval = float(concat_bytes + 0b01)
	vibX.append(Xval)
	end
	# convert by combining 3 bytes into one literal
	# bit shift right by 4 bits, twos complement, then convert to float
	# Repeat at sampling interval
end

# convert Xval to numpy array and generate plot

# Send message to ADXL to go into standby mode
if(time.time() > t_end):
	spi.writebytes([(power_ctrl_add << 1) & 0xFF, 0x01])				# Write 0x00 to power control register, enables stand by mode
	spi.close()

# Save vibration data to CSV