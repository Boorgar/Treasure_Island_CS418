import numpy as np

class Agent:
    def __init__(self, xStartPos, yStartPos):
        self.xPos = xStartPos
        self.yPos = yStartPos

    # Get agent position
    def getPosition(self):
        return (self.xPos, self.yPos)

class Player(Agent):
    def __init__(self, xStartPos, yStartPos):
        super().__init__(xStartPos, yStartPos)
        self.name = "Player"
        self.teleportCoin = 1
        self.scannerFoundTreasure = False

class Pirate(Agent):
    def __init__(self, prison_x, prison_y):
        super().__init__(prison_x, prison_y)
        self.name = "Pirate"
        self.isFree = False

    
