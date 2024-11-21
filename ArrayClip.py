class ArrayClip:
    def __init__(self,coreArray,framesPerIndex) -> None:
        self.coreArray = coreArray
        self.currentIndex = 0 #Get current returns coreArray[currentIndex]
        self.framesPerIndex = framesPerIndex #How long in frames to keep the current array
        self.framesLeft = framesPerIndex #Ticks down every time crank() is run, index changes when this hits 0
        self.going = 1 #Added to currentIndex when frames left reaches 0
        self.mode = 0
        #0 = Normal = When currentIndex if the length of coreArray coreArray is set to 0
        #1 = Reverse = Going is set to -1, when current index is -1 the length of the coreArray is added to it
        #2 = Osciallate = When the currentIndex is the length of coreArray-1 is set to -1. When the current index is 0 going is +1
        #3 = PlayThenStop = When currentFrame is the length of coreArray it subtracts 1 and playing is set to False
        self.playing = True

    def switchMode(self,toThis):
        self.mode = toThis

    def rewind(self):
        self.currentIndex = 0

    def getCurrent(self): 
        return self.coreArray[self.currentIndex]

    def setCurrentFrame(self, toThis):
        self.currentIndex = toThis
        if (self.currentIndex < 0): self.currentIndex = 0
        if (self.currentIndex >= len(self.coreArray)): self.currentIndex = len(self.coreArray) - 1
        self.framesLeft = self.framesPerIndex


    def crank(self):
        if self.playing == True:
            self.framesLeft = self.framesLeft -1
            if self.framesLeft <= 0:
                self.framesLeft = self.framesPerIndex
                if self.mode == 0: #Plays normally then starts over after it reaches the end
                    
                    self.currentIndex = self.currentIndex + 1
                    if (self.currentIndex >= len(self.coreArray)): self.currentIndex = 0
                
                if self.mode == 3: #Plays then stopps
                    if (self.currentIndex < len(self.coreArray) - 1): self.currentIndex = self.currentIndex + 1
                    

