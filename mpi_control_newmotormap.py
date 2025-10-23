from megapi import MegaPi


MBL = 2     # port for motor front right -->BACK LEFT
MFR = 3     # port for motor back left-->FRONT RIGHT
MFL = 10    # port for motor back right-->FRONT LEFT
MBR = 11    # port for motor front left-->BACK RIGHT


class MegaPiController:
    def __init__(self, port='/dev/ttyUSB0', verbose=True):
        self.port = port
        self.verbose = verbose
        if verbose:
            self.printConfiguration()
        self.bot = MegaPi()
        self.bot.start(port=port)
        self.mfr = MFR  # port for motor front right
        self.mbl = MBL  # port for motor back left
        self.mbr = MBR  # port for motor back right
        self.mfl = MFL  # port for motor front left   

    
    def printConfiguration(self):
        print('MegaPiController:')
        print("Communication Port:" + repr(self.port))
        print("Motor ports: MFR: " + repr(MFR) +
              " MBL: " + repr(MBL) + 
              " MBR: " + repr(MBR) + 
              " MFL: " + repr(MFL))


    def setFourMotors(self, vfl=0, vfr=0, vbl=0, vbr=0):
        if self.verbose:
            print("Set Motors: vfl: " + repr(int(round(vfl,0))) + 
                  " vfr: " + repr(int(round(vfr,0))) +
                  " vbl: " + repr(int(round(vbl,0))) +
                  " vbr: " + repr(int(round(vbr,0))))
        self.bot.motorRun(self.mfl,vfl)
        self.bot.motorRun(self.mfr,vfr)
        self.bot.motorRun(self.mbl,vbl)
        self.bot.motorRun(self.mbr,vbr)


    def carStop(self):
        if self.verbose:
            print("CAR STOP:")
        self.setFourMotors()


    def carStraight(self, speed):
        if self.verbose:
            print("CAR STRAIGHT:")
        self.setFourMotors(-speed, speed, -speed, speed)


    def carRotate(self, speed):
        if self.verbose:
            print("CAR ROTATE:")
        self.setFourMotors(speed, speed, speed, speed)


    def carSlide(self, speed):
        if self.verbose:
            print("CAR SLIDE:")
        self.setFourMotors(speed, speed, -speed, -speed)

    
    def carMixed(self, v_straight, v_rotate, v_slide):
        if self.verbose:
            print("CAR MIXED")
        self.setFourMotors(
            v_rotate-v_straight+v_slide,
            v_rotate+v_straight+v_slide,
            v_rotate-v_straight-v_slide,
            v_rotate+v_straight-v_slide
        )
    def motorTest():
    	# Test each motor one by one
		# Test each motor one by one
		for port in [2, 3, 10, 11]:
		    print(f"Testing motor on port {port}")
		    mpi_ctrl.bot.motorRun(port, 100)   # spin forward
		    time.sleep(2)
		    mpi_ctrl.bot.motorRun(port, 0)     # stop
		    time.sleep(1)
		#for port in [2, 3, 10, 11]:
		#print(f"Testing motor on port {port}")
		#bot.motorRun(port, 100)   # spin forward
		#time.sleep(2)
		#bot.motorRun(port, 0)     # stop
		#time.sleep(1)
####################################################
#           SENSOR BASED FUNCTIONS - begin
######################################################


    
    def close(self):
    	self.bot.close()
    	self.bot.exit()


if __name__ == "__main__":
    import time
    mpi_ctrl = MegaPiController(port='/dev/ttyUSB0', verbose=True)
    time.sleep(10)
    mpi_ctrl.carStraight(50)
    time.sleep(10)
    mpi_ctrl.carSlide(50)
    time.sleep(10)
    mpi_ctrl.carRotate(50)
    time.sleep(10)
    mpi_ctrl.carStop()

	# Read analog value from port A0 (replace A0 with correct pin)
	#mpi_ctrl.bot.analogRead(mpi_ctrl.bot.A0, ir_callback)
	

