import random
import numpy as np
from time import sleep
import os

# Prettytable for pretty map
from prettytable import PrettyTable

# Colorama for Windows, colored font
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style


from ConsoleColor import ConsoleColor
from Agent import Player, Pirate
from Node import Node

# Get Manhattan distance
def manhattanDist(pos1, pos2):
    return sum(abs(value1 - value2) for value1, value2 in zip(pos1, pos2))


class treasureIsland:
    def __init__(self, fileName, delimiter, debug=False):

        self.size = None
        self.turnRevealPrison = None
        self.nRegion = None
        self.turnFreePirate = None
        self.treasurePos = None

        # Map and terrain layers
        self.map = None
        self.terrain = None

        # Prison locations
        self.prisonPos = None

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
            self.treasurePos = tuple(int(x) for x in f.readline().split(sep=' '))

            # Convert to 2D array
            self.map = np.zeros((self.size[0], self.size[1]), dtype=int)
            self.terrain = np.zeros((self.size[0], self.size[1]), dtype=int)
            self.prisonPos = []

            # Use Height for loop
            for i in range(self.size[1]): 
                row = f.readline().replace(' ','').split(delimiter)

                # Use Width for loop
                for j in range(self.size[0]): 
                    
                    # Convert to list by unpacking string. Ex: [*j] -> ['1', '2']
                    cell = [*row[j].strip()]
                    
                    # Check if cell have terrain
                    if len(cell) != 1:
                        self.map[j][i] = int(cell[0])
                        if cell[1] == 'P':
                            self.prisonPos.append((i,j))
                        self.terrain[j][i] = ord(cell[1])
                    else:
                        self.map[j][i] = int(cell[0])
                        self.terrain[j][i] = 0


            self.map = np.array(self.map).reshape(self.size[0], self.size[1])
            self.terrain = np.array(self.terrain).reshape(self.size[0], self.size[1])
            self.prisonPos = np.array(self.prisonPos)

        # Debug mode: show both Player and Pirate position
        self.debug = debug

        self.Player = None
        self.Pirate = None
        self.log = []
        self.turn = 0
        self.win = False
        self.hint = None
        self.trueHint = None
        self.falseHint = None
    

    # Get map
    def getMap(self):
        return self.map

    # Get map terrain
    def getTerrain(self):
        return self.terrain

    # Get treasurePos
    def getTreasurePos(self):
        return self.treasurePos

    # Get map tile
    def getMapTile(self, x, y):
        return self.map[y][x]
    
    # Get map terrain
    def getMapTerrain (self, x, y):
        return self.terrain[y][x]
        
    # Get map size
    def getMapSize(self):
        return self.size

    # Print map
    def printMap(self):
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        colorama_init()

        map_print = PrettyTable()
        map_print.align = 'l'
        map_print.padding_width = 1
        # Print map
        for i in range(self.size[1]): # Use Height for loop
            row = []
            for j in range(self.size[0]): # Use Width for loop

                # Use cell to manage output 
                cell = []
                if self.map[i][j] == 0:
                    cell.append(ConsoleColor.BLUE + '0' + ConsoleColor.END)
                else:
                    cell.append(str(self.map[i][j]))

                # Add terrain layer
                if self.terrain[i][j] != 0:
                    cell.append(ConsoleColor.CYAN + chr(self.terrain[i][j]) + ConsoleColor.END)
                
                # Add agent layer
                # Print Player
                if self.Player.getPosition() == (j, i):
                    cell.append(ConsoleColor.BgBLUE + '*' + ConsoleColor.END)

                # Debug mode
                if self.debug:
                    # Print Pirate
                    if self.Pirate.getPosition() == (j, i):
                        cell.append(ConsoleColor.BgRED + '+' + ConsoleColor.END)
                    # Print Treasure
                    if self.treasurePos == (j, i):
                        cell.append(ConsoleColor.YELLOW + 'T' + ConsoleColor.END)
                
                row.append(''.join(cell))
            map_print.add_row(row)
        print(map_print.get_string(header=False, border=True))

    # Spawn agents
    def spawnAgents(self):

        # Check if position is valid
        def checkValidSpawn(pos):
            x, y = pos
            if self.getMapTile(x, y) == 0:
                return False
            elif self.getMapTerrain(x, y) == ord('M'):
                return False
            return True
        
        # Spawn pirate
        rng = np.random.randint(0,len(self.prisonPos))
        pirateStartPos = self.prisonPos[rng]
        
        # Spawn player
        playerStartPos = np.random.randint(0, self.size, size=(2))
        while True:
            # Make sure player don't spawn on Treasure
            if playerStartPos[0] != self.treasurePos[0] and playerStartPos[1] != self.treasurePos[1]:
                # Make sure player and pirate don't spawn at the same position or pirate s
                if playerStartPos[0] != pirateStartPos[0] and playerStartPos[1] != pirateStartPos[1]:
                    # Make sure player don't spawn on ocean tile
                    if checkValidSpawn(playerStartPos):
                        break
            playerStartPos = np.random.randint(0, self.size, size=(2))

        # Spawn agents
        self.Player = Player(playerStartPos[0], playerStartPos[1])
        self.Pirate = Pirate(pirateStartPos[0], pirateStartPos[1])

    # Find shorteset path to treasure for pirates
    # This sucks btw
    def pirateFindPath(self):
        # A* algorithm
        def AStar(start, end):
            # Create start and end node
            startNode = Node(start[0], start[1])
            endNode = Node(end[0], end[1])

            # Initialize open and closed list
            openList = []
            closedList = []

            # Add the start node
            openList.append(startNode)

            # Loop until you find the end
            while len(openList) > 0:
                # Get the current node
                currentNode = openList[0]
                currentIndex = 0
                for index, item in enumerate(openList):
                    if item.f < currentNode.f:
                        currentNode = item
                        currentIndex = index

                # Pop current off open list, add to closed list
                openList.pop(currentIndex)
                closedList.append(currentNode)

                # Found the goal
                if currentNode == endNode:
                    path = []
                    current = currentNode
                    while current is not None:
                        path.append(current)
                        current = current.parent
                    # Return reversed path
                    return path[::-1]
        
        start = self.Pirate.getPosition()
        end = self.treasurePos
        path = AStar(start, end)
        return path
        
    # Check if agent(Player/Pirate) win, return True if that agent win
    def checkWin(self, agent):
        if agent.name == "Player":
            # Check if player steps on treasure or scanner found treasure
            if agent.getPosition() == self.treasurePos or agent.scannerFoundTreasure:
                return True
            return False

        elif agent.name == "Pirate":
            # Check if pirate steps on treasure
            if agent.getPosition() == self.treasurePos:
                return True
            return False

    # Move agent
    def move(self, agent, direction, step):
        def checkValidMove():
            # Check out of bound
            if agent.xPos < 0 or agent.yPos < 0 or agent.xPos >= self.size[0] or agent.yPos >= self.size[1]:
                print("Out of bound!")
                return False

            # Check if agent steps into sea
            elif self.getMapTile(agent.xPos, agent.yPos) == 0:
                print("Out to the sea!")
                return False
            
            # Check if agent steps into mountain
            elif self.getMapTerrain(agent.xPos, agent.yPos) == ord('M'):
                print("Up to the mountain!")
                return False
            else:
                return True

        if direction == 'W' or direction == 'w':
            agent.yPos -= step
            if not checkValidMove():
                agent.yPos += step

        elif direction == 'S' or direction == 's':
            agent.yPos += step
            if not checkValidMove():
                agent.yPos -= step

        elif direction == 'A' or direction == 'a':
            agent.xPos -= step
            if not checkValidMove():
                agent.xPos += step

        elif direction == 'D' or direction == 'd':
            agent.xPos += step
            if not checkValidMove():
                agent.xPos -= step
        else:
            print("Invalid direction")

        print("Move to ({}, {})".format(agent.xPos, agent.yPos))
        return
    
    # Scan an area around a location (3x3)
    def scan(self, location):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if self.getMapTerrain(location[0] + i, location[1] + j) == self.getTreasurePos().all():
                    print("Treasure found!")
                    return True
        print("Treasure not found!")
        return False

    # Pirate give hint, also tick if hint is true or not
    def pirateGiveHint(self, hint):
        description = ''
        hintIsTrue = False
        match hint:
            case 1:
                description = "Hint: Random locations that doesn't contain treasure (1 to 12)"
                print(description)
                # Random number of tiles
                nTiles = np.random.randint(1, 13)
                for i in range(nTiles):
                    x = np.random.randint(0, self.size[0])
                    y = np.random.randint(0, self.size[1])

                    # Print the tiles
                    print("x: {}, y: {}".format(x, y))
                    if self.getMapTerrain(x, y) == ord('T'):
                        hintIsTrue = True
            case 2:
                description = "Hint: 2-5 regions that 1 of them has the treasure"
                print(description)
                # Random number of regions
                nRegions = np.random.randint(2, 6)
                for i in range(nRegions):
                    region = np.random.randint(0, len(self.regions))
                    
                    # Print the regions
                    print("r: {}".format(r))
                    if self.getMapTile(x, y) == region:
                        hintIsTrue = True
            case 3:
                description = "Hint: 1-3 regions that do not contain the treasure"
                print(description)

                # Random number of regions
                nRegions = np.random.randint(1, 4)
                for i in range(nRegions):
                    r = np.random.randint(0, len(self.regions))
                    print ("r: {}".format(r))
                    if self.map[self.treasurePos[0]][self.treasurePos[1]] != r:
                        hintIsTrue = True
                    else:
                        hintIsTrue = False

            case 4:
                description = "Hint: A large rectangle area that has the treasure"
                print(description)

                # Large rectangle area = 50% size
                pirateHintLocation = np.random.randint(0, self.size[0], size=(2,))
                rect_size = int(self.size[0] / 2)


                if manhattanDist(pirateHintLocation, self.treasurePos) == 2*rect_size:
                    hintIsTrue = True
                else:
                    hintIsTrue = False

                # for i in range(-rect_size, rect_size):
                #     for j in range(-rect_size, rect_size):
                #         if self.treasurePos + i == pirateHintLocation[0] and self.treasurePos + j == pirateHintLocation[1]:
                #             self.hintTrue = False
                #             return self.hintTrue
           
            case 5:
                description = "Hint: A small rectangle area that doesn't has the treasure"
                print(description)
            
                # Small rectangle area = 3x3
                pirateHintLocation = np.random.randint(0, self.size[0], size=(2,))
                rectsize = 3

                if manhattanDist(pirateHintLocation, self.treasurePos) == 2*rect_size:
                    hintIsTrue = True
                else:
                    hintIsTrue = False

                # for i in range(-1, 2):
                #     for j in range(-1, 2):
                #         if self.treasurePos + i == pirateHintLocation[0] and self.treasurePos + j == pirateHintLocation[1]:
                #             self.hintTrue = False
                #             return self.hintTrue

            case 6:
                description = "Hint: The nearest person to the treasure"
                print(description)

                agentHint = np.random.randint(0, 2)
                if agentHint == 0:
                    print("Player")
                    if manhattanDist(self.treasurePos, self.Player.getPosition()) < manhattanDist(self.treasurePos, self.Pirate.getPosition()):
                        hintIsTrue = True
                else:
                    print("Pirate")
                    if manhattanDist(self.treasurePos, self.Pirate.getPosition()) < manhattanDist(self.treasurePos, self.Player.getPosition()):
                        hintIsTruem = True
                
            case 7:
                description = "Hint: A column and/or a row that contain the treasure"
                print(description)

                rowOrColumn = np.random.randint(0, 2)
                if rowOrColumn == 0:
                    print("Row", end=" ")
                    # Same row as treasure y = y
                    tmp_y = np.random.randint(0, self.size[1])
                    if tmp_y == self.treasurePos[1]:
                        hintIsTrue = True
                else:
                    print("Column", end=" ")
                    # Same column as treasure x = x
                    tmp_x = np.random.randint(0, self.size[0])
                    if tmp_x == self.treasurePos[0]:
                        hintIsTrue = True
                
            case 8:
                description = "Hint: A column and/or a row that do not contain the treasure"
                print(description)

                rowOrColumn = np.random.randint(0, 2)
                if rowOrColumn == 0:
                    print("Row", end=" ")
                    # Same row as treasure y = y
                    tmp_y = np.random.randint(0, self.size[1])
                    if tmp_y != self.treasurePos[1]:
                        hintIsTrue = True
                else:
                    print("Column", end=" ")
                    # Same column as treasure x = x
                    tmp_x = np.random.randint(0, self.size[0])
                    if tmp_x != self.treasurePos[0]:
                        hintIsTrue = True

            case 9:
                description = "Hint: 2 regions that the treasure is somewhere in their boundary"
                print(description)

                # Random 2 regions
                regionHint = np.random.randint(0, len(self.regions), size=(2,))

                # Scan 3x3 around treasure to see if the surrounding regions are the same as the hint
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if len(regionHint) == 0:
                            hintIsTrue = True
                            break
                        if self.map[self.treasurePos[0] + i][self.treasurePos[1] + j] == regionHint[0]:
                            regionHint.remove(regionHint[0])
                        if self.map[self.treasurePos[0] + i][self.treasurePos[1] + j] == regionHint[1]:
                            regionHint.remove(regionHint[1])

            case 10:
                description = "Hint: The treasure is somewhere in a boundary of 2 regions"
                print(description)

                regionHint = []
                # Scan 3x3 around to if there are more than 2 regions
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if len(regionHint) == 2:
                            hintIsTrue = True
                            break
                        if self.map[self.treasurePos[0] + i][self.treasurePos[1] + j] not in regionHint:
                            regionHint.append(self.map[self.treasurePos[0] + i][self.treasurePos[1] + j])
                
            case 11:
                description = "Hint: The treasure is somewhere in an area bounded by 2-3 tiles from sea"
                print(description)

                if i + 2 > self.size[0] or j + 2 > self.size[1]:
                    return False
                if i - 2 < 0 or j - 2 < 0:
                    return False
                if i + 3 > self.size[0] or j + 3 > self.size[1]:
                    return False
                if i - 3 < 0 or j - 3 < 0:
                    return False


                # Scan 5x5 around treasure to see if there is a sea tile
                for i in range(-2, 3):
                    for j in range(-2, 3):
                        if self.map[self.treasurePos[0] + i][self.treasurePos[1] + j] == 0:
                            hintIsTrue = True

                # Scam 7x7 around treasure to see if there is a sea tile
                for i in range(-3, 4):
                    for j in range(-3, 4):
                        if self.map[self.treasurePos[0] + i][self.treasurePos[1] + j] == 0:
                            hintIsTrue = True


            case 12:
                description = "Hint: A half of the map without treasure"
                print(description)

                rng = np.random.randint(0, 4)
                if rng == 0:
                    print('The treasure is in the top half of the map')
                    if self.treasurePos[1] < self.size[1] / 2:
                        hintIsTrue = True
                elif rng == 1:
                    print('The treasure is in the bottom half of the map')
                    if self.treasurePos[1] > self.size[1] / 2:
                        hintIsTrue = True
                elif rng == 2:
                    print('The treasure is in the left half of the map')
                    if self.treasurePos[0] < self.size[0] / 2:
                        hintIsTrue = True
                elif rng == 3:
                    print('The treasure is in the right half of the map')
                    if self.treasurePos[0] > self.size[0] / 2:
                        hintIsTrue = True

            case 13:
                description = "Hint: From the center of the map/from the prison that he's staying, he tells you a direction that has the treasure (W, E, N, S or SE, SW, NE, NW)"
                print(description)
                
                directions = ['W', 'E', 'N', 'S', 'SE', 'SW', 'NE', 'NW']
                centerOrPrison = np.random.randint(0, 2)
                directionHint = np.random.randint(0, 8)

                if centerOrPrison == 0:
                    center = self.Pirate.getPosition()
                else:
                    center = (self.size[0] / 2, self.size[1] / 2)

                if directions[directionHint] == 'W':
                    if self.treasurePos[0] < center[0]:
                        hintIsTrue = True
                elif directions[directionHint] == 'E':
                    if self.treasurePos[0] > center[0]:
                        hintIsTrue = True
                elif directions[directionHint] == 'N':
                    if self.treasurePos[1] < center[1]:
                        hintIsTrue = True
                elif directions[directionHint] == 'S':
                    if self.treasurePos[1] > center[1]:
                        hintIsTrue = True
                elif directions[directionHint] == 'SE':
                    if self.treasurePos[0] > center[0] and self.treasurePos[1] > center[1]:
                        hintIsTrue = True
                elif directions[directionHint] == 'SW':
                    if self.treasurePos[0] < center[0] and self.treasurePos[1] > center[1]:
                        hintIsTrue = True
                elif directions[directionHint] == 'NE':
                    if self.treasurePos[0] > center[0] and self.treasurePos[1] < center[1]:
                        hintIsTrue = True
                elif directions[directionHint] == 'NW':
                    if self.treasurePos[0] < center[0] and self.treasurePos[1] < center[1]:
                        hintIsTrue = True

            case 14:
                description = "Hint: 2 squares that are different in size, the small one is placed inside the bigger one, the treasure is somewhere inside the gap between 2 squares"
                print(description, "(WIP)")

                pass

            case 15:
                description = "Hint: The treasure is in a region that has mountain"
                print(description)

                r = self.getMapTile(self.treasurePos[0], self.treasurePos[1])
                for i in range(self.size[1]):
                    for j in range(self.size[0]):
                        if self.getMapTerrain(j, i) == ord('M') and self.map[j][i] == r:
                            hintIsTrue = True

            case _:
                description = 'Invalid hint'
                
                return False
        return hintIsTrue
        
    
    # Player turn, process player's actions (verify, move&scan, moveBigStep, teleport)
    def playerTurn(self):

        '''
            Player's actions:
            1. Verify pirate's hint (return True if hint is correct, the game will do the checking)
            2. Move and scan 
            3. Move big step
            4. Teleport (one time only)

            Player's win condition:
            1. Player steps on treasure
            2. Scanner found treasure
            
        '''
        # Verify pirate's hint
        def verifyHint():
            if self.hintTrue:
                return True
            else:
                return False

        # Move and scan
        def moveAndScan():
            step = int(input("Enter step: "))
            direction = input("Enter direction: ")

            # Check conditions
            if step < 1 or step > 2:
                print("Step must be between 1 and 2")
                sleep(1)
                return
            if direction not in ['W', 'w', 'S', 's', 'A', 'a', 'D', 'd']:
                print("Invalid direction")
                sleep(1)
                return

            self.move(self.Player, direction=direction, step=step)

            scanLocation = input("Enter scan location: ").split()
            scanLocation = [int(i) for i in scanLocation]

            if len(scanLocation) != 2:
                print("Invalid scan location")
                sleep(1)
                return
            
            if self.scan(scanLocation):
                self.Player.foundTreasure = True


        # Move big step
        def moveBigStep():

            # Get step
            step = int(input("Enter step: "))
            if step < 3 or step > 5:
                print("Step must be between 3 and 4")
                sleep(1)
                return
            

            # Get direction
            direction = input("Enter direction: ")
            if direction not in ['W', 'w', 'S', 's', 'A', 'a', 'D', 'd']:
                print("Invalid direction")
                sleep(1)
                return

            self.move(self.Player, direction=direction, step=step)

        # Teleport
        def teleport(self, x, y):
            if self.Player.teleport == 0:
                print("Out of teleport coin")
                sleep(1)
                return
            else:
                self.Player.teleport -= 1
                self.Player.xPos = x
                self.Player.yPos = y
                
                print("Teleport to ({}, {})".format(x, y))
                sleep(1)
                return

        print()
        print("====", "Turn", self.turn, "========================")
        print("Player turn\n")
        print("1. Verify pirate's hint")
        print("2. Move and scan")
        print("3. Move long step")
        if self.Player.teleportCoin:
            print("4. Teleport")

        while True:
            choice = input("Enter your choice: ")
            if choice == '1':
                verifyHint()
                break
            elif choice == '2':
                moveAndScan()
                break
            elif choice == '3':
                moveBigStep()
                break
            elif choice == '4':
                teleport()
                break
            else:
                print("Invalid choice")
                break


    # Pirate turn
    def pirateTurn(self):
        '''
            Pirate have 3 actions:
            1. Move 2 tiles (if isFree == True)
            2. Give hint
            
            Pirate's win condition:
            1. Pirate steps on treasure (after free)
        '''
        def giveFirstHint():
            pass
        

        # print("Pirate turn. Argh!\n")
        # if self.turnFreePirate == self.turn:
        #     self.Pirate.isFree = True
        #     print("The pirate is free")
        #     return
        
        # if self.Pirate.isFree:
        #     self.move(self.Pirate, direction='W', step=1)

    # End scene, write output to file
    def conclude(self):
        with open('output.txt', 'w') as f:
            f.writeline(self.turn)
            if self.win == 1:
                f.writeline("WIN")
            else:
                f.writeline("LOSE")
            for i in self.log:
                f.writeline(i)

    # main
    def main(self):
        self.spawnAgents()

        # Set console size
        os.system('mode con: cols=100 lines=50')

        '''
            How game.main() loop works:
            1. Print map
            2. Player turn
            3. Check player win
            4. Pirate turn (runs in background)
            5. Check pirate win
            6. Repeat
        '''

        while True:
            self.printMap() 

            self.playerTurn()
            if self.checkWin(self.Player):
                self.win = True
                break

        #     self.pirateTurn()
        #     if self.checkWin(self.Pirate):
        #         self.win = False
        #         break

        #     self.turn += 1
        
        # # End game
        # self.conclude()


if __name__ == "__main__":
    game = treasureIsland('Map_8.txt', ';', debug=True)
    # game.spawnAgents()
    # game.printMap()
    game.main()




   
# Ex map
# 0;    0;  0;      0;  0 
# 0;    1;  1M;     1P; 1 
# 0;    1P; 2M;     2;  2 
# 0;    3;  3M;     3;  3 
# 0;    0;  0;      0;  0
