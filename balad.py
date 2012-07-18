#------------------------------------------------------------------------
# Library Imports
#------------------------------------------------------------------------

import pygame, sys, os
from pygame.sprite import Sprite
from random import randint, choice
from pygame.locals import *
import operator

#------------------------------------------------------------------------
# Global Constants
#------------------------------------------------------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
GROUND_COLOUR = (25, 50, 25)

MOVEMENT_SPEED_INCREMENT = 0.5
BALANAR_MAX_SPEED = 10
BALANAR_JUMP_SPEED = 10
BALANAR_GRAVITY = 0.5

#------------------------------------------------------------------------
# Class Definitions
#------------------------------------------------------------------------

class ball(Sprite):

    image = None
    movement_force = 0
    isjumping = False

    def __init__(self, screen, img_filename, init_position, speed):

        """Initialise the ball"""
        Sprite.__init__(self)
        self.screen = screen
        self.speed_x, self.speed_y = speed
        self.position = init_position
        self.image =  pygame.image.load(img_filename).convert()
        self.rect = self.image.get_rect()
        #Pull Balanar back onto the screen
        init_position = tuple(map(operator.add, init_position, (0, -self.rect.height)))
        self.rect = self.rect.move(init_position)
        self.isgrounded = True

    def update(self, real_ground):
        """Updates ball position and checks for obstacles"""
        
        #Horizontal Movement
        if self.movement_force != 0:
        	if self.speed_x <= BALANAR_MAX_SPEED: 
        		self.speed_x += MOVEMENT_SPEED_INCREMENT * self.movement_force
        else:
        	if self.speed_x > 0: self.speed_x -= MOVEMENT_SPEED_INCREMENT
        	elif self.speed_x < 0: self.speed_x += MOVEMENT_SPEED_INCREMENT
        	
        
        	
        if self.rect.bottom < real_ground[self.rect.left+5] and self.rect.bottom < real_ground[self.rect.right-5]:
            self.isgrounded = False
        
        #Vertical Movement	
        if self.isjumping == True:
            if self.isgrounded == True:
                self.isgrounded = False
                self.speed_y = BALANAR_JUMP_SPEED + BALANAR_GRAVITY #BALANAR_GRAVITY is added straight away because it will get cancelled in the next line
        if self.isgrounded == False:
            self.speed_y -= BALANAR_GRAVITY
 				
        self.rect = self.rect.move(self.speed_x, -self.speed_y)
        
        #Stops the jump routine only at the ground
        if self.rect.bottom > real_ground[self.rect.centerx]:
            self.rect.bottom = real_ground[self.rect.centerx] 
            self.isjumping = False
            self.isgrounded = True
            self.speed_y = 0

    def blitme(self, screen):
        self.screen.blit(self.image, self.rect.topleft)

#-------------------------------------------------------------------------
# Event Handler
#-------------------------------------------------------------------------
def EventHandler(balanar):
    for event in pygame.event.get():
    	if event.type == pygame.QUIT:
        	pygame.quit()
        if event.type == KEYDOWN:
        	if event.key == K_q:
        		pygame.quit()
           	if event.key == K_LEFT:
           		balanar.movement_force = -1
           	if event.key == K_RIGHT:
           		balanar.movement_force = 1
           	if event.key == K_UP:
           		balanar.isjumping = True
        if event.type == KEYUP:
           	if event.key == K_LEFT:
           		balanar.movement_force = 0
           	if event.key == K_RIGHT:
           		balanar.movement_force = 0

def blit_ground (screen, ground):
    count = 0
    for i in ground:
        tmp_rect = pygame.Rect(count*80, SCREEN_HEIGHT - i*50, 80, i*50)
        pygame.draw.rect(screen, GROUND_COLOUR, tmp_rect)
        count = count+1
        
def calc_real_ground (ground, real_ground):
    for i in ground:
        for j in range(0, 80):
            real_ground.append(SCREEN_HEIGHT - i*50)
        
#-------------------------------------------------------------------------
# Game Loop
#-------------------------------------------------------------------------

def game():

    #-------------------------Game Initialization-------------------------
    
    BG_COLOUR = 100, 200, 100

    img_filename = "images/ball.png"

    pygame.init()
    screen = pygame.display.set_mode ((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    clock = pygame.time.Clock()
    
    balanar = ball(screen, img_filename, (0,SCREEN_HEIGHT-50), (0,0))
    
    ground = [1,2,1,4,4,4,3,3,2,1]
    real_ground = []
    
    running = True
    
    calc_real_ground(ground, real_ground) 

    #-----------------------------The Game Loop---------------------------
    while running:
        #Delay
        pygame.time.wait(20)

        #Event Handler
        EventHandler(balanar)

        #Update all objects    
             
        balanar.update(real_ground)

        #Fill background colour
        screen.fill(BG_COLOUR)

        #Blit all objects to screen
        blit_ground(screen, ground)
        balanar.blitme(screen)

        #Flip the display buffer
        pygame.display.flip()

game()
