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

MOVEMENT_SPEED_INCREMENT = 1.5
BALANAR_MAX_SPEED = 10
BALANAR_JUMP_SPEED = 20
BALANAR_GRAVITY = 1.5

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
        self.rect.inflate(-5, -5)
        self.isgrounded = True

    def update(self, current_ground_rects):
        """Updates ball position and checks for obstacles"""
        
        #Horizontal Movement
        if self.movement_force != 0:
        	if abs(self.speed_x) <= BALANAR_MAX_SPEED: 
        		self.speed_x += MOVEMENT_SPEED_INCREMENT * self.movement_force
        else:
        	if self.speed_x > 0: self.speed_x -= MOVEMENT_SPEED_INCREMENT
        	elif self.speed_x < 0: self.speed_x += MOVEMENT_SPEED_INCREMENT
       
        self.rect = self.rect.move(self.speed_x, 0)
        for rect in current_ground_rects:
            if self.rect.colliderect(rect):
                if self.speed_x > 0:
                    self.rect.right = rect.left
                elif self.speed_x < 0:
                    self.rect.left = rect.right
                break
        
        #Vertical Movement	
        if self.isjumping == True:
            if self.isgrounded == True:
                self.isgrounded = False
                self.speed_y = BALANAR_JUMP_SPEED + BALANAR_GRAVITY #BALANAR_GRAVITY is added straight away because it will get cancelled in the next line
        if self.isgrounded == False:
            self.speed_y -= BALANAR_GRAVITY
 				
        	
        self.rect = self.rect.move(0, -self.speed_y)
        for rect in current_ground_rects:
            if self.rect.colliderect(rect):
                self.isgrounded = True
                self.isjumping = False
                self.rect.bottom = rect.top
                break
            else:
                self.isgrounded = False

    def blitme(self, screen):
        self.screen.blit(self.image, self.rect.topleft)

#-------------------------------------------------------------------------
# Event Handler
#-------------------------------------------------------------------------
def EventHandler(balanar, move_screen):
    for event in pygame.event.get():
    	if event.type == pygame.QUIT:
        	pygame.quit()
        if event.type == KEYDOWN:
        	if event.key == K_q:
        		pygame.quit()
        	if event.key == K_DOWN:
        	    move_screen = True
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
    return move_screen

def blit_ground (screen, current_ground_rects):    
    for rect in current_ground_rects:
        pygame.draw.rect(screen, GROUND_COLOUR, rect)
        
def animation_offset_calc():
    num = 0
    while (1):
        num = num + 10
        yield num
        if num >= SCREEN_WIDTH: #must be the same as the condition in move_screen_func()
            num = 0
        
                
def create_ground_rects(ground, current_ground_rects, screen_offset, animation_offset):
    """Creates the actual ground object consisting of 20 Rects"""
    #current_ground_rects = [] #NOO idea why it doesnt work over here. This has been pushed to the main loop
    count = 0
    for i in range(0,20):
    #TODO- Too many hardcoded values!
        current_ground_rects.append(pygame.Rect(count*80-(animation_offset), SCREEN_HEIGHT - ground[i+screen_offset]*50, 80, ground[i+screen_offset]*50))
        count = count+1
    
def move_screen_func(animation_offset_calc, move_screen, screen_offset):
    """Function to pan the screen over to the next or previous screen"""
    animation_offset = 0
    if move_screen == True:
        animation_offset = animation_offset_calc.next()
        print animation_offset
        if animation_offset >= SCREEN_WIDTH:
            move_screen = False
            animation_offset = 0
            screen_offset += 10
    return move_screen, screen_offset, animation_offset
            
        
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
    
    move_screen = False
    
    balanar = ball(screen, img_filename, (0,SCREEN_HEIGHT-50), (0,0))
    
    filestream = open('level', 'r')
    
    screen_offset = 0
    animation_offset = 0
    
    ground = []
    x = filestream.read(1)
    while x != '':
        ground.append(int(x))
        x = filestream.read(1)
    
    current_ground_rects = []
    
    func = animation_offset_calc()
    
    running = True
    
     

    #-----------------------------The Game Loop---------------------------
    while running:
        #Delay
        pygame.time.wait(30)

        #Event Handler
        move_screen = EventHandler(balanar, move_screen) #Has to return a value because move_screen is an immutable datatype and so, wont be changed in EventHandler 

        #Update all objects 
        current_ground_rects = [] 
        if move_screen == True:
            move_screen, screen_offset, animation_offset = move_screen_func(func, move_screen, screen_offset)
        create_ground_rects(ground, current_ground_rects, screen_offset, animation_offset)
            
        balanar.update(current_ground_rects)

        #Fill background colour
        screen.fill(BG_COLOUR)

        #Blit all objects to screen
        blit_ground(screen, current_ground_rects)
        balanar.blitme(screen)

        #Flip the display buffer
        pygame.display.flip()
        
    filestream.close

game()
