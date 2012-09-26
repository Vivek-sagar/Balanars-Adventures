'''
------------------------------------------------------------------------
    Copyright (C) 2012  Vivek Vidyasagaran
    Email : vivek.v.sagar@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

-------------------------------------------------------------------------
'''

#------------------------------------------------------------------------
# Library Imports
#------------------------------------------------------------------------

import pygame, sys, os
from pygame.sprite import Sprite
from random import randint, choice
from pygame.locals import *
import operator
import math                 #Just for logs

#------------------------------------------------------------------------
# Global Constants
#------------------------------------------------------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
BG_COLOUR = 200, 200, 200
GROUND_UNIT_WIDTH, GROUND_UNIT_HEIGHT = 80, 50
GROUND_COLOUR = (50, 25, 25)
HEALTH_BAR_COLOUR = (200, 255, 100)

ENEMY_ATTACK_REACH = 30     #Number of pixels the enemy can reach. Don't set below 15
ENEMY_ATTACK_DELAY = 50     #Number of cycles before enemy attacks again.

MOVEMENT_SPEED_INCREMENT = 0.5
BALANAR_MAX_SPEED = 3
BALANAR_JUMP_SPEED = 15
BALANAR_GRAVITY = 1.0
SCREEN_PAN_SPEED = 30
SCREEN_PAN_ZONE = 10
MAX_SCREEN_OFFSET = 3000     #Changes whenever the number of blocks in level is changed

BALANAR_IMAGE_CHANGE_THRESHOLD = 20

global offset_count         #Meant for the screen movement. Bad naming i know :/
global move_screen          #Flag to be set if the screen must be panned
global screen_offset        #Keeps track of the current offset of the screen

#------------------------------------------------------------------------
# Class Definitions
#------------------------------------------------------------------------

#-----------------------Balanar------------------------------------------

class ball(Sprite):

    image = None
    movement_force = 0
    isjumping = False
    

    def __init__(self, screen, init_position, speed):
        """Initialize Balanar"""
        
        Sprite.__init__(self)
        self.screen = screen
        self.speed_x, self.speed_y = speed
        self.position = init_position
        #TODO: Should learn to use spritesheets!
        image_walk_1 = pygame.image.load("images/BaladSprites/bala_side_2.png")
        image_walk_2 = pygame.image.load("images/BaladSprites/bala_side_1.png")
        image_walk_3 = pygame.image.load("images/BaladSprites/bala_side_3.png")
        image_attack_1 = pygame.image.load("images/BaladSprites/bala_attack_1.png")
        image_attack_2 = pygame.image.load("images/BaladSprites/bala_attack_2.png")
        image_attack_3 = pygame.image.load("images/BaladSprites/bala_attack_3.png")
        image_jump = pygame.image.load("images/BaladSprites/bala_jump.png")
        image_red = pygame.image.load("images/BaladSprites/bala_red.png")
        self.rect = image_walk_1.get_rect()
        #self.image.set_colorkey((255, 248, 255))   #Required only if the image isnt transparent
        self.attack_rect = pygame.Rect(0,0,0,0)
        self.attack_rect.width, self.attack_rect.height = 0, self.rect.height
        init_position = tuple(map(operator.add, init_position, (0, -self.rect.height)))     #Pull Balanar back onto the screen
        self.rect = self.rect.move(init_position)
        self.attack_rect.topleft = self.rect.topleft
        self.rect.inflate(-5, -5)
        self.isgrounded = True
        self.directionchanged = False
        self.isattacking = 0
        self.hit_cooldown = 0
        self.image_change_threshold = 0
        self.direction = 1
        self.health = 100
        self.states = {0 : image_walk_1, 
                       1 : image_walk_2, 
                       2 : image_walk_3,
                       3 : image_attack_1,
                       4 : image_attack_2,
                       5 : image_attack_3,
                       6 : image_jump,
                       7 : image_red}
        self.image_differences = {0 : 0,
                            1 : image_walk_2.get_width() - image_walk_1.get_width(),
                            2 : image_walk_3.get_width() - image_walk_1.get_width(),
                            3 : image_attack_1.get_width() - image_walk_1.get_width(),
                            4 : image_attack_2.get_width() - image_walk_1.get_width(),
                            5 : image_attack_3.get_width() - image_walk_1.get_width(),
                            6 : image_jump.get_width() - image_walk_1.get_width(),
                            7 : image_red.get_width() - image_walk_1.get_width()}
        self.state = 0
    def update(self, current_ground_rects):
        """Updates ball position. Checks for obstacles, causes jumping and allows for falling off edges"""
        
        global move_screen
        self.directionchanged = False
        #Horizontal Movement
        if self.movement_force != 0:
        	if abs(self.speed_x) <= BALANAR_MAX_SPEED: 
        		self.speed_x += MOVEMENT_SPEED_INCREMENT * self.movement_force
        		#TODO: Definitely a better way to do this!
        		if self.speed_x > 0:
        		    if self.direction != 1:     #If direction changed (Defunct!)
        		        self.directionchanged = True
        		    self.direction = 1
        		    
        		elif self.speed_x < 0:
        		    if self.direction != -1:     #If direction changed (Defunct!)
        		        self.directionchanged = True
        		    self.direction = -1
        		    
        else:
        	if self.speed_x > 0: self.speed_x -= MOVEMENT_SPEED_INCREMENT
        	elif self.speed_x < 0: self.speed_x += MOVEMENT_SPEED_INCREMENT
       
        self.rect = self.rect.move(self.speed_x, 0)
        
        self.image_change_threshold = self.image_change_threshold + self.speed_x     #To check if the image needs to be changed
        if self.speed_x == 0: self.state = 0
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
        
        #Code to loop through the walking pictures of balanar  
        if self.image_change_threshold > BALANAR_IMAGE_CHANGE_THRESHOLD or self.image_change_threshold < -BALANAR_IMAGE_CHANGE_THRESHOLD:
            self.image_change_threshold = 0      
            self.state = self.state + 1
            if self.state > 3:
                self.state = 0
        
        
        #Vertical Movement	
        if self.isjumping == True:
            self.state = 7
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
              
        #Health Considerations:        
        if self.hit_cooldown > 0:
            self.hit_cooldown = self.hit_cooldown - 1
            if self.hit_cooldown > 30: self.state = 8                       
        if self.health < 0:
            #Game Over!
            self.health = 0
                    
        #Attacking
        if self.isattacking:
            self.isattacking = self.isattacking + 1
            self.state = 4
            self.attack_rect.width = 5*self.isattacking
            if self.isattacking > 5:
                self.state = 5
            if self.isattacking > 10:
                self.state = 6
            if self.isattacking > 15:
                self.attack_rect.width = 0
                self.isattacking = 0
                
        if self.direction == 1:        
            self.attack_rect.topleft = self.rect.topright
        elif self.direction == -1:
            self.attack_rect.topright = self.rect.topleft
            
        
    def blitme(self, screen):
        """Blits Balanar and his attacking rect onto the screen"""       
        shift = 0
        if self.state == 0:
            self.image = self.states[0]
        elif self.state == 1:
            self.image = self.states[1]
            shift = self.image_differences[1]
        elif self.state == 2:
            self.image = self.states[0]
            shift = self.image_differences[0]
        elif self.state == 3:
            self.image = self.states[2]
            shift = self.image_differences[2]
        elif self.state == 4:
            self.image = self.states[3]
            shift = self.image_differences[3]
        elif self.state == 5:
            self.image = self.states[4]
            shift = self.image_differences[4]
        elif self.state == 6:
            self.image = self.states[5]
            shift = self.image_differences[5]
        elif self.state == 7:
            self.image = self.states[6]
            shift = self.image_differences[6]
        elif self.state == 8:
            self.image = self.states[7]
            shift = self.image_differences[7]
            
        self.image = pygame.transform.flip(self.image, True, False)     #Balanar is the only one facing the other way in the beginning :/  
                                                                        #TODO: Should probably invert the image to begin with.
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            shift = 0
            
        self.screen.blit(self.image, (self.rect.left-shift, self.rect.top)) 
        
        #pygame.draw.rect(screen, (0,0,0), self.rect)              
        #pygame.draw.rect(screen, (0,0,0), self.attack_rect)
        
#-----------------------Enemy---------------------------------------------
        
class enemy(Sprite):
    def __init__(self, screen, init_position):
        """Initialiser for all enemies"""        
        Sprite.__init__(self)
        
        self.screen = screen
        self.position = init_position
        #self.image =  pygame.image.load(img_filename).convert()        
        self.speed = 2
        self.direction = -1
        self.health = 100 
        #self.image.set_colorkey((255, 255, 255))     
        self.hit_cooldown = 0
        self.isattacking = 0        
        self.state = 0
        
        
    def update(self, ground_rects, enemies, balanar):
        """Updates enemy position, checking for obstacles and allowing for screen panning""" 
        
        if move_screen:
            self.rect = self.rect.move(-(move_screen*SCREEN_PAN_SPEED), 0) 
            
        #if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
         #   return
        
        #If Enemy is currently attacking, dont move!    
        if not self.isattacking:
            if self.direction == 1:
                if balanar.rect.left < self.rect.right + (ENEMY_ATTACK_REACH-10) and balanar.rect.left > self.rect.right:
                    self.isattacking = True
            elif self.direction == -1:
                if balanar.rect.right > self.rect.left - (ENEMY_ATTACK_REACH-10) and balanar.rect.right < self.rect.left:
                    self.isattacking = True
                    
        #If not, move!    
        if not self.isattacking:
            self.rect = self.rect.move(self.direction*self.speed, 0);
            self.image_change_threshold = self.image_change_threshold + self.direction*self.speed     #To check if the image needs to be changed
            
            for rect in ground_rects:
                if self.rect.colliderect(rect):
                    if self.direction > 0:
                        self.rect.right = rect.left
                    else:
                        self.rect.left = rect.right
                    self.direction = -self.direction
                
                if self.rect.left < rect.right and rect.right - self.rect.left < GROUND_UNIT_WIDTH:
                    if self.rect.bottom < rect.top - 5:
                        self.direction = -self.direction
                        self.rect.left = rect.right
                elif self.rect.right > rect.left and self.rect.right - rect.left < GROUND_UNIT_WIDTH:
                    if self.rect.bottom < rect.top - 5:
                        self.direction = -self.direction
                        self.rect.right = rect.left

        
            
        #Health Considerations:        
        if self.hit_cooldown > 0:
            self.hit_cooldown = self.hit_cooldown - 1
        if self.health < 0:
            #Destroy!!
            enemies.remove(self)
            self.health = 0
            
        #Code to loop through the walking pictures of enemy:  
        if self.image_change_threshold > BALANAR_IMAGE_CHANGE_THRESHOLD or self.image_change_threshold < -BALANAR_IMAGE_CHANGE_THRESHOLD:
            self.image_change_threshold = 0      
            self.state = self.state + 1
            if self.state > 2:
                self.state = 0
                
        #Attack rect:
        if self.direction == 1:
            self.attack_rect.topleft = self.rect.topright
        elif self.direction == -1:
            self.attack_rect.topright = self.rect.topleft
          
        #Attacking              
        if self.isattacking:
            self.isattacking = self.isattacking + 1
            self.state = 1
            if self.isattacking < 10:
                self.attack_rect.width = (ENEMY_ATTACK_REACH/10)*self.isattacking
            if self.isattacking < 5:
                self.state = 3
            elif self.isattacking < 10:
                self.state = 4
            elif self.isattacking < 15:
                self.state = 5
            else:
                self.attack_rect.width = 0
            if self.isattacking > ENEMY_ATTACK_DELAY:
                self.isattacking = 0
                    
        
    def blitme(self, screen):
        """Blits the enemy onto the screen"""
        self.image = self.states[self.state]
        (shift, shift_height) = self.image_differences[self.state]
        
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            if shift > 0: shift = 0
            #self.screen.blit(self.image, self.rect.topleft)
        else:    
            if shift < 0: shift = 0                             #To take care of the sword going the other way
        self.screen.blit(self.image, (self.rect.left + (self.direction*shift), self.rect.top))
        #pygame.draw.rect(screen, (0,0,0), self.attack_rect)
        pygame.draw.rect(screen, HEALTH_BAR_COLOUR, pygame.Rect(self.rect.left, self.rect.top-20, self.rect.width*(self.health/100.0), 10))
   
        
class enemy_type1(enemy):
    def __init__(self, screen, img_filename, init_position, ground_rects):
        """Initialiser for type 1 enemies"""      
        enemy.__init__(self, screen, init_position)                                                            #Parent init function
        
        self.image_change_threshold = 0
        image_walk_1 = pygame.image.load("images/BaladSprites/axeguy1.png")             #Must be the base image!
        image_walk_2 = pygame.image.load("images/BaladSprites/axeguy3.png")
        image_walk_3 = pygame.image.load("images/BaladSprites/axeguy4.png")
        image_attack_1 = pygame.image.load("images/BaladSprites/axeguyattack1.png")
        image_attack_2 = pygame.image.load("images/BaladSprites/axeguyattack2.png")
        image_attack_3 = pygame.image.load("images/BaladSprites/axeguyattack3.png")
        
        self.states = {0 : image_walk_1, 
                  1 : image_walk_2, 
                  2 : image_walk_3,
                  3 : image_attack_1,
                  4 : image_attack_2,
                  5 : image_attack_3}
        
        self.image_differences = {
                            0 : (0,0),
                            1 : (image_walk_2.get_width() - image_walk_1.get_width(), 0),
                            2 : (image_walk_3.get_width() - image_walk_1.get_width(), 0),
                            3 : (-(image_attack_1.get_width() - image_walk_1.get_width()), 0),
                            4 : (image_attack_2.get_width() - image_walk_1.get_width(), 0),
                            5 : (image_attack_3.get_width() - image_walk_1.get_width(), 0)}
        
        self.rect = self.states[0].get_rect()
        self.rect = self.rect.move(init_position)
        self.attack_rect = pygame.Rect(0,0,0,0)
        self.attack_rect.h = self.rect.h
        
        #Lifts the enemy onto ground level
        for rects in ground_rects:
            if self.rect.colliderect(rects):
                self.rect.bottom = rects.top


class enemy_type2(enemy):
    def __init__(self, screen, img_filename, init_position, ground_rects):
        """Initialiser for type 2 enemies"""      
        enemy.__init__(self, screen, init_position)                                       #Parent init function
        
        self.image_change_threshold = 0
        image_walk_1 = pygame.image.load("images/BaladSprites/swordguy1.png")             #Must be the base image!
        image_walk_2 = pygame.image.load("images/BaladSprites/swordguy2.png")
        image_walk_3 = pygame.image.load("images/BaladSprites/swordguy3.png")
        image_attack_1 = pygame.image.load("images/BaladSprites/swordguyattack1.png")
        image_attack_2 = pygame.image.load("images/BaladSprites/swordguyattack2.png")
        image_attack_3 = pygame.image.load("images/BaladSprites/swordguyattack3.png")
        
        self.states = {0 : image_walk_1, 
                  1 : image_walk_2, 
                  2 : image_walk_3,
                  3 : image_attack_1,
                  4 : image_attack_2,
                  5 : image_attack_3}
        
        self.image_differences = {
                            0 : (0,0),
                            1 : (image_walk_2.get_width() - image_walk_1.get_width(), 0),
                            2 : (image_walk_3.get_width() - image_walk_1.get_width(), 0),
                            3 : (-(image_attack_1.get_width() - image_walk_1.get_width()), 0),
                            4 : (image_attack_2.get_width() - image_walk_1.get_width(), 0),
                            5 : (image_attack_3.get_width() - image_walk_1.get_width(), 0)}
        
        self.rect = self.states[0].get_rect()
        self.rect = self.rect.move(init_position)
        self.attack_rect = pygame.Rect(0,0,0,0)
        self.attack_rect.h = self.rect.h
        
        #Lifts the enemy onto ground level
        for rects in ground_rects:
            if self.rect.colliderect(rects):
                self.rect.bottom = rects.top

#-------------------------------------------------------------------------
# Event Handler
#-------------------------------------------------------------------------
def EventHandler(balanar):
    """Keyboard input handler"""
    global move_screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.locals.USEREVENT:
            pass #print("done")
        if event.type == KEYDOWN:
            if event.key == K_q:
                pygame.quit()
            elif event.key == K_LEFT:
                balanar.movement_force = -1
            elif event.key == K_RIGHT:
                balanar.movement_force = 1
            elif event.key == K_DOWN:
                balanar.isattacking = 1
            elif event.key == K_UP:
                balanar.isjumping = True
                
        if event.type == KEYUP:
           	if event.key == K_LEFT:
           		balanar.movement_force = 0
           	elif event.key == K_RIGHT:
           		balanar.movement_force = 0
           		
#-------------------------------------------------------------------------
# Misc Functions
#-------------------------------------------------------------------------

def blit_ground (screen, current_ground_rects, texture):
    """ Blits the ground based on current_ground_rects"""    
    for rect in current_ground_rects:
        pygame.draw.rect(screen, GROUND_COLOUR, rect)
        cursor = Rect(rect)
        while (cursor.top < rect.bottom):
            screen.blit(texture, cursor)
            cursor.top += GROUND_UNIT_HEIGHT
            
def dec_to_bin(dec):
    """Converts decimal to binary"""
    count = 0
    binary = 0
    while (dec):
        rem = dec%2
        quo = dec/2
        binary += (10**count)*rem
        dec /= 2
        count += 1
    return binary
    
def create_ground(ground):   
    """Fills up the ground array by reading off the file
        Right now, the entire ground is filled at once""" 
    filestream = open('level', 'r')    
    temp = ''
    ground = []
    x = filestream.read(1)
    while x != '':
        if (x != ';'):
            temp = temp + x
        else:
            ground.append(int(temp))
            temp = ''
        x = filestream.read(1)
    return ground
    
def create_objects(ground, enemies, screen, enemy_img_filename, current_ground_rects):
    """Places enemies on the map based on ground"""
    for i in range(len(ground)):
        if ground[i] > 999:
            obj_type = ground[i]/1000
            ground[i] = ground[i]%1000
            obj_height = int(math.log(ground[i], 2))
            if (obj_type == 1):
                enemies.append(enemy_type2(screen, enemy_img_filename, (GROUND_UNIT_WIDTH*i, SCREEN_HEIGHT-((obj_height+1)*GROUND_UNIT_HEIGHT)), current_ground_rects))
                #pygame.draw.rect(screen, (0,0,0), (GROUND_UNIT_WIDTH*i, 200), (10,10))
    return ground, enemies
        
def create_ground_rects(ground, current_ground_rects):
    """Creates the actual ground object consisting of all rects"""
    #current_ground_rects = [] #NOO idea why it doesnt work over here. This has been pushed to the main loop
    count = 0
    global screen_offset
    
    for i in range(len(ground)):
        #raw_input('')
        temp = ground[i]%1000               #To remove any objects
        temp = dec_to_bin(temp)
        cells = []
        for j in range(8):
            cells.append(temp%10)
            temp /= 10
        cells.insert(0,1)
        j = 0
        no_of_units = 0
        ground_unit_top = SCREEN_HEIGHT
        while (j <= 8):                     # j=0 is below the screen!
            if cells[j] == 1:
                ground_unit_top = SCREEN_HEIGHT - ((j)*GROUND_UNIT_HEIGHT)
                no_of_units += 1
            elif cells[j] == 0 and cells[j-1] == 1:
                current_ground_rects.append(pygame.Rect(count*GROUND_UNIT_WIDTH-screen_offset, ground_unit_top, GROUND_UNIT_WIDTH, no_of_units*GROUND_UNIT_HEIGHT))
                no_of_units = 0
            elif cells[j] == 0:
                pass
            j += 1
        if cells[8] == 1: 
            current_ground_rects.append(pygame.Rect(count*GROUND_UNIT_WIDTH-screen_offset, ground_unit_top, GROUND_UNIT_WIDTH, no_of_units*GROUND_UNIT_HEIGHT))
        count += 1
            
def move_screen_func():
    """Function to pan the screen over to the next or previous screen"""
    global move_screen
    global screen_offset
    global offset_count
    if move_screen:
        if move_screen > 0 and screen_offset >= MAX_SCREEN_OFFSET: 
            move_screen = 0
            return
        if move_screen < 0 and screen_offset <= 0:
            move_screen = 0
            return
        screen_offset = screen_offset + move_screen*SCREEN_PAN_SPEED
        offset_count = offset_count+SCREEN_PAN_SPEED
        if offset_count >= SCREEN_WIDTH-(5*SCREEN_PAN_ZONE):    #5*SCREEN_PAN_ZONE to avoid the pendulem effect
            move_screen = 0
            offset_count = 0
            
def hit_enemy(enemy, balanar):        #For when an enemy hits balanar #TODO: Is this the right way to do it ??
    """Called when an enemy hits Balanar"""
    if balanar.hit_cooldown <= 0:
        balanar.health -= 10
        balanar.hit_cooldown = ENEMY_ATTACK_DELAY
        print balanar.health
    #print('ok')

def balanar_hit(enemy):      #For when Balanar hits an enemy :P     #TODO: Is this the right way to do this ??
    """Called when Balanar hits an enemy"""
    if enemy.hit_cooldown <= 0:
        enemy.health = enemy.health - 40
        enemy.hit_cooldown = 10
    #print ('Oh Yeah!')
    
def load_sound(name):               # The only Proper Exception Handled code right now :|
    """Function to load currently queued sound onto the mixer"""
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error, message:
        print 'Cannot load sound:', name
        raise SystemExit, message
    return sound
    
def fill_sound_queue(chnl, drum_chnl, loops, enemies):
    """Chooses the track to be played next according to the number of creeps on the screen right now"""
    enemy_count = 0
    for enemy in enemies:
        if (enemy.rect.left < SCREEN_WIDTH) and (enemy.rect.right > 0):
            enemy_count = enemy_count + 1
    
    if enemy_count > 5:
        chnl.queue(loops[3])
        drum_chnl.queue(loops[6])
    elif enemy_count > 3:
        chnl.queue(loops[3])
        drum_chnl.queue(loops[5])
    elif enemy_count > 0:
        chnl.queue(loops[2])
        drum_chnl.queue(loops[5])
    else:
        chnl.queue(loops[0])
        drum_chnl.queue(loops[0])
        
#-------------------------------------------------------------------------
# Game Loop
#-------------------------------------------------------------------------

def game():

    #-------------------------Game Initialization-------------------------

    enemy_img_filename = "images/enemy3.PNG"
    dummy_track = "sounds/empty.ogg"
    base_track_1 = "sounds/backtrack1.wav"
    base_track_2 = "sounds/backtrack2.wav"
    base_track_3 = "sounds/backtrack3.wav"
    base_track_4 = "sounds/backtrack4.wav"
    drum_track_1 = "sounds/drumtrack1.ogg"
    drum_track_2 = "sounds/drumtrack2.ogg"
    texture = pygame.image.load("images/BaladSprites/stone_texture.png")
    

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode ((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
 
    clock = pygame.time.Clock()
    
    global move_screen
    global offset_count
    global screen_offset
    offset_count = 0
    move_screen = 0
    screen_offset = 0
    
    pygame.mixer.music.load(base_track_1)       #Not sure if its better to run this as a music loop, or just leave it as a sound object.
    dummy_track = load_sound(dummy_track)
    drum_track_1 = load_sound(drum_track_1)
    drum_track_2 = load_sound(drum_track_2)
    base_track_1 = load_sound(base_track_1)
    base_track_2 = load_sound(base_track_2)
    base_track_3 = load_sound(base_track_3)
    base_track_4 = load_sound(base_track_4)
    
    loops = []
    loops.append(dummy_track)
    loops.append(base_track_1)
    loops.append(base_track_2)
    loops.append(base_track_3)
    loops.append(base_track_4)
    loops.append(drum_track_1)
    loops.append(drum_track_2)
    
    chnl = pygame.mixer.Channel(1)
    base_chnl = pygame.mixer.Channel(2)
    drum_chnl = pygame.mixer.Channel(3)
    chnl.set_endevent(pygame.locals.USEREVENT)        
    base_chnl.play(base_track_1, -1)                   #Starts playing automatically
    chnl.queue(dummy_track)
    drum_chnl.queue(dummy_track)
    #print chnl.get_length()
    
    balanar = ball(screen, (100,SCREEN_HEIGHT-GROUND_UNIT_HEIGHT), (0,0))
    
    ground = []
    ground = create_ground(ground)                      #Why do i need to assign the function to ground ? :/
        
    #Calculates current_ground_rects so that it can be fed to enemy.init
    current_ground_rects = []    
    create_ground_rects(ground, current_ground_rects)
    
    
    enemies = []
    ground, enemies = create_objects(ground, enemies, screen, enemy_img_filename, current_ground_rects)
    
    #enemies = []
    #for i in range (5, 16):
     #   enemies.append(enemy(screen, enemy_img_filename, (i*100, SCREEN_HEIGHT-GROUND_UNIT_HEIGHT), 2, current_ground_rects))
    #enemies.append(enemy(screen, enemy_img_filename, (500, SCREEN_HEIGHT-GROUND_UNIT_HEIGHT), 2, current_ground_rects))
    offset_count = 0
    
    running = True
    
     

    #-----------------------------The Game Loop---------------------------
    while running:
        #Delay
        pygame.time.wait(15)            #66 FPS

        #Event Handler
        EventHandler(balanar)
        
        current_ground_rects = [] 
        if move_screen:
            move_screen_func()
            
        create_ground_rects(ground, current_ground_rects)
        
        #Check for collision between balanar and an enemy
        for enemie in enemies:                              #'enemy' is the name of the class!
            if enemie.attack_rect.colliderect(balanar.rect):
                #print('hmm')
                hit_enemy(enemie, balanar)
        #Check for collision between balanar's attack rect and an enemy
            if enemie.rect.colliderect(balanar.attack_rect) and balanar.isattacking:
                balanar_hit(enemie)
        
        #Update all objects     
        balanar.update(current_ground_rects)
        for enemie in enemies:
            enemie.update(current_ground_rects, enemies, balanar)
            
        #Fill sound queue if required
        fill_sound_queue(chnl, drum_chnl, loops, enemies )

        #Fill background colour
        screen.fill(BG_COLOUR)       

        #Blit all objects to screen
        blit_ground(screen, current_ground_rects, texture)
        for enemie in enemies:
            enemie.blitme(screen)
        balanar.blitme(screen)

        #Flip the display buffer
        pygame.display.flip()
        
    filestream.close

game()
