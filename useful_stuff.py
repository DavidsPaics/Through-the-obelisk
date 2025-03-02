from random import *
from math import *
import pygame
def center(sprite,surface,x,y): #Centers a sprite on specific coordinates
   # print(sprite.get_width(),x)
    surface.blit(sprite,(x-sprite.get_width()/2,y-sprite.get_height()/2))
fonts={}
texts={}
def draw_fps_counter(screen,clock,font="comicsansms",size=20,color=(255,255,255),bold=False,italic=False): #Draws the fps counter
    fps=round(clock.get_fps())
    screen.blit(render_text("FPS: "+str(fps),size=size,color=color,font=font,bold=bold,italic=italic),(0,0))

def render_text(text="TEXT NOT PROVIDED",size=20,color=(255,255,255),font="comicsansms",bold=False,italic=False): #allows you to render text fast
    font_key=str(font)+str(size)
    text_key=str(font_key)+str(text)+str(color)
    if not font_key in fonts:
        try:
            fonts[font_key]=pygame.font.SysFont(font,int(size)) #Tries to load the file from the system
        except: #If that doesn't work
            try:
                fonts[font_key]=pygame.font.Font(font,int(size)) #Tries to load the font from a specified path, Don't do italic or bold unless very neccessary, bc pygame might do some strange stuff
            except:
                fonts[font_key]=pygame.font.SysFont("comicsansms")

    if not text_key in texts:
        texts[text_key]=fonts[font_key].render(str(text),1,color)
    return texts[text_key]
class Vector_Element:
    def __init__(self,dimensions=2): #Might extend this later into higher dimensions, but, for now, there is no reason to
        self.dimensions=dimensions
        self.set_up=False
    def setup(self,x,y,rotation=0):
        self.x=x
        self.y=y
        self.rotation=rotation
        self.vectors=[]
        self.set_up=True
    def move_with_easing_motion_to(self,destination_x,destination_y, easing_rate=20,destination_rotation=0,delta=1): #Higher easing rate means slower easing
        easing_rate/=delta
        self.x=(self.x*(easing_rate-1)+destination_x)/easing_rate
        self.y=(self.y*(easing_rate-1)+destination_y)/easing_rate
        self.rotation=(self.rotation*(easing_rate-1)+destination_rotation)/easing_rate
card_transparency_overlay=pygame.Surface((210,320))
card_transparency_overlay.set_colorkey((255,255,255))
card_transparency_color=(234,23,4)
card_transparency_overlay.fill((card_transparency_color))
pygame.draw.rect(card_transparency_overlay,(255,255,255),(0,0,210,320),0,15)