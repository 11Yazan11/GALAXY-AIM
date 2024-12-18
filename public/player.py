import pygame
import socketio
import sys
import math
import ctypes

class Player:
    def __init__(self, game, x, y, w, h, color, name, angle, bullets, kills, id):
        self.game = game
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.name = name
        self.angle = angle
        self.bullets = bullets
        self.kills = kills
        self.id = id
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
    def draw(self):
        pygame.draw.rect(self.game.screen, self.color, self.rect)
        # Handle name, angle, bullets, kills, (and id) later.

