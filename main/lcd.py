import wiringpi2 as wp
reg = 0x70


def init():
	fd = wp.wiringPiI2CSetup(0x38)
	type = False

	if(fd==3):
		print "I2C device initialized \n"
	wp.delay(110)

	writeByte = 0x30 # 1100 0000

	LCD8bit(writeByte, type, fd)
	wp.delay(5)  

	LCD8bit(writeByte, type, fd) 
	wp.delayMicroseconds(110)

	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(50)

	writeByte = 0x20 #0100 0000

	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(50)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(50)

	writeByte = 0x80                # sets up device to 2 lines5x7 pixel chars, 1/8 duty cycle
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)
	#============================= can switch to 4 bit
	writeByte = 0x00          # display on, cursor on (blink)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0xF0
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)
	writeByte = 0x40
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x00          # display on, cursor on (blink)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delay(5)

	writeByte = 0x40
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)  

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x00          # display on, cursor on (blink)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delay(5)
		
	return fd
	
	
def LCD8bit(writeByte, type, fd):	
	writeByte = writeByte>>4#clear the lower nibble since it isn't used
	writeByte = writeByte<<4
	if(type):
		value = 4 #set bit 2
		writeByte = writeByte|value# set CD to 1 for data (bit2)

	  #=====================================================write
	wp.wiringPiI2CWriteReg8(fd, reg, writeByte)

	wp.delayMicroseconds(10)

	value = 8
	writeByte = writeByte|value #pulse enable pin (bit3)
	wp.wiringPiI2CWriteReg8(fd, reg, writeByte)

	wp.delayMicroseconds(10)

	writeByte = writeByte^value#clear enable pin	
	wp.wiringPiI2CWriteReg8(fd, reg, writeByte)

	wp.delayMicroseconds(10)
	return
#===================================write a string to the lcd display========================
def writeString(word, fd):
	for i in word:
		write(ord(i), True, fd)
	return

	
#===================================write to LCD in 4 bit mode========================
# Receives an 8 bit LCD command and a type (type=false for a command and true for data)
def write(writeByte, type, fd):

	#===============================extract upper nibble
	value = writeByte
	#clear the lower nibble
	value = value>>4
	value = value<<4
	#place in register
	upperNibble = value
	#==================================extract lower nibble
	value = writeByte
	#move the lower nibble to the upper nibble
	value = value<<4
	#place in register
	lowerNibble = value


	if(type):
		value = 4 #set bit 2
		upperNibble = upperNibble|value# set CD to 1 for data (bit2)
		lowerNibble = lowerNibble|value
	#else CD is 0 for a command



	#=====================================================write upperNibble
	wp.wiringPiI2CWriteReg8(fd, reg, upperNibble)

	wp.delayMicroseconds(10)

	value = 8
	upperNibble = upperNibble|value #pulse enable pin (bit3)
	wp.wiringPiI2CWriteReg8(fd, reg, upperNibble)

	wp.delayMicroseconds(10)

	upperNibble = upperNibble^value#clear enable pin

	wp.wiringPiI2CWriteReg8(fd, reg, upperNibble)

	wp.delayMicroseconds(10)
	#=====================================================write lowerNibble
	wp.wiringPiI2CWriteReg8(fd, reg, lowerNibble)

	wp.delayMicroseconds(10)

	value = 8
	lowerNibble = lowerNibble|value #pulse enable pin (bit3)
	wp.wiringPiI2CWriteReg8(fd, reg, lowerNibble)

	wp.delayMicroseconds(10)

	lowerNibble = lowerNibble^value#clear enable pin	
	wp.wiringPiI2CWriteReg8(fd, reg, lowerNibble)

	wp.delayMicroseconds(10)

	return

	
def clear(fd):
	type = False
	writeByte = 0x00          # display on, cursor on (blink)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delay(5)
	return
	
def reset(fd):
	type = False
	
	writeByte = 0x30 # 1100 0000

	LCD8bit(writeByte, type, fd)
	wp.delay(5)  

	LCD8bit(writeByte, type, fd) 
	wp.delayMicroseconds(110)

	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(50)

	writeByte = 0x20 #0100 0000

	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(50)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(50)

	writeByte = 0x80                # sets up device to 2 lines5x7 pixel chars, 1/8 duty cycle
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)
	#============================= can switch to 4 bit
	writeByte = 0x00          # display on, cursor on (blink)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0xF0
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)
	writeByte = 0x40
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x00          # display on, cursor on (blink)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delay(5)

	writeByte = 0x40
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)  

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x00          # display on, cursor on (blink)
	LCD8bit(writeByte, type, fd)
	wp.delayMicroseconds(100)

	writeByte = 0x10
	LCD8bit(writeByte, type, fd)
	wp.delay(5)
		
	return
