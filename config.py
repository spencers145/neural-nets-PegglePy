from vectors import Vector # used for gravity

import pygame

# hard coded window size
WIDTH = 1200
HEIGHT = 900

# CONSTANTS (defaults)
LAUNCH_FORCE = 4.5
gravity = Vector(0, 0.02)
trajectoryDepth = 75 # how many steps to take in the trajectory calculation
bucketVelocity = -1.3

#images
#non hit peg
bluePegImg = pygame.image.load("resources/images/pegs/28x28/unlit_blue_peg.png")
orangePegImg = pygame.image.load("resources/images/pegs/28x28/unlit_red_peg.png")
greenPegImg = pygame.image.load("resources/images/pegs/28x28/unlit_green_peg.png")
#hit peg
hitBluePegImg = pygame.image.load("resources/images/pegs/28x28/glowing_blue_peg.png")
hitOrangePegImg = pygame.image.load("resources/images/pegs/28x28/glowing_red_peg.png")
hitGreenPegImg = pygame.image.load("resources/images/pegs/28x28/glowing_green_peg.png")