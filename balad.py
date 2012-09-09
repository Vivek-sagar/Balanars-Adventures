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
BG_COLOUR = 200, 200, 200
GROUND_UNIT_WIDTH, GROUND_UNIT_HEIGHT = 80, 50
GROUND_COLOUR = (50, 25, 25)
HEALTH_BAR_COLOUR = (200, 255, 100)

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

class ball(Sprite):

    image = None
    movement_force = 0
    isjumping = False
    

    def __init__(self, screen, init_position, speed):
        """Initialise the ball"""
        
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
        self.rect = image_walk_1.get_rect()
        #self.image.set_colorkey((255, 248, 255))   #Required only if the image isnt transparent
        self.attack_rect = pygame.Rect(0,0,0,0)
        self.attack_rect.width, self.attack_rect.height = 0, self.rect.height
        #Pull Balanar back onto the screen
        init_position = tuple(map(operator.add, init_position, (0, -self.rect.height)))
        self.rect = self.rect.move(init_position)
        self.attack_rect.topleft = self.rect.topleft
        self.rect.inflate(-5, -5)
        self.isgrounded = True
        self.directionchanged = False
        self.isattacking = 0
        self.image_change_threshold = 0
        self.direction = 1
        self.health = 100
        self.states = {0 : image_walk_1, 
                       1 : image_walk_2, 
                       2 : image_walk_3,
                       3 : image_attack_1,
                       4 : image_attack_2}
        self.image_differences = {0 : 0,
                            1 : image_walk_2.get_width() - image_walk_1.get_width(),
                            2 : image_walk_3.get_width() - image_walk_1.get_width(),
                            3 : image_attack_1.get_width() - image_walk_1.get_width(),
                            4 : image_attack_2.get_width() - image_walk_1.get_width()}
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
            self.state = 0
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
            self.state = 4
            self.attack_rect.width = 5*self.isattacking
            if self.isattacking > 5:
                self.state = 5
            if self.isattacking > 10:
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
            
        self.image = pygame.transform.flip(self.image, True, False)     #Balanar is the only one facing the other way in the beginning :/  #TODO: Should probably change the image
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            shift = 0
            
        self.screen.blit(self.image, (self.rect.left-shift, self.rect.top)) 
        
        #pygame.draw.rect(screen, (0,0,0), self.rect)              
        #pygame.draw.rect(screen, (0,0,0), self.attack_rect)
        
class enemy(Sprite):

    def __init__(self, screen, img_filename, init_position, speed, ground_rects):
        """Initialiser for all enemies"""        
        self.screen = screen
        self.position = init_position
        #self.image =  pygame.image.load(img_filename).convert()
        
        self.speed = speed
        self.direction = -1
        self.health = 100 
        #self.image.set_colorkey((255, 255, 255))     
        self.hit_cooldown = 0
        self.isattacking = 0
        
        self.image_change_threshold = 0
        image_walk_1 = pygame.image.load("images/BaladSprites/axeguy1.png")
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
        self.state = 0
        
        self.image_differences = {0 : 0,
                            1 : image_walk_2.get_width() - image_walk_1.get_width(),
                            2 : image_walk_3.get_width() - image_walk_1.get_width(),
                            3 : -(image_attack_1.get_width() - image_walk_1.get_width()),
                            4 : image_attack_2.get_width() - image_walk_1.get_width(),
                            5 : image_attack_3.get_width() - image_walk_1.get_width()}
        
        self.rect = self.states[0].get_rect()
        self.rect = self.rect.move(init_position)
        self.attack_rect = pygame.Rect(0,0,0,0)
        self.attack_rect.h = self.rect.h
        
        #Lifts the enemy onto ground level
        for rects in ground_rects:
            if self.rect.colliderect(rects):
                self.rect.bottom = rects.top
        
    def update(self, ground_rects, enemies, balanar):
        """Updates enemy position, checking for obstacles and allowing for screen panning""" 
        
        if move_screen:
            self.rect = self.rect.move(-(move_screen*SCREEN_PAN_SPEED), 0) 
            
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            return
        
        #If Enemy is currently attacking, dont move!    
        if not self.isattacking:
            if self.direction == 1:
                if balanar.rect.left < self.rect.right + 50 and balanar.rect.left > self.rect.right:
                    self.isattacking = True
            elif self.direction == -1:
                if balanar.rect.right > self.rect.left - 50 and balanar.rect.right < self.rect.left:
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
                self.attack_rect.width = 5*self.isattacking
            if self.isattacking < 5:
                self.state = 3
            elif self.isattacking < 10:
                self.state = 4
            elif self.isattacking < 15:
                self.state = 5
            if self.isattacking > 100:
                self.attack_rect.width = 0
                self.isattacking = 0
                    
        
    def blitme(self, screen):
        """Blits the enemy onto the screen"""
        self.image = self.states[self.state]
        shift = self.image_differences[self.state]
        
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            if shift > 0: shift = 0
            #self.screen.blit(self.image, self.rect.topleft)
        else:    
            if shift < 0: shift = 0                             #To take care of the sword going the other way
        self.screen.blit(self.image, (self.rect.left + (self.direction*shift), self.rect.top))
        #pygame.draw.rect(screen, (0,0,0), self.attack_rect)
        pygame.draw.rect(screen, HEALTH_BAR_COLOUR, pygame.Rect(self.rect.left, self.rect.top-20, self.rect.width*(self.health/100.0), 10))
        

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
            print("done")
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
         
def create_ground_rects(ground, current_ground_rects):
    """Creates the actual ground object consisting of all rects"""
    #current_ground_rects = [] #NOO idea why it doesnt work over here. This has been pushed to the main loop
    count = 0
    global screen_offset
    
    for i in range(len(ground)):
        ground_base = (ground[i] - ground[i]%100)/100
        gap = ((ground[i]-ground_base*100) - (ground[i]-ground_base*100)%10)/10
        cloud_size = ground[i]%10
        current_ground_rects.append(pygame.Rect(count*GROUND_UNIT_WIDTH-screen_offset, SCREEN_HEIGHT - ground_base*GROUND_UNIT_HEIGHT, GROUND_UNIT_WIDTH, ground_base*GROUND_UNIT_HEIGHT))
        if gap != 0:            #This unit contains a cloud
            current_ground_rects.append(pygame.Rect(count*GROUND_UNIT_WIDTH-screen_offset, SCREEN_HEIGHT - (ground_base+gap+cloud_size)*GROUND_UNIT_HEIGHT, GROUND_UNIT_WIDTH, cloud_size*GROUND_UNIT_HEIGHT))
        count = count+1
            
            
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
            
def hit_enemy(enemy, balanar):        #For when an enemy hits balanar
    pass

def balanar_hit(enemy):      #For when Balanar hits an enemy :P
    if enemy.hit_cooldown == 0:
        enemy.health = enemy.health - 40
        enemy.hit_cooldown = 10
    #print ('Oh Yeah!')
    
def load_sound(name):               # The only Proper Exception Handled code right now :|
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
    
    #Calculates current_ground_rects so that it can be fed to enemy.init
    current_ground_rects = []    
    create_ground_rects(ground, current_ground_rects)
    
    enemies = []
    for i in range (5, 16):
        enemies.append(enemy(screen, enemy_img_filename, (i*100, SCREEN_HEIGHT-GROUND_UNIT_HEIGHT), 2, current_ground_rects))
    
    offset_count = 0
    
    running = True
    
     

    #-----------------------------The Game Loop---------------------------
    while running:
        #Delay
        pygame.time.wait(15)

        #Event Handler
        EventHandler(balanar) #Has to return a value because move_screen is an immutable datatype and so, wont be changed in EventHandler 

        #Update all objects 
        current_ground_rects = [] 
        if move_screen:
            move_screen_func()

        create_ground_rects(ground, current_ground_rects)
        
        #Check for collision between balanar and an enemy
        for enemy1 in enemies:
            if enemy1.rect.colliderect(balanar.rect):
                hit_enemy(enemy1)
        #Check for collision between balanar's attack rect and an enemy
            if enemy1.rect.colliderect(balanar.attack_rect) and balanar.isattacking:
                balanar_hit(enemy1)
            
        balanar.update(current_ground_rects)
        for enemy1 in enemies:
            enemy1.update(current_ground_rects, enemies, balanar)
            
        #Fill sound queue if required
        fill_sound_queue(chnl, drum_chnl, loops, enemies )

        #Fill background colour
        screen.fill(BG_COLOUR)       

        #Blit all objects to screen
        blit_ground(screen, current_ground_rects, texture)
        for enemy1 in enemies:
            enemy1.blitme(screen)
        balanar.blitme(screen)

        #Flip the display buffer
        pygame.display.flip()
        
    filestream.close

game()
