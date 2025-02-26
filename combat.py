import board
import pygame
import json
import random 
import math
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
with open("Resources/decks.json","r") as read_file:
    default_deck_1=json.loads(read_file.read())["Warrior"]
def combat(surface):
    combat_menu_is_running=True
    _board=board.Board()
    _board.setup_card_pile("Deck")
    _board.import_deck(default_deck_1)
    while combat_menu_is_running:
        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                combat_menu_is_running=False
        surface.fill((0,0,0))
        _board.draw(screen)
        pygame.display.update()
combat(screen)