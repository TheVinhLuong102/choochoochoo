# Imports ---------------------------------------------------------------------

import sys
import vex
from vex import *
import math

# Robot Class -----------------------------------------------------------------

class Robot:

    x = 0 # x coordinate
    y = 0 # y coordinate
    angle = 0 # current angle of the robot

    # object instantiation
    def __init__(self,dt,turn,speed):

        self.drivetrain = dt #sets the drivetrain variable
        self.turnSpeed = turn
        self.movementSpeed = speed

    # move the robot to an x coord, y coord and angle of rotation
    def moveToXYA(self,x,y,angle = None): 

        self.currentX = self.x #grabs current x coordinate
        self.currentY = self.y #grabs current y coordinate

        self.deltaX = float(math.fabs(x - self.currentX)) #calulates distance between two x coordinates
        self.deltaY = float(math.fabs(y - self.currentY)) #calulates distance between two y coordinates

        if self.deltaX == 0 and self.deltaY != 0: #if the robot is only moving in the y axis
            if self.currentY > y: #if the movement is negative
                self.rotateTo(180) #rotate the robot to 180 degrees
            else: #if the movement is positive
                self.rotateTo(0) #rotate the robot to 0 degrees
        elif self.deltaX != 0 and self.deltaY == 0: #if the robot is only moving in the x axis
            if self.currentX > x: # if the movement is negative
                self.rotateTo(-90) #rotate the robot to -90 degrees
            else: #if the movmeent is postiive
                self.rotateTo(90) # rotate the robot to 90 degrees
        else: #if there is movmeent in the x and y axis'
            if x > self.currentX and y > self.currentY: #if the robot is moving into the first quadrant
                self.rotation = math.degrees(math.atan(self.deltaX / self.deltaY)) #calculate the amount of rotation relative to 0
                self.rotateTo(self.rotation) #rotate to this newly calculated angle
            elif x > self.currentX and y < self.currentY: #if the robot is moving into the second quadrant
                self.rotation = 180 - math.degrees(math.atan(self.deltaX / self.deltaY)) #calculate the amount of rotation relative to 0
                self.rotateTo(self.rotation) #rotate to this newly calculated angle
            elif x < self.currentX and y > self.currentY: #if the robot is moving into the fourth quadrant
                self.rotation = math.degrees(math.atan(self.deltaX / self.deltaY)) * -1 #calculate the amount of rotation relative to 0
                self.rotateTo(self.rotation) #rotate to this newly calculated angle
            elif x < self.currentX and y < self.currentY: #if the robot is moving into the third quadrant
                self.rotation = math.degrees(math.atan(self.deltaX / self.deltaY)) - 180 #calculate the amount of rotation relative to 0
                self.rotateTo(self.rotation) #rotate to this newly calculated angle

        self.distance = self.calculateDeltaD(x,y,self.currentX,self.currentY) # calculate the absolute value between the two coordinates
        self.motion = self.moveBy(self.distance) #move by the newly found distance, and specifiying the ignoreCone parmater with a variable

        if self.motion == False: #if the robot was unable to complete its journey
            self.drivetrain.stop(vex.BrakeType.HOLD)
            return False #return that journey was unsuccessful
        else: #otherwsie,
            self.x = x #set new x coordinate
            self.y = y #set new y coordinate
            if angle != None: # if an end rotation angle was specified
                self.rotateTo(angle) #rotate to the specified angle
            self.drivetrain.stop(vex.BrakeType.HOLD)
            return True #return that journey was successful

    # move the robot forwards by a certain distance
    def moveBy(self,distance): 

        self.currentAngle = self.angle #gets current gyro reading

        if distance >= 0:
             dt.drive_for(vex.DirectionType.FWD,distance,vex.DistanceUnits.CM,self.movementSpeed,vex.VelocityUnits.PCT)
        else:
            dt.drive_for(vex.DirectionType.REV,distance*-1,vex.DistanceUnits.CM,self.movementSpeed,vex.VelocityUnits.PCT)

        self.resolveResult = self.resolveXY(self.x,self.y,distance,self.currentAngle)
        self.x , self.y = self.resolveResult.x , self.resolveResult.y

        self.drivetrain.stop(vex.BrakeType.HOLD)
        return True #robot has been able to reach destination

    # rotate the robot to a certain angle
    def rotateTo(self,degrees): 

        if degrees < -180 or degrees > 180:
            return False #invalid goal angle
        else:
            self.currentAngle = self.angle #grabs the current angle of the robot
            self.goalAngle = round(degrees) #sets the goal degrees to a new variable

            if self.currentAngle < 0 and self.goalAngle == 180: #couteract 180/-180 clash
                self.goalAngle = -180
            elif self.currentAngle > 0 and self.goalAngle == -180:
                self.goalAngle = 180
            elif self.currentAngle == 180 and self.goalAngle < 0:
                self.currentAngle = -180
            elif self.currentAngle == -180 and self.goalAngle > 0:
                self.currentAngle = 180

            self.deltaR = self.goalAngle - self.currentAngle #calculates how far the robot needs to rotate

            #changes the deltaR value to the desired value (avoids 180/-180 cutoff)
            if self.deltaR > 180:
                self.deltaR = (self.deltaR - 360)
            elif self.deltaR < -180:
                self.deltaR = (self.deltaR + 360)

            if self.deltaR >= 0: #turn the robot
                self.drivetrain.turn_for(vex.TurnType.RIGHT,self.deltaR,vex.RotationUnits.DEG,self.turnSpeed,vex.VelocityUnits.PCT)
            else:
                self.drivetrain.turn_for(vex.TurnType.LEFT,self.deltaR*-1,vex.RotationUnits.DEG,self.turnSpeed,vex.VelocityUnits.PCT)

            self.angle = self.goalAngle #set new angle

            self.drivetrain.stop(vex.BrakeType.HOLD)
            return True

    # function to update distaplacement of the robot by calculating new coordinates
    def resolveXY(self,xCoord,yCoord,distance,rotation): 

        self.distance = distance

        self.radians = math.radians(rotation) #turns the gyro reading into radians

        self.gyro = rotation #keeps the gyro reading in degrees

        self.coordinates = XYCoordinates() #makes a new set of coordinates

        self.ninety = math.radians(90)

        if self.gyro == 0:
            self.coordinates.x = xCoord
            self.coordinates.y = yCoord + self.distance
        elif self.gyro == 180 or self.gyro == -180:
            self.coordinates.x = xCoord
            self.coordinates.y = yCoord - self.distance
        elif self.gyro == 90:
            self.coordinates.x = xCoord + self.distance
            self.coordinates.y = yCoord
        elif self.gyro == -90:
            self.coordinates.x = xCoord - self.distance
            self.coordinates.y = yCoord
        else:
            if self.gyro > 0 and self.gyro < 90: #first quadrant
                self.coordinates.x = xCoord + (math.sin(self.radians) * self.distance)
                self.coordinates.y = yCoord + (math.cos(self.radians) * self.distance)
            elif self.gyro > 0 and self.gyro > 90: #second quadrant
                self.coordinates.x = xCoord + (math.cos(self.radians - self.ninety) * self.distance)
                self.coordinates.y = yCoord - (math.sin(self.radians - self.ninety) * self.distance)
            elif self.gyro < 0 and self.gyro > -90: #fourth quadrant
                self.coordinates.x = xCoord - (math.sin(math.fabs(self.radians)) * self.distance)
                self.coordinates.y = yCoord + (math.cos(math.fabs(self.radians)) * self.distance)
            elif self.gyro < 0 and self.gyro < -90: #third quadrant
                self.coordinates.x = xCoord - (math.cos(math.fabs(self.radians + self.ninety)) * self.distance)
                self.coordinates.y = yCoord - (math.sin(math.fabs(self.radians + self.ninety)) * self.distance)

        self.coordinates.x = round(self.coordinates.x) #create new coordinates
        self.coordinates.y = round(self.coordinates.y)

        return self.coordinates #return values

    # function to return distance between two coordinates
    def calculateDeltaD(self,goalX,goalY,currentX,currentY): #function to return distance between two coordinates
        self.deltaX = math.fabs(currentX - goalX) #caclulates change in x axis
        self.deltaY = math.fabs(currentY - goalY) #caclulates change in y axis
        self.deltaD = math.fabs(math.sqrt((self.deltaX ** 2) + (self.deltaY ** 2))) # performs pythagoras on two values
        return self.deltaD #returns absolute value

# Coordinates Class -----------------------------------------------------------

class XYCoordinates:
    def __init__(self): #intiation function
        self.x = 0 #x coordinate
        self.y = 0 #y coordinate
        return None

# Functions & Variables -------------------------------------------------------

flywheelStatus = False
intakeStatus = False
column = 35

#halts the motors dependent on certain rules
def haltMotors(flywheel,inatake):
    leftMotor.stop(vex.BrakeType.BRAKE)
    rightMotor.stop(vex.BrakeType.BRAKE)
    twoBar.stop(vex.BrakeType.HOLD)
    if flywheel = False:
        flywheelOne.stop(vex.BrakeType.COAST)
        flywheelTwo.stop(vex.BrakeType.COAST)
    if intake == False:
        intake.stop(vex.BrakeType.COAST)
    return True

#moves the robot forwards
def moveForwards(time,power):
    #time measured in milliseconds, power measured in 0-100 percentage
    newPower = math.fabs(power)
    dt.drive(vex.DirectionType.FWD,newPower,vex.VelocityUnits.PCT)
    sys.sleep(time)

#moves the robot backwards
def moveBackwards(time,power):
    #time measured in milliseconds, power measured in 0-100 percentage
    newPower = math.fabs(power)
    dt.drive(vex.DirectionType.REV,newPower,vex.VelocityUnits.PCT)
    sys.sleep(time)

#turns the robot left
def turnLeft(time,power):
    #time measured in milliseconds, power measured in 0-100 percentage
    newPower = math.fabs(power) / 3
    dt.turn(vex.TurnType.LEFT,newPower,vex.VelocityUnits.PCT)
    sys.sleep(time)

#turns the robot right
def turnRight(time,power):
    #time measured in milliseconds, power measured in 0-100 percentage
    newPower = math.fabs(power) / 3
    dt.turn(vex.TurnType.RIGHT,newPower,vex.VelocityUnits.PCT)
    sys.sleep(time)

#turns the flywheel on
def turnFlywheelOn(delayStartup = True):
    flywheelOne.spin(vex.DirectionType.FWD,100,vex.VelocityUnits.PCT)
    flywheelTwo.spin(vex.DirectionType.FWD,100,vex.VelocityUnits.PCT)
    if delayStartup == True:
        while(flywheelOne.velocity(vex.VelocityUnits.PCT) < 95): #hold the return of the function
            continue
    return True

#turns the flywheel off
def turnFlywheelOff():
    return False

#turn the intake on
def turnIntakeOn():
    intake.spin(vex.DirectionType.REV,100,vex.VelocityUnits.PCT)
    return True

#turn the intake off
def turnIntakeOff():
    intake.stop(vex.BrakeType.COAST)
    return False

#move the arm up
def moveArmUp(time,power):
    #time measured in milliseconds, power measured in 0-100 percentage
    newPower = math.fabs(power)
    twoBar.spin(vex.DirectionType.FWD,100,vex.VelocityUnits.PCT)
    sys.sleep(time)

#move the arm down
def moveArmDown(time,power):
    #time measured in milliseconds, power measured in 0-100 percentage
    newPower = math.fabs(power)
    twoBar.spin(vex.DirectionType.REV,100,vex.VelocityUnits.PCT)
    sys.sleep(time)

#shoot a ball
def fireABall():
    flywheelStatus = turnFlywheelOn()
    loader.spin(vex.DirectionType.FWD,100,vex.VelocityUnits.PCT)
    while(flywheelOne.velocity(vex.VelocityUnits.PCT) > 90):
        continue
    loader.stop(vex.BrakeType.COAST)
    return True

#check the loader for a ball
def checkLoader():
    if sonar.distance(vex.DistanceUnits.IN) < 2 and sonar.distance(vex.DistanceUnits.IN) > 0:
        loader.stop(vex.BrakeType.COAST)
        flywheelStatus = turnFlywheelOn(False)
    else:
        flywheelStatus = turnFlywheelOff()
        loader.spin(vex.DirectionType.FWD,30,vex.VelocityUnits.PCT)
    return False


# Robot Setup -----------------------------------------------------------------

wheelTravel = 310 # circumference of the wheel (mm)
trackWidth = 370 # width of the chassis (mm)
turnSpeed = 20 # how fast the robot will turn (%)
movementSpeed = 35 # how fast the robot will go forwards and back (%)

brain       = vex.Brain()
controller  = vex.Controller(vex.ControllerType.PRIMARY)

twoBar      = vex.Motor(vex.Ports.PORT1 , vex.GearSetting.RATIO18_1, False)
leftMotor   = vex.Motor(vex.Ports.PORT14, vex.GearSetting.RATIO18_1, False) 
rightMotor  = vex.Motor(vex.Ports.PORT15, vex.GearSetting.RATIO18_1, True) 
flywheelOne = vex.Motor(vex.Ports.PORT9 , vex.GearSetting.RATIO18_1, True) 
flywheelTwo = vex.Motor(vex.Ports.PORT10, vex.GearSetting.RATIO18_1, False) 
intake      = vex.Motor(vex.Ports.PORT16, vex.GearSetting.RATIO18_1, False)
loader      = vex.Motor(vex.Ports.PORT11, vex.GearSetting.RATIO18_1, False)

sonar       = vex.Sonar(brain.three_wire_port.c)
dt          = vex.Drivetrain(leftMotor, rightMotor, wheelTravel, trackWidth, vex.DistanceUnits.MM)

robot = Robot(dt,turnSpeed,movementSpeed) #create the robot class
competition = vex.Competition()

# Main program ----------------------------------------------------------------
    
def pre_auton():
    # All activities that occur before competition start
    # Example: setting initial positions
    pass

def autonomous():
    # Place autonomous code here
    pass

def drivercontrol():
    while True:
        checkLoader()
        if thing:

        else:
            haltMotors(flywheelStatus,intakeStatus)
        

# Set up (but don't start) callbacks for autonomous and driver control periods.
competition.autonomous(autonomous)
competition.drivercontrol(drivercontrol)

# Run the pre-autonomous function.
pre_auton()

# Robot Mesh Studio runtime continues to run until all threads and
# competition callbacks are finished.