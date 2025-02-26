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
cached_sprite_pictures
class Creature:
    def __init__(self,_id):
        self.id=_id
        self.data=creature_data[self.id].copy()
        self.max_hp=self.data["Health"]
        self.hp=self.max_hp
        self.card=None
    def draw(self):
        if self.card!=None:
            self.card.sides["Front"].fill((12,23,34))
            center(self.sprite,self.card.sides["Front"],105,160)
    