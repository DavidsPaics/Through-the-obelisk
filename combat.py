import Engine.board
import pygame
import json
from chat import Chat
import random 
import math

import globalState
import useful_stuff

with open("./Resources/decks.json","r") as read_file:
    default_deck_1=json.loads(read_file.read())["Warrior"]

def combat(surface):
    pygame.mouse.set_visible(False)
    combat_menu_is_running=True
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    _board=Engine.board.Board((screen_width,screen_height))
    _board.setup_card_pile("Deck",(1867,1000),(105,160))
    _board.setup_card_pile("Graveyard",(53,1000),(105,160))
    _board.setup_hand()
    _board.hand.pos=[960,900]
    _board.import_deck(default_deck_1)
    pcard_1=_board.add_card_to_game("Warrior","Creature")

    _board.locations["OnTable"].append({
        "Card":pcard_1,
        "Position":[200,300]
    })
    for i in range(5):
        _board.draw_a_card()

    if globalState.networkManager != None:
        chat = Chat()

    #clock=pygame.time.Clock()
    while combat_menu_is_running:
        globalState.clock.tick()
        dt=globalState.clock.get_fps()
        if dt==0:
            dt=1
        dt=60/dt
        for event in pygame.event.get():
            if globalState.networkManager:
                chat.handle_event(event)
            if event.type==pygame.QUIT:
                combat_menu_is_running=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==3:
                    if _board.locations["Hand"]["Card Rendered On Top"]:
                        _board.locations["Hand"]["Card Rendered On Top"].flip(50)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F7:
                    globalState.debugMode = not globalState.debugMode
                
        _board.update(dt)
        _board.draw(dt)
        surface.blit(pygame.transform.scale(_board.surface,(screen_width,screen_height)),(0,0))

        if globalState.debugMode:
            useful_stuff.draw_fps_counter(surface, globalState.clock)
            surface.blit(useful_stuff.render_text(f"dt:  {round(dt,2)}",30,(255,255,0),"comicsansms"),(0,30))
        if globalState.networkManager:
            chat.draw(surface)
            globalState.networkManager.handle_events()

        pygame.display.flip()
#combat(screen)
