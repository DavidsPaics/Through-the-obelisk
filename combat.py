import board
import pygame
import json
import random 
import math

with open("./Resources/decks.json","r") as read_file:
    default_deck_1=json.loads(read_file.read())["Warrior"]

def combat(surface):
    combat_menu_is_running=True
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    _board=board.Board((screen_width,screen_height))
    _board.setup_card_pile("Deck",(1920,1080))
    _board.setup_card_pile("Graveyard",(0,1080))
    _board.setup_hand()
    _board.locations["Hand"]["Position"]=[960,900]
    _board.import_deck(default_deck_1)
    
    for i in range(5):
        _board.draw_a_card()

    clock=pygame.time.Clock()
    while combat_menu_is_running:

        dt=clock.tick()
        if dt==0:
            dt=10
        dt=10/dt
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                combat_menu_is_running=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==3:
                    if _board.locations["Hand"]["Card Rendered On Top"]:
                        _board.locations["Hand"]["Card Rendered On Top"].flip(50)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F7:
                    combat_menu_is_running=False
        _board.update()
        _board.draw(dt)
        surface.blit(pygame.transform.scale(_board.surface,(screen_width,screen_height)),(0,0))
        pygame.display.flip()
#combat(screen)
