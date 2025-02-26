import os
import json
import pygame
spell_data={}
for root, dirs, files in os.walk(r"Resources/spells/"):
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(root,file),"r") as f:
                spell_data[file[:-5]]=json.loads(f.read())

class Spell:
    def __init__(self,id):
        self.id=id #Will use this later, just needed for board things rn
        self.data=spell_data[self.id].copy()
        self.type="Spell"
    def draw(self):
        pass