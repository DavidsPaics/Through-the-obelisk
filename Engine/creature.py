import os
import pygame
from useful_stuff import *
import json
creature_data={}
for root, dirs, files in os.walk(r"Resources/creatures/"):
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(root,file),"r") as f:
                creature_data[file[:-5]]=json.loads(f.read())
cached_sprite_pictures={}
class Creature:
    def __init__(self,_id):
        self.id=_id
        self.data=creature_data[self.id].copy()
        self.max_hp=self.data["Health"]
        self.hp=self.max_hp
        self.card=None
        self.sprite=[]
        for i in self.data["Animations"]:
            if not i["Sprite Path"] in cached_sprite_pictures:
                cached_sprite_pictures[i["Sprite Path"]]=pygame.image.load(i["Sprite Path"])
            self.sprite.append(i.copy())
        self.type="Creature"
        self.b_timer=0
    def draw(self,delta=1):
        if self.card!=None:
            self.b_timer+=delta
            #Currently only front is functional
            self.card.sides[self.card.data["Side On Top"]].fill((35,35,35))
            for i in range(11):
                cq=max(0,sin(-self.b_timer/100+i/11*tau))
                pygame.draw.rect(self.card.sides[self.card.data["Side On Top"]],(5,5+cq*125,5+cq*250),(105-i*10.5-cq*10,160-i*16-cq*16,i*21+cq*21,i*32+cq*32),2,ceil(i*1.5))
            for i in self.sprite:
                x_position=i["X Center"]+105
                y_position=i["Y Center"]+160
                if "Fi" in i:
                    i["Fi"]+=i["Omega"]*delta
                    x_position+=cos(i["Fi"])*i["X Movement"]
                    y_position+=sin(i["Fi"])*i["Y Movement"]
                if "X Fi" in i:
                    i["X Fi"]+=i["Omega"]/delta
                    x_position+=cos(i["Fi"])*i["X Movement"]
                if "Y Fi" in i:
                    i["Y Fi"]+=i["Omega"]/delta
                    y_position+=sin(i["Y Fi"])*i["Y Movement"]
                if self.card.data["Side On Top"]==i["Side"]:
                    center(cached_sprite_pictures[i["Sprite Path"]],self.card.sides[i["Side"]],x_position,y_position)
                else:
                    pass
            self.card.sides[self.card.data["Side On Top"]].blit(card_transparency_overlay,(0,0))
            #center()