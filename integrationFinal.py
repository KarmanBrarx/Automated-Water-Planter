#imports required to run program
import math
import spidev
import RPi.GPIO as GPIO
import time
import displayBar

irSense=1 #used to set adc channel
soilSense=2 #used to set adc channel
sleep_motor=0 #used to control how long water will flow
percent_moist=0 #display the moisture level
proximity_check=2 #arbitrary value for someone being near the IR sensor
soil_completely_dry=900
soil_completely_wet=540
GPIO.setmode(GPIO.BCM)
stepper_pins=[5,6,13,19] #pins that were used for the stepper motor and their GPIO pins

spi=spidev.SpiDev()
spi.open(0,0) # which chip enable was used for the SPI device
spi.max_speed_hz = 5000 
GPIO.setup(stepper_pins,GPIO.OUT)

# sets the sequence to turn the motor clockwise
stepper_sequence=[]
stepper_sequence.append([GPIO.HIGH, GPIO.LOW, GPIO.LOW,GPIO.LOW])
stepper_sequence.append([GPIO.LOW, GPIO.HIGH, GPIO.LOW,GPIO.LOW])
stepper_sequence.append([GPIO.LOW, GPIO.LOW, GPIO.HIGH,GPIO.LOW])
stepper_sequence.append([GPIO.LOW, GPIO.LOW, GPIO.LOW,GPIO.HIGH])

# sets the sequence to turn the motor counter clockwise
stepper_sequence_reversed=[]
stepper_sequence_reversed.append([GPIO.LOW, GPIO.LOW, GPIO.LOW,GPIO.HIGH])
stepper_sequence_reversed.append([GPIO.LOW, GPIO.LOW, GPIO.HIGH,GPIO.LOW])
stepper_sequence_reversed.append([GPIO.LOW, GPIO.HIGH, GPIO.LOW,GPIO.LOW])
stepper_sequence_reversed.append([GPIO.HIGH, GPIO.LOW, GPIO.LOW,GPIO.LOW])

#used for the 4 digit display
digits = [0,0,0,0] #initials the array for the display
#sets the paramaters to use the display
Display = displayBar.TM1637(CLK=21, DIO=20, brightness=1.0)
Display.Show(digits)

try:
        #loop to run the program infinitely to keep checcking if someone is near
        while True:
                #gets data from IR sensor converts from analog to digital then send that to the PI 
                adcIr=spi.xfer2([1,(8+irSense)<<4,0])
                data=((adcIr[1]&3)<<8) +adcIr[2]
                data_scale=(data*3.3)/float(1023)
                data_scale=round(data_scale,2) #rounds the value to a integer
                print (data_scale)
                time.sleep(1) #IR sensor check if someone is there once a second
                if data_scale >= proximity_check:
                    #gets data from soil sensor converts from analog to digital then send it to PI
                    adc=spi.xfer2([1,(8+soilSense)<<4,0])
                    soil_data=((adc[1]&3)<<8) +adc[2] #direct moisture level (540 is 100% wet, 900 is 100% dry)
                    print("Soil moisture level")
                    print(soil_data)
                     
                    #case for completely dry
                    if(soil_data >= soil_completely_dry):
                       sleep_motor=2 #sets the motor sleep time to simultate open tap
                       digits=[0,0,0,0] #displays 0% moisture

                    #case for completely wet
                    elif(soil_data<=soil_completely_wet):
                       sleep_motor=1  #sets the motor sleep time to simulate open tap
                       digits=[0,1,0,0] #displays 100% moisture

                    #case for moisture level between 1-99%
                    else:
                       sleep_motor=0.01 #sets the motor sleep time to simulate open tap
                       numerator=soil_data-540 #used to convert into a percent
                       denominator=900-540  #used to convert into a percent
                       #converts fractional value to percent
                       percent_moist=100-(round(((numerator/denominator)*100)))
                       print("printing the percentage")
                       print(percent_moist)
                       #splits the percent into single integers for array
                       right_digit=percent_moist%10
                       left_digit=math.floor(percent_moist/10)
                       digits=[0,0,left_digit,right_digit] #displays moisture level
                       
                    Display.Show(digits) #shows the resulted moisture percent
                    clockwise_turn = 1 #counter for turning the motor clockwise
                    while clockwise_turn < 100:
                          for row in stepper_sequence_reversed:
                              GPIO.output(stepper_pins,row)
                              time.sleep(0.01) #turns the stepper motor
                          clockwise_turn+=1
                    clockwise_turn = 1
                    time.sleep(sleep_motor) #how long the "tap" will stay open
                    cclockwise_turn = 1 #counter for turning the motor counter clockwise
                    while cclockwise_turn < 100:
                          for row in stepper_sequence:
                              GPIO.output(stepper_pins,row)
                              time.sleep(0.01) #turns the stepper motor
                          cclockwise_turn+=1
                    cclockwise_turn = 1
                #case if nobody is near
                else:
                     print("distance < 2: ")
                    # print(data_scale)
                     Display.Clear() #turns off display


except KeyboardInterrupt: #used to stop the program
        Display.cleanup() #tunrs off display
        pass
spi.close() #closes SPI channel
#GPIO.cleanup() #releases GPIO pins
