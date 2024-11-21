# Stay In the Circle
A game where you have to stay within a bouncing circle. Made with PyGame/Python.

#How to Run
1. If you don't have python installed run follow this tutorial: https://www.youtube.com/watch?v=YKSpANU8jPE
2. If you don't have pygame installed enter this into your command prompt 
<i>pip install pygame</i>
3. Open command prompt, navigate to the root folder and enter:
<i>python StayInTheCircle.py</i>

Alternatively, you can put "python StayInTheCircle.py" into a text document and change that document's extension to "cmd" and double click that.

#How to Play
Use the arrow keys to control the yellow cone inside the bouncing platform. There's a surprise if you can make it to 60 seconds. 

#Explanation of Files

ArrayClip.py: Automatically presents an item from an array using an ever changing index which usually increases by 1 and then goes back to 0 when it reaches the end of the array. Ideal for handling animation frames. Meant to function similarily to MovieClip within Flash. Used by StayInTheCircle.py
StayInTheCircle.py: The presentation layer. It is responsible for relaying input from the player to the core game and using PyGame to add visuals and sound to the core game for the player. Uses StayInTheCircleCore.py.
StayInTheCircleCore.py: The actual abstract game that functions independently from PyGame, visuals, and audio. In here everything is math and geometry so it needs the StayInTheCircle.py to create and audio visual experience so the player can see what's going on. Makes use of TrigJacknife.py.
TrigJacknife.py: Contains home-made point and rectangle classes along with trigonmetric functions. All essential for making a game like this.
