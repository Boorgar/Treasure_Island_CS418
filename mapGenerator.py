import numpy as np

# Generate map
def generateMap(size):
    w, h = size
    t_map = np.zeros((w, h))

    # Generate map
    for i in range(w):
        for j in range(h):
            t_map[i][j] = np.random.randint(0, 2)
        

# Save map
def saveMap(self, fileName):
    with open(fileName, 'w') as f:
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                if j != 0:
                    f.write(";")
                f.write(str(self.map[i][j]))
            f.write("\n")