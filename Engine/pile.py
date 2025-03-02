from useful_stuff import *
class Pile:
    def __init__(self,name="Deck",pos=(0,0),custom_size=(210,320)):
        self.cards=[]
        self.name=name
        self.pos=pos
        self.custom_size=custom_size
    def draw(self,surface):
        
        if len(self.cards)>0:
            self.cards[-1].draw()
            if self.custom_size!=(210,320):
                center(pygame.transform.scale(self.cards[-1].sprite,self.custom_size),surface,self.pos[0],self.pos[1])       
            else:
                center(self.cards[-1].sprite,surface,self.pos[0],self.pos[1])       

class Hand(Pile):
    def __init__(self,pos,max_cards=10):
        super().__init__(name="Hand",pos=pos)
        self.max_cards=max_cards
        self.curvature_alpha=10
        self.curvature_beta=1.5
        self.curvature_gamma=10
        self.card_rendered_on_top=None
        self.selected_card=None
        self.original_card_pos=None #Used to determine spells n stuff
    def draw(self,board,delta=1):
        self.cards_in_hand=len(self.cards)
        if self.cards_in_hand>0:
            card_distance_from_mouse={}
            for I,iterated_card in enumerate(self.cards):
                if not iterated_card in [self.selected_card,self.card_rendered_on_top]:
                    central_offset=-(self.cards_in_hand-1)/2+I #Used to calculate rotation
                    iterated_card.draw(delta=delta)
                    destination_x=self.pos[0]-((self.cards_in_hand-1)/2-I)*170 #Determines card position in hand
                    destination_y=self.pos[1]+abs(central_offset)**self.curvature_beta*self.curvature_gamma #This is where the schizophrenia starts. I'll forget how this works once i look away, so i must not look away.
                    rotation=self.curvature_alpha*((self.cards_in_hand-1)/2-I)/((self.max_cards-1)/2)
                    if not iterated_card.vector_space_element.set_up:
                        iterated_card.vector_space_element.setup(destination_x,destination_y)
                    iterated_card.vector_space_element.move_with_easing_motion_to(destination_x,destination_y,75,rotation,delta)
                    center(pygame.transform.rotate(iterated_card.sprite,iterated_card.vector_space_element.rotation),
                        board.surface,iterated_card.vector_space_element.x,
                        iterated_card.vector_space_element.y)
                    #center(render_text((round(iterated_card.vector_space_element.x),round(iterated_card.vector_space_element.y)),30,(255,0,0)),self.surface,iterated_card.vector_space_element.x-self.camera_x,iterated_card.vector_space_element.y-self.camera_y)
                    #The line above is used in debug to determine card positions
                elif iterated_card==self.card_rendered_on_top:
                    saved_I=I
                
                dist_from_mouse=dist((iterated_card.vector_space_element.x,iterated_card.vector_space_element.y),board.mouse_pos)
                while dist_from_mouse in card_distance_from_mouse: #Ensures all the elements are of unique distance to the mouse position
                    dist_from_mouse+=0.000001
                card_distance_from_mouse[dist_from_mouse]=iterated_card #Sets up detection of which card is selected
            if self.card_rendered_on_top!=None: #Brings the topmost rendered card to the very end of the loop, ensuring it is rendered last
                I=saved_I
                iterated_card=self.card_rendered_on_top
                central_offset=-(self.cards_in_hand-1)/2+I
                iterated_card.draw(delta=delta)
                destination_x=self.pos[0]-((self.cards_in_hand-1)/2-I)*170 #Determines card position in hand
                destination_y=self.pos[1]+abs(central_offset)**self.curvature_beta*self.curvature_gamma #This is where the schizophrenia starts. I'll forget how this works once i look away, so i must not look away.
                rotation=self.curvature_alpha*((self.cards_in_hand-1)/2-I)/((self.max_cards-1)/2)
                if not iterated_card.vector_space_element.set_up:
                    iterated_card.vector_space_element.setup(destination_x,destination_y)
                if iterated_card!=self.selected_card:
                    iterated_card.vector_space_element.move_with_easing_motion_to(destination_x,destination_y,75,rotation,delta)
                    center(pygame.transform.rotate(iterated_card.sprite,iterated_card.vector_space_element.rotation),
                        board.surface,iterated_card.vector_space_element.x,
                        iterated_card.vector_space_element.y)
                else:
                    center(pygame.transform.rotate(iterated_card.sprite,iterated_card.vector_space_element.rotation),
                        board.surface,iterated_card.vector_space_element.x,
                        iterated_card.vector_space_element.y)
                
                #center(render_text((round(iterated_card.vector_space_element.x),round(iterated_card.vector_space_element.y)),30,(255,0,0)),self.surface,iterated_card.vector_space_element.x-self.camera_x,iterated_card.vector_space_element.y-self.camera_y)
                #The line above is used in debug to determine card positions
                
                if board.click[0]:
                    self.original_card_pos=(iterated_card.vector_space_element.x,iterated_card.vector_space_element.y)
                    self.selected_card=iterated_card
                    self.original_card_pos=(iterated_card.vector_space_element.x,iterated_card.vector_space_element.y)
            if len(board.open_GUIs)==0: #If there are any other GUIs, cards cannot be interacted with
                if self.selected_card!=None:
                    self.selected_card.vector_space_element.move_with_easing_motion_to(board.mouse_pos[0],board.mouse_pos[1],4,0,delta)
                    
                    if self.selected_card.parent.type=="Spell": #Basically every single card in the game
                        if not board.mouse_down[0]:
                            t=dist(self.original_card_pos,(self.selected_card.vector_space_element.x,self.selected_card.vector_space_element.y))
                            if t>140:
                                
                                board.play_a_card(self.selected_card.parent)
                                board.card_piles["Graveyard"].cards.append(self.selected_card)
                                self.cards.remove(self.selected_card)
                                                    
                            self.selected_card=None
                            self.card_rendered_on_top=None
                        else:
                            self.drag_screen_allowed=False
                else:
                    closest_card_to_mouse_distance=sorted(list(card_distance_from_mouse.keys()))[0]
                    if closest_card_to_mouse_distance<192 or self.selected_card!=None:
                        #self.surface.blit(render_text(closest_card_to_mouse_distance,30,(255,0,0)),(200,0))
                        self.card_rendered_on_top=card_distance_from_mouse[closest_card_to_mouse_distance]
                        self.drag_screen_allowed=False
                    else:
                        self.card_rendered_on_top=None
    
        