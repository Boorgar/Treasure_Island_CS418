import random
import numpy as np
from argparse import ArgumentParser
from Agent import Agent
from Pirate import Pirate

class treasureIsland:
    def __init__(self, fileName, delimiter):
        # Read file
        with open(fileName, 'r') as f:
            # Get size
            self.size = [int(x) for x in f.readline().split(sep=' ')]
            # Get turn number that the pirate reveals the prison
            self.turnRevealPrison = int(f.readline())
            # Get the number of regions
            self.nRegion = int(f.readline())
            # Get turn number that the pirate is free
            self.turnFreePirate = int(f.readline())
            # Get treasure position
            self.treasurePos = [int(x) for x in f.readline().split(sep=' ')]
            # Convert to 2D array
            self.map = []
            for i in range(self.size[1]): # Use Height for loop
                self.map.append(f.readline().split(delimiter))
            self.map = np.array(self.map).reshape(self.size[0], self.size[1])


        self.Agent = Agent()
        self.Pirate = Pirate()
        self.turn = 0


    # Generate map
    def generateMap(self):
        # Check map valid
        def checkMapValid():
            pass
        for i in range(self.size):
            for j in range(self.size):
                self.map[i][j] = random.randint(0, 1)
        # Place treasure
        self.map[self.treasure[0]][self.treasure[1]] = 2
        return self.map

    # Save map
    def saveMap(self, fileName):
        with open(fileName, 'w') as f:
            for i in range(self.size[1]):
                for j in range(self.size[0]):
                    if j != 0:
                        f.write(";")
                    f.write(str(self.map[i][j]))
                f.write("\n")


    # Print map
    def printMap(self):
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                print(self.map[i][j], end=" ")
            print()

    # main
    def main(self):
        pass


if __name__ == "__main__":
    game = treasureIsland('input.txt', ';')
    game.printMap()
    game.saveMap('output.txt')




   
# Ex map
# 0;    0;  0;      0;  0 
# 0;    1;  1M;     1P; 1 
# 0;    1P; 2M;     2;  2 
# 0;    3;  3M;     3;  3 
# 0;    0;  0;      0;  0
