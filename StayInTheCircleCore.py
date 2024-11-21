#Made by David Schriver October 2024 - 
import TrigJacknife
import math
import datetime
import random


ArenaWidth = 500
ArenaHeight = 500
ArenaBounds = TrigJacknife.Rectangle(0,0,ArenaWidth,ArenaHeight)
SNDBump = "assets/snd/bounce1.wav"
SNDBump2 = "assets/snd/bounce2.wav"
SNDWrap = "assets/snd/phase.wav"
SNDSpeedUp = "PowerUp"
SNDSpeedDown = "PowerDown"
SndShrink = "Shrink"
SndVictory = "assets/snd/win2.wav"
SndDrill = "assets/snd/drill2.wav"
SndDie = "assets/snd/die.wav"

class Player:
    def __init__(self,x,y) -> None:
        self.corePoint = TrigJacknife.Point(x,y)
        self.lastPoint = TrigJacknife.Point(x,y) #Location 1 frame ago
        self.speed = 10

        #Stores player input
        self.UP = False
        self.DOWN = False
        self.LEFT = False
        self.RIGHT = False
        
        self.facing = "" #Stores the last direction the player tried to move in.
        self.radius = 20
        self.endMode = False #If this is true the player moves quickly in a direction that isn't diagonal
        

    def getNine(self):
        return TrigJacknife.NinePoints(self.corePoint,ArenaBounds)
    
    def getFacing(self):
        toSend = ""
        if (self.LEFT): toSend =  "l"
        if (self.RIGHT): toSend = "r"
        if (self.UP): toSend = "u"
        if (self.DOWN): toSend = "d"
        return toSend
        
    
    #Switches to end mode
    def EndMode(self):
        self.speed *= 2
        self.endMode = True

        #Make sure it's going in a direction
        if (self.UP == False and self.DOWN == False and self.LEFT == False and self.RIGHT == False):
            self.UP = True

    #Receieves input, ultimately from the player.
    def InputUp(self):
        self.UP = True
        self.DOWN = False

        #In end mode you cannot move diagonally or stop
        if (self.endMode):
            self.LEFT = self.RIGHT = False
      
    
    def InputDown(self):
        self.UP = False
        self.DOWN = True
        if (self.endMode):
            self.LEFT = self.RIGHT = False
        

    def InputLeft(self):
        self.LEFT = True
        self.RIGHT = False
        if (self.endMode):
            self.UP = self.DOWN = False

    def InputRight(self):
        self.RIGHT = True
        self.LEFT = False
        if (self.endMode):
            self.UP = self.DOWN = False

    #Whether or not the player moved the last frame.
    def PlayerMoved(self):
        return self.corePoint.x != self.lastPoint.x or self.corePoint.y != self.lastPoint.y



    def crank(self):
        self.lastPoint = TrigJacknife.Point(self.corePoint.x,self.corePoint.y)
        multiplier = 1
        #If the player is moving diagonally, slow them down a bit
        if (self.RIGHT == True or self.LEFT == True) and (self.UP == True or self.DOWN == True): multiplier = 0.7

        if (self.RIGHT): self.corePoint.x = self.corePoint.x  + self.speed * multiplier
        if (self.LEFT): self.corePoint.x = self.corePoint.x  - self.speed * multiplier
        if (self.UP): self.corePoint.y = self.corePoint.y  - self.speed * multiplier
        if (self.DOWN): self.corePoint.y = self.corePoint.y  + self.speed * multiplier

        #Make the player go out the other side if they leave the screen.
        ArenaBounds.wrapPoint(self.corePoint,0)

        self.facing = self.getFacing()

        #Purge inputs after processing during regular play.
        if (self.endMode == False):
            self.RIGHT = self.LEFT = self.UP = self.DOWN = False
        


class Circle:
    def __init__(self,x,y) -> None:
        self.corePoint = TrigJacknife.Point(x,y)
        self.radius = 80
        self.speed = 6
        self.speedMax = 6 #If the speed is under this the game will automatically try to approach this, same with radius min.
        self.radiusMin = 80
        self.speedMaxTrue = 10
        self.radiusMinTrue = 60
        self.going = TrigJacknife.shoot(30 * (math.pi/180),self.speed)
        self.lastScore = 0
        self.phasePlayed = False #Used to ensure the sound effect is only played once if the circle wraps around the other side of the arena
        
        self.mode = 0
        #0 = Bounces off walls (regular behaviour)
        #1 = Wraps around to other side until it touches the middle. \
        #2 = Speed up 
        #3 = Shrink
        #4 = Randomly stop.
        #5 = Randomly change directions (Does not need a mode) 

        self.mode1Pt2 = False #Toggles when the circle wraps. When True sets mode to 0 after the circle clears the edge
        self.mode23Counter = TrigJacknife.Point(5,5)
        self.mode23Pt2 = False #When true: the platform slows back down
        self.mode5Tickdown = TrigJacknife.Point(10,10) #Stays still until x = 0
        
        self.modeGrace = 0 #Once the score hits this, the mode will start switching
        self.modeTickdown = 0
        self.modeTickdownRange = (60,120) #When it switches back to mode 0 modeTickdown is set to a random number based on this.
        self.modeTickdown = random.randrange(self.modeTickdownRange[0] - 1,self.modeTickdownRange[1] + 1)
        self.bump1 = True #Toggles between true and false to alternate the sound that plays when the circle hits the wall.
        
        self.knockMomentum = TrigJacknife.Point(0,50) #Speed will have x * knockStep added to it if accesed through get AugSpeed
        self.knockStep = 0.5
        self.playerHasWon = False #When set to true the circle will either shrink or speed up every time score % harderEvery is equal to 0 
        self.harderEvery = 10

        
    #Gets 8 parallel points for rendering purposes to create the illusion of leaving the side of the screen and coming out the other side
    def getNine(self):
        return TrigJacknife.NinePoints(self.corePoint,ArenaBounds)
    
    #Returns the speed + the momentum from getting hit by the player in end mode.
    def getAugSpeed(self):
        return self.speed + (self.knockMomentum.x * self.knockStep)
    
    #On contact with the player: bounces away
    def knock(self,knockPoint):
        self.knockMomentum.x = self.knockMomentum.y
        self.going = TrigJacknife.chase(knockPoint, self.corePoint,self.getAugSpeed())
    
    #Used to update the trajectory of the circle, specifically when the speed canges 
    def UpdateGoing(self):
        self.going = TrigJacknife.shoot(TrigJacknife.pointToAngle(self.going) + math.pi,self.getAugSpeed())

    #Randomly changes dirction
    def RandDirection(self):
        self.speed = 4
        self.going = TrigJacknife.shoot(random.random() * (180 * ((math.pi/180))),self.getAugSpeed())
        if (random.random() < 0.5):
            self.going.x = self.going.x * -1
            self.going.y = self.going.y * -1

    def BackToMode0 (self):
        self.mode = 0
        self.phasePlayed = False
        
    
    #Switches to a random mode or randomly chances direction
    def RandomMode(self):
        dice = random.random()
        if (dice < 0.25):
            self.mode = 1
        elif (dice < 0.5):
            self.mode = random.randrange(2,4)
            
        else:
            self.RandDirection()
            
        #And resets the timer
        self.modeTickdown = random.randrange(self.modeTickdownRange[0] - 1,self.modeTickdownRange[1] + 1)
      

    def crank (self, score):
        #This is used to relay the sound effect to be played
        toSend = ""

        #Slowly approach max speed and minimum radius
        if (score != self.lastScore and (self.speed < self.speedMax or self.radius > self.radiusMin)):
            if (self.speed < self.speedMax): 
                self.speed += 1
                self.going = TrigJacknife.shoot(TrigJacknife.pointToAngle(self.going) + math.pi,self.speed)
            if (self.radius > self.radiusMin): self.radius -= 2

        
        #After a time switch the mode
        if ( self.mode == 0):
            self.modeTickdown = self.modeTickdown - 1
            if (self.modeTickdown == 0):
                self.RandomMode()

        #Get harder after the player has won
        if (score != self.lastScore and self.playerHasWon == True and score % self.harderEvery == 0):
            dice = random.random()

            if self.speedMax == self.speedMaxTrue: dice = 1
            if self.radiusMin == self.radiusMinTrue: dice = 0

            if (dice > 0.5 and self.speedMax < self.speedMaxTrue):
                self.speedMax += 1
                
            elif (self.radiusMin > self.radiusMinTrue):
                self.radiusMin = self.radiusMin - 5
                

            
            


        #If the player hits the circle in end mode, ease down gradually
        if self.knockMomentum.x > 0: 
            self.knockMomentum.x = self.knockMomentum.x - 1 
            self.UpdateGoing()

        #Move the circle unless instructed to stop suddenly
        if (self.mode != 5):
            self.corePoint.x = self.corePoint.x + self.going.x
            self.corePoint.y = self.corePoint.y + self.going.y
        else:
            self.mode5Tickdown.x = self.mode5Tickdown.x - 1
            if self.mode5Tickdown.x <= 0:
                self.BackToMode0()
                self.mode5Tickdown.x = self.mode5Tickdown.y

        #Restrain and flip the going point

        if (self.mode != 1):
            #Bounce as usual
            bump = ArenaBounds.containPoint(self.corePoint,self.radius)

            #Share sound effect
            if (bump != "" and self.bump1):
                toSend = SNDBump
                self.bump1 = False
            elif (bump != ""):
                toSend = SNDBump2
                self.bump1 = True

            #Flip X or Y on going if it hits the "wall"
            if (bump.find("l") != -1 or bump.find("r") != -1): self.going.x = self.going.x * -1
            if (bump.find("u") != -1 or bump.find("d") != -1): self.going.y = self.going.y * -1
        else:
            #Goes out the other side of the screen
            wrap = ArenaBounds.wrapPoint(self.corePoint,0)

            #Play the sound when it starts to phase.
            if (self.phasePlayed == False and ArenaBounds.containPointNoTouch(self.corePoint,self.radius) != ""):
                    self.phasePlayed = True
                    #Uncomment line below to have the game play a sound when the circle starts to wrap around the other side.
                    #toSend = SNDWrap
            
            if (wrap != ""):
                self.mode1Pt2 = True
               

            #It's mode 1 phase 2 and the circle has cleared the edge of the screen, change back to mode 0
            if (self.mode1Pt2 == True and ArenaBounds.containPointNoTouch(self.corePoint,self.radius) == ""):
                self.mode1Pt2 = False
                self.BackToMode0()

        #The circle goes faster with every bump
        if (self.mode == 2):
            if bump != "":
                if (self.mode23Counter.x > 0 and self.mode23Pt2 == False):#Speed up when hitting the side of the arena
                    self.mode23Counter.x = self.mode23Counter.x -1
                    
                    self.speed = self.speed + 0.75
                    self.UpdateGoing()
                    if (self.mode23Counter.x <= 0): self.mode23Pt2 = True
                elif (self.mode23Pt2 == True):#Slow down when hitting the side of the arena
                    self.mode23Counter.x = self.mode23Counter.x + 1
                    self.speed = self.speed - 0.75
                    self.UpdateGoing()
                    
                    if (self.mode23Counter.x >= self.mode23Counter.y): #Back to normal, return to normal mode.
                        self.mode23Pt2 = False
                        self.BackToMode0()

        if (self.mode == 3):
            if bump != "":
                if (self.mode23Counter.x > 0 and self.mode23Pt2 == False):#Shrink when hitting the side of the arena
                    self.mode23Counter.x = self.mode23Counter.x -1
                    
                    self.radius = self.radius - 7
                    
                    if (self.mode23Counter.x <= 0): self.mode23Pt2 = True
                elif (self.mode23Pt2 == True):#Grow when hitting the side of the arena
                    self.mode23Counter.x = self.mode23Counter.x + 1
                    self.radius = self.radius  + 7
                    
                    
                    if (self.mode23Counter.x >= self.mode23Counter.y): #Back to normal, return to normal mode.
                        self.mode23Pt2 = False
                        self.BackToMode0()
                        

        
            



        


        self.lastScore = score
        return toSend
        


class StayInTheCircleCore:
    def __init__(self) -> None:
        
        self.UP = False
        self.DOWN = False
        self.LEFT = False
        self.RIGHT = False
        self.player = Player(ArenaWidth/2,ArenaHeight/2)
        self.circle = Circle(ArenaWidth/2,ArenaHeight/2)
        self.countdown = 4 #Countdown before game starts
        self.playerMoved = False
      
        self.grace = TrigJacknife.Point(3,3) #To compensate for the brief amount of time the player loses contact during mode 1.
        self.score = 0
        self.scoreCountdown = TrigJacknife.Point(30,30) #How many frames to wait before increasing the score
        self.scoreCheck = datetime.datetime.now()
        self.gameOn = True #If this is 
        self.playerWon = False 
        self.scoreToWin = 60 #The score at which the game is considered a win
        self.endPause = TrigJacknife.Point(0,30) #Keeps the player from moving while x is 0
        self.lostDuringMode1 = False

        

        

        

    #Returns true if the game is still running
    def GameOn(self):
        return self.UP == False and self.DOWN == False

    #Is the player in the circle or 8 mirror circles (important for wrap mode).
    def InCircle(self):
        nineCircles = TrigJacknife.NinePoints(self.circle.corePoint,ArenaBounds)
        for leCircle in nineCircles:
            if (leCircle.distanceTo(self.player.corePoint) <= self.circle.radius + self.player.radius/2): return True

        return False
    
    #Returns false if grace.x is 0. Grace.x ticks down every frame that the player is not in the circle and resets when the player is.
    def InCircleGrace(self):
        if self.grace.x <= 0: return False
        return True

    #Relays input from the presentation layer to the player object.
    def InputUp(self):
        if (self.endPause.x == 0 and (self.gameOn == True or self.playerWon == True)):
            self.player.InputUp()
            
    
    def InputDown(self):
        if (self.endPause.x == 0 and (self.gameOn == True or self.playerWon == True)):
            self.player.InputDown()

    def InputLeft(self):
        if (self.endPause.x == 0 and (self.gameOn == True or self.playerWon == True)):
            self.player.InputLeft()

    def InputRight(self):
        if (self.endPause.x == 0 and (self.gameOn == True or self.playerWon == True)):
            self.player.InputRight()

 

    def crank(self):
       
       #Used to relay the sound effect to play
        toSend = []
        #Keep track of the seconds
        if (self.playerMoved == True and self.gameOn == True): 
            self.scoreCountdown.x = self.scoreCountdown.x - 1
            if (self.scoreCountdown.x == 0):
                self.scoreCountdown.x = self.scoreCountdown.y
                self.score += 1
                if (self.score >= self.scoreToWin): 
                    self.playerWon = True
        
      
        if (self.score == self.scoreToWin):self.circle.playerHasWon = True

        #If the player collides with the circle in end mode, deflect it
        if self.gameOn == False and self.playerWon == True and self.endPause.x == 0:
            if self.circle.corePoint.distanceTo(self.player.corePoint) <= self.circle.radius + self.player.radius:
                self.circle.knock(self.player.corePoint)

        #Game starts in a paused state until the player tries to move
        if self.playerMoved == True:
            
            self.player.crank()
            
            #Pause the circle while the player is playing the end animation
            if (self.endPause.x == 0):
                circleSND = self.circle.crank(self.score)

                #Relay the sound effect instruction
                if (circleSND != ""): toSend.append(circleSND)

            #Gives a little leniency if the player leaves the circe. This was done to solve an issue where the player would "fall off" if they wrapped witht the circle.
            if (self.InCircle() == False): self.grace.x = self.grace.x -1
            else: self.grace.x = self.grace.y

            #Check for a game over.
            if (self.grace.x <= 0 and self.gameOn == True):
                self.gameOn = False
                if (self.circle.mode == 1): self.lostDuringMode1 = True #I could see someone getting confused on what to do when they see the circle leave the edge. This instructs the presentation layer to give a hint.
                self.endPause.x = self.endPause.y #Create a pause to play a sound and animation
                if (self.playerWon == True): 
                    toSend.append(SndVictory)
                else: toSend.append(SndDie)
                 

            #Tick down the end pause, and when it hits 0 set the player into endmode if they won
            if (self.endPause.x > 0):
                self.endPause.x = self.endPause.x - 1
                if (self.endPause.x <= 0 and self.playerWon == True): 
                    self.player.EndMode() #Player won, they can fly around if they want. 
                    toSend.append(SndDrill)

            
                
        else:
            self.player.crank() #Keep an eye out if the player moved.
            if (self.player.PlayerMoved() == True): self.playerMoved = True
        
        return toSend
        

    