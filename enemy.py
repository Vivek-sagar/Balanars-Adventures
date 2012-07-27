import pygame
from pygame.sprite import Sprite

class enemy(Sprite):

    def __init__(self, screen, img_filename, init_position, speed, ground_rects):
        """Initialiser for all enemies"""
        
        self.screen = screen
        self.position = init_position
        self.image =  pygame.image.load(img_filename).convert()
        self.rect = self.image.get_rect()
        self.speed = speed
        self.direction = 1
        
        self.rect = self.rect.move(init_position)
        #Lifts the enemy onto ground level
        for rects in ground_rects:
            if self.rect.colliderect(rects):
                self.rect.bottom = rects.top
        
    def update(self, ground_rects):
        
        self.rect = self.rect.move(self.direction*self.speed, 0);
        for rect in ground_rects:
            if self.rect.colliderect(rect):
                if self.direction > 0:
                    self.rect.right = rect.left
                else:
                    self.rect.left = rect.right
                self.direction = -self.direction
                
            if self.rect.left < rect.right and rect.right - self.rect.left < 80:
                if self.rect.bottom < rect.top - 5:
                    self.direction = -self.direction
                    self.rect.left = rect.right
            elif self.rect.right > rect.left and self.rect.right - rect.left < 80:
                if self.rect.bottom < rect.top - 5:
                    self.direction = -self.direction
                    self.rect.right = rect.left
                    
        
    def blitme(self, screen):
        self.screen.blit(self.image, self.rect.topleft)

