#imports required to run program
import math
import spidev
import RPi.GPIO as GPIO
import time

def converting_to_percentage(soil_data_value):
	soil_completely_dry=900
	soil_completely_wet=540
	percent_value = 100
	#case for completely dry
	if(soil_data_value >= soil_completely_dry):
		print("Its completely dry!")
		percent_value = 0
	
	#case for completely wet
	elif(soil_data<=soil_completely_wet):
		print("Its completely wet!")
	
	#case for moisture level between 1-99%
	else:
		print("Its somewhat moist")
		numerator=soil_data-soil_completely_wet #used to convert into a percent
		denominator=soil_completely_dry-soil_completely_wet  #used to convert into a percent
		#converts fractional value to percent
		percent_moist=100-(round(((numerator/denominator)*100)))
		percent_value = percent_moist

	print("Percent Value is: " + str(percent_value))

soilSense=2 #used to set adc channel

percent_moist=0 #display the moisture level


GPIO.setmode(GPIO.BCM)

spi=spidev.SpiDev()
spi.open(0,0) # which chip enable was used for the SPI device
spi.max_speed_hz = 5000

try:

		while True:
		
			#gets data from soil sensor converts from analog to digital$
			adc=spi.xfer2([1,(8+soilSense)<<4,0])
			soil_data=((adc[1]&3)<<8) +adc[2] #direct moisture level (5$
			print("Soil Data")
			print(soil_data)
			converting_to_percentage(soil_data)
			
			time.sleep(1) #IR sensor check if someone is there once a second
			
except KeyboardInterrupt: #used to stop the program
		pass
spi.close() #closes SPI channel
#GPIO.cleanup() #releases GPIO pins
