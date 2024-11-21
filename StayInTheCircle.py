#Made by David Schriver October 2024 - 

# Used to do the fade out effect
#https://stackoverflow.com/questions/6339057/draw-transparent-rectangles-and-polygons-in-pygame

import StayInTheCircleCore
import pygame
import math
import ArrayClip
import os

pygame.init()

window = pygame.display.set_mode((StayInTheCircleCore.ArenaWidth,StayInTheCircleCore.ArenaHeight))
pygame.display.set_caption("Stay in the Circle")


#Which part of the game the game is at
Screen = 0
#0 = Menu
#1 = Menu to Game
#2 = Game
#3 = Game to End
#4 = End
#5 = End to Title


FadingOut = True
Transitioning = False #Whether or not the game is fading in or out
FadeOutCurrent = 0 
FadeOutMax = 50
leFont = pygame.font.Font('assets/consola.ttf',32)
leFontSmaller = pygame.font.Font('assets/consola.ttf',24)
leFontSmallest = pygame.font.Font('assets/consola.ttf',16)
RestartText = leFontSmaller.render("Press R to restart",False,(255,255,255))
coreGame = StayInTheCircleCore.StayInTheCircleCore()
paused = False

#This stops the game from getting paused or unpaused for a time. Without this the game will pause and unpause rapidly if the P button is pressed.
pauseCooldown = 0
pauseCooldonwMax = 5


#Returns an array of fetched resources
def bulkLoad(prefix,goTo,end):
     toSend = []
     counter = 1

     while (counter <= goTo):
          toPut = prefix+str(counter)+end
         
          toSend.append(pygame.image.load(toPut))
          counter += 1

     return toSend

#Regular walking
ConeFrames = {}
ConeFrames[""] = ArrayClip.ArrayClip(bulkLoad("assets/img/idle",4,".png"),5)
ConeFrames["l"] = ArrayClip.ArrayClip(bulkLoad("assets/img/Left",4,".png"),5)
ConeFrames["r"] = ArrayClip.ArrayClip(bulkLoad("assets/img/Right",4,".png"),5)
ConeFrames["u"] = ArrayClip.ArrayClip(bulkLoad("assets/img/Up",4,".png"),5)
ConeFrames["d"] = ArrayClip.ArrayClip(bulkLoad("assets/img/Down",4,".png"),5)

#Spinning cone
ConeFramesWin = {}
ConeFramesWin[""] = ArrayClip.ArrayClip(bulkLoad("assets/img/WinUp",2,".png"),3)
ConeFramesWin["l"] = ArrayClip.ArrayClip(bulkLoad("assets/img/WinLeft",2,".png"),3)
ConeFramesWin["r"] = ArrayClip.ArrayClip(bulkLoad("assets/img/WinRight",2,".png"),3)
ConeFramesWin["u"] = ArrayClip.ArrayClip(bulkLoad("assets/img/WinUp",2,".png"),3)
ConeFramesWin["d"] = ArrayClip.ArrayClip(bulkLoad("assets/img/WinDown",2,".png"),3)

#Audio
sfx = {}
sfx [StayInTheCircleCore.SNDBump] = pygame.mixer.Sound(StayInTheCircleCore.SNDBump)
sfx [StayInTheCircleCore.SNDBump2] = pygame.mixer.Sound(StayInTheCircleCore.SNDBump2)
sfx [StayInTheCircleCore.SNDWrap] = pygame.mixer.Sound(StayInTheCircleCore.SNDWrap)
sfx [StayInTheCircleCore.SndVictory] = pygame.mixer.Sound(StayInTheCircleCore.SndVictory)
sfx [StayInTheCircleCore.SndDrill] = pygame.mixer.Sound(StayInTheCircleCore.SndDrill)
sfx [StayInTheCircleCore.SndDie] = pygame.mixer.Sound(StayInTheCircleCore.SndDie)

sfxTransition = pygame.mixer.Sound("assets/snd/transition.wav")

ConeDie = ArrayClip.ArrayClip(bulkLoad("assets/img/Die",16,".png"),5)
ConeDie.switchMode(3) #Plays and then stops
ConeWin = ArrayClip.ArrayClip(bulkLoad("assets/img/Win",4,".png"),5)
StoneCircleBase = bulkLoad("assets/img/StoneCircle",1,".png")[0]
TitleImage = bulkLoad("assets/img/ConeTitle",1,".png")[0]
StarsBKGBase = ArrayClip.ArrayClip(bulkLoad("assets/img/stars",68,".png"),1)
ColorCycle = ArrayClip.ArrayClip([(255,0,0),(255,55,0),(255,105,0),(255,155,0),(255,205,0),(255,255,0),(205,255,0),(155,255,0),(105,255,0),(55,255,0),(0,255,0),(0,255,55),(0,255,105),(0,255,155),(0,255,205),(0,255,255),(0,205,255),(0,155,255),(0,105,255),(0,55,255),(0,0,255),(55,0,255),(105,0,255),(105,0,255),(155,0,255),(205,0,255),(255,0,255),(255,0,205),(255,0,155),(255,0,105),(255,0,55)],1)

#Game runs a block of code at about 30fpx. This prevents the game from freezing on trying to close.
def isClosed():
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT: return True

    return False

def RenderTitle():
    window.blit(TitleImage,(0,0,500,500))
    leText = leFontSmaller.render('Press Space to Begin',False,ColorCycle.getCurrent())
    leTextRect = leText.get_rect()
    leTextRect.center = (StayInTheCircleCore.ArenaWidth//2,StayInTheCircleCore.ArenaHeight - 20)
    window.blit(leText,leTextRect)
    

def RenderGame():
    global coreGame
    global paused
    window.fill((0,0,0))
    window.blit(StarsBKGBase.getCurrent(),(0,0))
    if (coreGame.playerMoved):StarsBKGBase.crank() #Animate the stars after the player has moved.
    if coreGame.playerMoved == False: #Before the player moves, tell them what they need to do to start the game.
         baseWords = leFont.render(str("Use Arrow Keys to Move"),False,ColorCycle.getCurrent())
         baseWordsCenter = baseWords.get_rect()
         baseWordsCenter.center = (StayInTheCircleCore.ArenaWidth//2,StayInTheCircleCore.ArenaHeight - 100)
         window.blit(baseWords,baseWordsCenter)
    
    RenderCircle()
    RenderPlayer()

    if paused: #Show "PAUSED" when paused
         centermepause = leFont.render("PAUSED",False,(255,100,100))
         centermepauserect = centermepause.get_rect()
         centermepauserect.center = (StayInTheCircleCore.ArenaWidth//2,StayInTheCircleCore.ArenaHeight//2)
         window.blit(centermepause,centermepauserect)

    if coreGame.playerMoved == True: 
        #Show the score.
        ScoreToPut = str(coreGame.score)
        ColorToPut = (150,255,100)

        if (coreGame.playerWon == False and coreGame.gameOn == False): #Player lost the game, show final score, and a hint if relevant
             ColorToPut = (255,100,100)
             hintToPut = leFontSmallest.render("Try to make it to " + str(coreGame.scoreToWin),False,ColorToPut) #Shows the "goal"
             if (coreGame.lostDuringMode1): #The plaer lost while the circle was clipping through the otheside of the arena
                  hintToPut = leFontSmallest.render("Tip: You can go off the edge of the screen too.",False,ColorToPut)
             hintToPutRect = hintToPut.get_rect()
             hintToPutRect.center = (StayInTheCircleCore.ArenaWidth//2,50)
             window.blit(hintToPut,hintToPutRect)

        if (coreGame.gameOn == False): 
            ScoreToPut = "Final Score: " + ScoreToPut
            window.blit(RestartText,(StayInTheCircleCore.ArenaWidth - 250,StayInTheCircleCore.ArenaHeight - 30))

        centerme = leFont.render(ScoreToPut,False,ColorToPut)
        centermerect = centerme.get_rect()
        centermerect.center = (StayInTheCircleCore.ArenaWidth//2,30)
        window.blit(centerme,centermerect)
    

def RenderPlayer():
    for pt in coreGame.player.getNine(): #Create 8 mirror images for wrapping
        color = (100,255,255)

        if coreGame.gameOn == False:#Game over
             color = (255,100,100)
             if (coreGame.playerWon): #Player won the game
                 color = (100,255,100)
                 if (coreGame.endPause.x != 0): #Should play an animation then go into end mode
                      window.blit(ConeWin.getCurrent(),(pt.x - 20, pt.y - 20))
                      ConeWin.crank()
                 else:
                      window.blit(ConeFramesWin[coreGame.player.facing].getCurrent(),(pt.x - 20, pt.y - 20))
                      ConeFramesWin[coreGame.player.facing].crank()
             else:
                  if (coreGame.endPause.x != 0 and coreGame.endPause.x != 0):# Should play an animation and disappear after losing
                       

                       window.blit(ConeDie.getCurrent(),(pt.x - 20, pt.y - 20))
                       

                       ConeDie.crank()
                       
                       

             


        else: #Game is running
            window.blit(ConeFrames[coreGame.player.facing].getCurrent(),(pt.x - 20,pt.y - 20))

def RenderCircle():
     
     
     color = (100,100,100)

     if coreGame.InCircleGrace() == False:
          color = (100,50,50)

     for pt in coreGame.circle.getNine():
          pygame.draw.circle(window,color,pt.toTuple(),coreGame.circle.radius)
          window.blit(pygame.transform.scale(StoneCircleBase,(coreGame.circle.radius * 2,coreGame.circle.radius * 2)),(pt.x - coreGame.circle.radius,pt.y - coreGame.circle.radius))

def RenderLose():
    window.fill((0,0,0))
    window.blit(leFont.render('FAIL',False,(255,100,100)),(0,0))

def RenderWin():
    window.fill((0,0,0))
    window.blit(leFont.render('WIN',False,(100,255,100)),(0,0))



def RenderEnd():
     if coreGame.TEMPGAMESTATE == 1:
            RenderWin()
     else:
         RenderLose()


def FadeOut(ThingInBKG):
    global FadeOutCurrent
    global window
    leSurface = pygame.Surface((StayInTheCircleCore.ArenaWidth,StayInTheCircleCore.ArenaHeight),pygame.SRCALPHA)
    
    FadeOutCurrent += 2
    ThingInBKG()
    
    pygame.draw.rect(leSurface,(0,0,0,round(255 * (FadeOutCurrent/FadeOutMax))),(0,0,StayInTheCircleCore.ArenaWidth,StayInTheCircleCore.ArenaHeight))
    window.blit(leSurface,(0,0,StayInTheCircleCore.ArenaWidth,StayInTheCircleCore.ArenaHeight))

    if FadeOutCurrent >= FadeOutMax:
            return True
        
    return False

def FadeIn(ThingInBKG):
    global FadeOutCurrent
    global window
    leSurface = pygame.Surface((StayInTheCircleCore.ArenaWidth,StayInTheCircleCore.ArenaHeight),pygame.SRCALPHA)
    
    FadeOutCurrent -= 2
    ThingInBKG()
    
    pygame.draw.rect(leSurface,(0,0,0,round(255 * (FadeOutCurrent/FadeOutMax))),(0,0,StayInTheCircleCore.ArenaWidth,StayInTheCircleCore.ArenaHeight))
    window.blit(leSurface,(0,0,StayInTheCircleCore.ArenaWidth,StayInTheCircleCore.ArenaHeight))

    if FadeOutCurrent <= 0:
            return True
        
    return False




while isClosed() == False:
    pygame.time.delay(33)
    input = pygame.key.get_pressed()
    ColorCycle.crank()

    if Screen == 0:#Title Screen
        RenderTitle()
        if input[pygame.K_SPACE]: 
             Screen += 1
             sfxTransition.play()

    elif Screen == 1: #Transitioning to game
       
        if FadingOut == True:
           if FadeOut(RenderTitle) == True:
                FadingOut = False
                coreGame = StayInTheCircleCore.StayInTheCircleCore()
        
        elif FadingOut == False:
             if FadeIn(RenderGame) == True:
                  FadingOut = True
                  Screen += 1
    elif Screen == 2: #Game
        if paused == True:
            if input[pygame.K_p] == True and pauseCooldown == 0: 
                    paused = False
                    
                    
                    pauseCooldown = pauseCooldonwMax
        elif coreGame.GameOn(): #Relay user input
            if input[pygame.K_UP]: coreGame.InputUp()
            if input[pygame.K_DOWN]: coreGame.InputDown()
            if input[pygame.K_LEFT]: coreGame.InputLeft()
            if input[pygame.K_RIGHT]: coreGame.InputRight()
          
            if input[pygame.K_r]: #Restarts the game
                 sfxTransition.play()
                 FadingOut = True
                 Screen = 6
                 ConeDie.rewind()
                
                
            if input[pygame.K_p] == True and pauseCooldown == 0: 
                paused = True
                
                RenderGame()
                
                pauseCooldown = pauseCooldonwMax
            else:
                crankSounds = coreGame.crank()

                for sound in crankSounds:
                    sfx[sound].play()

                ConeFrames[coreGame.player.facing].crank()
                RenderGame()
                
        else: #I don't see when this will fire off, but I'm afriad to remove it.
            Screen +=1
        
        if pauseCooldown > 0: pauseCooldown -= 1


    elif Screen == 6: #Restarting the game from the game
         if FadingOut == True:
           if FadeOut(RenderGame) == True:
                FadingOut = False
                coreGame = StayInTheCircleCore.StayInTheCircleCore() #Reload the core game completely
         elif FadingOut == False:
             if FadeIn(RenderGame) == True:
                  FadingOut = True
                  Screen = 2
                  ConeDie.rewind()


             

        


    pygame.display.update()
