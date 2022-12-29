import random

class treasureIsland:
    def ___init___(self, mapSize, treasurePos, treasureMap=None):
        self.mapSize = mapSize
        self.treasurePos = treasurePos
        self.treasureMap = treasureMap
        
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
            for i in range(self.size):
                for j in range(self.size):
                    f.write(str(self.map[i][j]))
                f.write("\n")

    # Load map
    def loadMap(self, inputMap):
        self.map = inputMap
        return self.map

    # Print map
    def printMap(self):
        for i in range(self.size):
            for j in range(self.size):
                print(self.map[i][j], end=" ")
            print()
# Ex map
# 0;    0;  0;      0;  0 
# 0;    1;  1M;     1P; 1 
# 0;    1P; 2M;     2;  2 
# 0;    3;  3M;     3;  3 
# 0;    0;  0;      0;  0

if __name__ == '__main__':
    mapSize = 5
    treasurePos = (2, 2)
    treasureMap = treasureMap(mapSize, treasurePos)
    treasureMap.printMap()
    treasureMap.saveMap("treasureMap.txt")
    treasureMap.loadMap("treasureMap.txt")
