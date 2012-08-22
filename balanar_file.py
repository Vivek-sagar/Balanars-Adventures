

#------------------------------------------------------------------------
# Library Imports
#------------------------------------------------------------------------

import pygame, sys, os
from pygame.sprite import Sprite
from random import randint, choice
from pygame.locals import *
import balad
import operator


global offset_count     #Meant for the screen movement. Bad naming i know :/
global move_screen      #Flag to be set if the screen must be panned
global screen_offset    #Keeps track of the current offset of the screen

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
        self.attack_rect = pygame.Rect(0,0,0,0)
        self.attack_rect.width, self.attack_rect.height = 0, self.rect.height
        #Pull Balanar back onto the screen
        init_position = tuple(map(operator.add, init_position, (0, -self.rect.height)))
        self.rect = self.rect.move(init_position)
        self.attack_rect.topleft = self.rect.topleft
        self.rect.inflate(-5, -5)
        self.isgrounded = True
        self.isattacking = 0
        self.direction = 1
        self.health = 100

    def update(self, current_ground_rects):
        """Updates ball position. Checks for obstacles, causes jumping and allows for falling off edges"""
        
        global move_screen
        #Horizontal Movement
        if self.movement_force != 0:
        	if abs(self.speed_x) <= BALANAR_MAX_SPEED: 
        		self.speed_x += MOVEMENT_SPEED_INCREMENT * self.movement_force
        		#TODO: Definitely a better way to do this!
        		if self.speed_x > 0:
        		    self.direction = 1
        		elif self.speed_x < 0:
        		    self.direction = -1
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
                
        #Keep Balanar at the same location while the screen is being moved      
        if move_screen:
            self.rect = self.rect.move(-(move_screen*SCREEN_PAN_SPEED), 0)  
            
        if self.rect.right >= SCREEN_WIDTH-SCREEN_PAN_ZONE:
            move_screen = 1
        elif self.rect.left <= SCREEN_PAN_ZONE:
            move_screen = -1
        
        
        
        #Vertical Movement	
        if self.isjumping == True:
            if self.isgrounded == True:
                self.isgrounded = False
                self.speed_y = BALANAR_JUMP_SPEED + BALANAR_GRAVITY #BALANAR_GRAVITY is added straight away because it will get cancelled in the next line
        if self.isgrounded == False:
            self.speed_y -= BALANAR_GRAVITY
 				
        	
        self.rect = self.rect.move(0, -self.speed_y)
        for rect in current_ground_rects:
            if self.rect.colliderect(rect) and self.speed_y < 0:
                self.isgrounded = True
                self.isjumping = False
                self.rect.bottom = rect.top
                break
            elif self.rect.colliderect(rect) and self.speed_y > 0:       #Case where balanar bumps his head
                self.speed_y = 0
                self.rect.top = rect.bottom
            else:
                self.isgrounded = False
        
                    
        #Attacking
        if self.isattacking:
            self.isattacking = self.isattacking + 1
            self.attack_rect.width = 5*self.isattacking
            if (self.isattacking > 10):
                self.attack_rect.width = 0
                self.isattacking = 0
                
        if self.direction == 1:        
            self.attack_rect.topleft = self.rect.topright
        elif self.direction == -1:
            self.attack_rect.topright = self.rect.topleft

    def blitme(self, screen):
        """Blits Balanar and his attacking rect onto the screen"""
        self.screen.blit(self.image, self.rect.topleft)
        pygame.draw.rect(screen, (0,0,0), self.attack_rect)
        
