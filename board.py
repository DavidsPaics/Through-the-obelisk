from card import *
import creature
import spell
import sys
import logging
import os

class Board:
    def __init__(self,inherited_screen_size=(1920,1080)):
        self.locations={  #Contains all the data about where cards can exist
            "Board":[],
            "OnTable":[]
        }
        self.card_piles=[]
        self.surface=pygame.Surface((1920,1080))
        self.camera_x=0
        self.camera_y=0 #Puts the camera about right

        self.mouse_pos=[0,0] #Set to this for now, as it causes a crash if unset
        self.r_mouse_pos=[0,0]
        self.mouse_pos_multiplier=[[1920,1080][i]/inherited_screen_size[i] for i in range(2)] #Adjusts the mouse correctly
        self.drag_screen_allowed=True #Sets whether or not if you drag something, it will be dragged across the screen
        self.mouse_down=[False for i in range(3)]
        self.ctimer=[0,0,0]
        self.click=[False,False,False] #Can accurately detect the first frame when the mouse button is clicked
        self.game_over=False
        self.open_GUIs={}

        loadCardImages()

        self.frame=0
        self.tech={} #Current Effects happening on board
    

    def setup_hand(self,max_cards=10):
        self.locations["Hand"]={
            "Position":[0,500], #Can be changed later if needed
            "Max Cards":max_cards,
            "Cards":[],
            "Curvature Settings":{ #Defines some stuff about how cards are held in hand, It's best not to think about this that much right now
                "Alpha":10, #How much the cards are bent
                "Beta":1.5, #Exponential of how far down the cards go, it's best to be kept small at larger number of cards
                "Gamma":10 #Card Descent Multiplier in pixels
            },
            "Card Rendered On Top":None,
            "Selected Card":None,
            "Original Card Pos":None, #Used to determine whether or not a spell is played from hand
        }
    def setup_card_pile(self,card_pile_name="Deck",pos=(900,0)):
        self.locations[card_pile_name]={
            "Position":pos,
            "Cards":[]
        }
        self.card_piles.append(card_pile_name)
    def draw(self,delta=1):
        #self.camera_x*=1.01
        #self.camera_y*=1.01
        self.frame+=1
        self.drag_screen_allowed=False
        self.surface.fill((25,5,5)) #Fills the board with a nice color to draw on
        #Draws the board at the very bottom
        for i in self.locations["OnTable"]:
            i["Card"].draw(delta=delta)
            #logging.info(i)
            #pygame.image.save(i["Card"].sprite,"test.png")
            center(i["Card"].sprite,self.surface,i["Position"][0],i["Position"][1])
        pygame.draw.circle(self.surface,(255,255,255),self.mouse_pos,10)
             
        #Draws all the block positions and the blocks themselves
        hand_locked=False #Flag which determines if cards can be played from hand, useful for coop operations
        for iterated_card_pile in self.card_piles: #Draws the top card of every card pile
            selected_card_pile=self.locations[iterated_card_pile]
            cards_in_pile=len(selected_card_pile["Cards"])
            if cards_in_pile>0:
                selected_card_pile["Cards"][-1].draw()
                center(selected_card_pile["Cards"][-1].sprite,self.surface,selected_card_pile["Position"][0]-self.camera_x,selected_card_pile["Position"][1]-self.camera_y)                
        if "Hand" in self.locations:
           # self.locations["Hand"]["Position"]=[self.camera_x+surface.get_width()/2,self.camera_y+surface.get_height()/2+500]
            self.cards_in_hand=len(self.locations["Hand"]["Cards"])
            if self.cards_in_hand>0:
                curvature_settings=self.locations["Hand"]["Curvature Settings"]
                card_distance_from_mouse={}
                for I,iterated_card in enumerate(self.locations["Hand"]["Cards"]):
                    #print(iterated_card.vector_space_element.x,iterated_card.vector_space_element.y)
                    if not iterated_card in [self.locations["Hand"]["Selected Card"],self.locations["Hand"]["Card Rendered On Top"]]:
                        central_offset=-(self.cards_in_hand-1)/2+I #Used to calculate rotation
                        iterated_card.draw(delta=delta)
                        destination_x=self.locations["Hand"]["Position"][0]-((self.cards_in_hand-1)/2-I)*170 #Determines card position in hand
                        destination_y=self.locations["Hand"]["Position"][1]+abs(central_offset)**curvature_settings["Beta"]*curvature_settings["Gamma"] #This is where the schizophrenia starts. I'll forget how this works once i look away, so i must not look away.
                        rotation=curvature_settings["Alpha"]*((self.cards_in_hand-1)/2-I)/((self.locations["Hand"]["Max Cards"]-1)/2)
                        if not iterated_card.vector_space_element.set_up:
                            iterated_card.vector_space_element.setup(destination_x,destination_y)
                        iterated_card.vector_space_element.move_with_easing_motion_to(destination_x,destination_y,75,rotation,delta)
                        #print(iterated_card.sprite)
                        center(pygame.transform.rotate(iterated_card.sprite,iterated_card.vector_space_element.rotation),
                            self.surface,iterated_card.vector_space_element.x-self.camera_x,
                            iterated_card.vector_space_element.y-self.camera_y)
                        #center(render_text((round(iterated_card.vector_space_element.x),round(iterated_card.vector_space_element.y)),30,(255,0,0)),self.surface,iterated_card.vector_space_element.x-self.camera_x,iterated_card.vector_space_element.y-self.camera_y)
                        #The line above is used in debug to determine card positions
                    elif iterated_card==self.locations["Hand"]["Card Rendered On Top"]:
                        saved_I=I
                    
                    dist_from_mouse=dist((iterated_card.vector_space_element.x,iterated_card.vector_space_element.y),self.mouse_pos)
                    while dist_from_mouse in card_distance_from_mouse: #Ensures all the elements are of unique distance to the mouse position
                        dist_from_mouse+=0.000001
                    card_distance_from_mouse[dist_from_mouse]=iterated_card #Sets up detection of which card is selected
                    #if dist_from_mouse<192: #If is within a circle of the mouse cursor
                    #    self.drag_screen_allowed=False #You can't drag the screen
                if self.locations["Hand"]["Card Rendered On Top"]!=None: #Brings the topmost rendered card to the very end of the loop, ensuring it is rendered last
                    I=saved_I
                    iterated_card=self.locations["Hand"]["Card Rendered On Top"]
                    central_offset=-(self.cards_in_hand-1)/2+I
                    iterated_card.draw(delta=delta)
                    destination_x=self.locations["Hand"]["Position"][0]-((self.cards_in_hand-1)/2-I)*170 #Determines card position in hand
                    destination_y=self.locations["Hand"]["Position"][1]+abs(central_offset)**curvature_settings["Beta"]*curvature_settings["Gamma"] #This is where the schizophrenia starts. I'll forget how this works once i look away, so i must not look away.
                    rotation=curvature_settings["Alpha"]*((self.cards_in_hand-1)/2-I)/((self.locations["Hand"]["Max Cards"]-1)/2)
                    
                    if not iterated_card.vector_space_element.set_up:
                        iterated_card.vector_space_element.setup(destination_x,destination_y)
                    if iterated_card!=self.locations["Hand"]["Selected Card"]:
                        iterated_card.vector_space_element.move_with_easing_motion_to(destination_x,destination_y,75,rotation,delta)
                        center(pygame.transform.rotate(iterated_card.sprite,iterated_card.vector_space_element.rotation),
                            self.surface,iterated_card.vector_space_element.x-self.camera_x,
                            iterated_card.vector_space_element.y-self.camera_y)
                    else:
                        center(pygame.transform.rotate(iterated_card.sprite,iterated_card.vector_space_element.rotation),
                            self.surface,iterated_card.vector_space_element.x-self.camera_x,
                            iterated_card.vector_space_element.y-self.camera_y)
                    
                    #center(render_text((round(iterated_card.vector_space_element.x),round(iterated_card.vector_space_element.y)),30,(255,0,0)),self.surface,iterated_card.vector_space_element.x-self.camera_x,iterated_card.vector_space_element.y-self.camera_y)
                    #The line above is used in debug to determine card positions
                    
                    if self.mouse_down[0]:
                        self.locations["Hand"]["Original Card Pos"]=(iterated_card.vector_space_element.x,iterated_card.vector_space_element.y)
                        self.locations["Hand"]["Selected Card"]=iterated_card
                        self.locations["Hand"]["Selected Card Original Position"]=(iterated_card.vector_space_element.x,iterated_card.vector_space_element.y)
                if len(self.open_GUIs)==0: #If there are any other GUIs, cards cannot be interacted with
                    if self.locations["Hand"]["Selected Card"]!=None:
                        self.selected_card=self.locations["Hand"]["Selected Card"]
                        self.selected_card.vector_space_element.move_with_easing_motion_to(self.mouse_pos[0],self.mouse_pos[1],4,0,delta)
                        
                        if self.selected_card.parent.type=="Spell": #Basically every single card in the game
                            if not self.mouse_down[0]:
                                if dist(self.locations["Hand"]["Original Card Pos"],(self.selected_card.vector_space_element.x,self.selected_card.vector_space_element.y))<140:
                                    
                                    self.play_a_card(self.selected_card.parent)
                                    self.locations["Graveyard"]["Cards"].append(self.selected_card)
                                    self.locations["Hand"]["Cards"].remove(self.selected_card)
                                                        
                                self.locations["Hand"]["Selected Card"]=None
                                self.locations["Hand"]["Card Rendered On Top"]=None
                            else:
                                self.drag_screen_allowed=False
                    else:
                        closest_card_to_mouse_distance=sorted(list(card_distance_from_mouse.keys()))[0]
                        if closest_card_to_mouse_distance<192 or self.locations["Hand"]["Selected Card"]!=None:
                            #self.surface.blit(render_text(closest_card_to_mouse_distance,30,(255,0,0)),(200,0))
                            self.locations["Hand"]["Card Rendered On Top"]=card_distance_from_mouse[closest_card_to_mouse_distance]
                            self.drag_screen_allowed=False
                        else:
                            self.locations["Hand"]["Card Rendered On Top"]=None
        
        if "Interacting With Card On Field" in self.open_GUIs:
            interacted_card=self.open_GUIs["Interacting With Card On Field"]["Selected Card"]
            if interacted_card.parent.type=="Creature":
                possible_actions=["Close"]
                #A Nice little block checking all the cases for actions that a creature can do. 
                if interacted_card.parent.attack>0:             possible_actions.append("Attack")
                for I,i in enumerate(possible_actions):
                    action_center_x=960-((len(possible_actions)-1)/2-I)*200
                    pygame.draw.rect(self.surface,(15,15,15),(action_center_x-80,820,160,60),0,10)
                    center(render_text(i,20,(255,255,255)),self.surface,action_center_x,850)
                    if not (abs(self.r_mouse_pos[0]-action_center_x)<80 and abs(self.r_mouse_pos[1]-835)<30): #If The mouse hovers over this button
                        pygame.draw.rect(self.surface,(125,125,125),(action_center_x-80,820,160,60),5,10)
                    else:
                        pygame.draw.rect(self.surface,(175,175,125),(action_center_x-80,820,160,60),5,10) #It Gets a different color
                        if self.click[0]:
                            if i=="Close":
                                del self.open_GUIs["Interacting With Card On Field"]
    def update(self): #Updates the board so that 
        self.mouse_rel=pygame.mouse.get_rel()
        self.mouse_down=pygame.mouse.get_pressed()
        self.mouse_pos=pygame.mouse.get_pos()
        self.r_mouse_pos=[self.mouse_pos[i]*self.mouse_pos_multiplier[i] for i in range(2)] #adjusts to the change in resolution
        self.mouse_pos=[self.r_mouse_pos[0]+self.camera_x,self.r_mouse_pos[1]+self.camera_y] #adds the position of camera to the mouse, allowing simple access. 
        if self.mouse_down[0] and self.drag_screen_allowed:
            self.camera_x-=self.mouse_rel[0]
            self.camera_y-=self.mouse_rel[1]
        self.ctimer=[(self.ctimer[i]+1)*self.mouse_down[i] for i in range(3)]
        self.click=[self.ctimer[i]==1 for i in range(3)]
    def add_card_to_game(self,plain_card_id,plain_card_type="Creature"): #Adds a new card to the game, returns the created card
        new_card=Card() 

        if plain_card_type=="Spell":
            new_object_manager=spell.Spell(plain_card_id)
            new_object_manager.card=new_card
            new_object_manager.draw() #Draws the new card at the start, so it is visible at all
            new_card.parent=new_object_manager #Also attributes the parent to whatever is locked inside the card
        elif plain_card_type=="Creature":
            new_object_manager=creature.Creature(plain_card_id)
            new_object_manager.card=new_card
            new_object_manager.draw() #Draws the new card at the start, so it is visible at all
            new_card.parent=new_object_manager #Also attributes the parent to whatever is locked inside the card
        
        if plain_card_id + "-front" in cardSideImages:
            new_object_manager.card.side_from_surface(cardSideImages[plain_card_id + "-front"], "Front")
        else:
            new_object_manager.card.side_from_surface(cardSideImages["default-front"], "Front")

        if plain_card_id + "-back" in cardSideImages:
             new_object_manager.card.side_from_surface(cardSideImages[plain_card_id + "-back"], "Back")
        else:
            new_object_manager.card.side_from_surface(cardSideImages["default-back"], "Back")

        return new_object_manager.card
        

    def draw_a_card(self,from_pile="Deck"): #Takes a card from a deck, adds it to the hand, the animation engine itself figures out how to animate that
        if len(self.locations[from_pile]["Cards"])>0:
            drawn_card=self.locations[from_pile]["Cards"][0]
            self.locations[from_pile]["Cards"].pop(0)
            if len(self.locations["Hand"]["Cards"])<self.locations["Hand"]["Max Cards"]:
                self.locations["Hand"]["Cards"].append(drawn_card)
                drawn_card.vector_space_element=Vector_Element()
                drawn_card.vector_space_element.setup(self.locations[from_pile]["Position"][0],self.locations[from_pile]["Position"][1])
                drawn_card.iflip("Back")
                drawn_card.clear_animations()
                drawn_card.flip(40,"Front")
                drawn_card.draw()
            else:
                return "Full Hand"
        else:
            return "Empty Pile"
    def import_deck(self,json_deck_list=[],to_card_pile="Deck"): #Imports deck from a decklist
        # Ideal decklist should be a list consisting of cards in the following format
        # {"Name":"CARD NAME","Type":"CARD TYPE"}
        # This doesn't shuffle the deck, so it has to be done manually
        if not to_card_pile in self.locations:
            self.setup_card_pile(to_card_pile)
        for iterated_card_packed in json_deck_list:
            new_card=self.add_card_to_game(iterated_card_packed["ID"],iterated_card_packed["Type"])
            new_card.iflip("Back")
            self.locations[to_card_pile]["Cards"].append(new_card)
    def shuffle_card_pile(self,card_pile="Deck"):
        shuffle(self.locations[card_pile]["Cards"])
    def check_for_target(self,locations=[]):
        possible_cards=[]
        #First finds all the cards, then removes all the ones that don't count. 
        for i in self.locations:
            if not i in ["Board"]: #Custom Card Location
                if len(locations)>0:
                    if i in locations:
                        #print(i,locations)
                        for card in self.locations[i]["Cards"]:
                            possible_cards.append(card)
                    else:
                        continue
                else:
                    for card in i["Cards"]:
                        possible_cards.append(card)
            else:
                if len(locations)>0:
                    if "Board" in locations:
                        for space in self.locations[i]:
                            if space["Space"].card!=None:
                                possible_cards.append(space["Space"].card)

        #print(possible_cards)
        return possible_cards
    

       #Effect Building Starts Here
    #Warning: No Return after this

    #You are now entering the wastelands
    #Population: 2 of my braincells (currently)


    def play_a_card(self,card):
        self.card_played=card
        if card.type=="Spell":
            self.caster=card
            if "Effects" in card.data:
                if "On Play" in card.data["Effects"]:
                    for effect in card.data["Effects"]["On Play"]:
                        self.run_effect(effect)

    def run_effect(self,effect):
        #print(effect)
        if effect["Type"]=="Modify Value Creature":
            for target in self.effect_target_creatures(effect):
                if effect["Attribute"] in target.parent.data["Attributes"]:
                    if effect["Operation"]=="+":
                        target.parent.data["Attributes"][effect["Attribute"]]+=self.get_value(effect["Value"])
                    if effect["Operation"]=="-":
                        target.parent.data["Attributes"][effect["Attribute"]]-=self.get_value(effect["Value"])
                    if effect["Operation"]=="*":
                        target.parent.data["Attributes"][effect["Attribute"]]*=self.get_value(effect["Value"])
                        target.parent.data["Attributes"][effect["Attribute"]]=round(target.parent.data["Attributes"][effect["Attribute"]],2)
                    if effect["Operation"]=="/":
                        target.parent.data["Attributes"][effect["Attribute"]]/=self.get_value(effect["Value"])
                        target.parent.data["Attributes"][effect["Attribute"]]=round(target.parent.data["Attributes"][effect["Attribute"]],2)
                    print(target.parent.data)
        if effect["Type"]=="If":
            for target in self.effect_target_creatures(effect):
                if effect["Condition"]=="Has Tribe":
                    if target.parent.data["Tribe"]==effect["Tribe Required"]:
                        self.run_effect(effect["Then"])
        if effect["Type"]=="Multiple Effects":
            for new_effect in effect["Effects"]:
                self.run_effect(new_effect)
        if effect["Type"]=="Assign Variable":
            if "Count" in effect:
                try:
                    self.caster.data["Attributes"][effect["Name"]]=len(self.effect_target_creatures({"Target":effect["Count"]}))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error:",exc_type,e, fname, exc_tb.tb_lineno)
                    print("Invalid Count")
                    self.caster.data["Attributes"][effect["Name"]]=0
            if "Attribute Target" in effect:
                try:
                    self.caster.data["Attributes"][effect["Name"]]=self.effect_target_creatures({"Target":effect["Attribute Target"]})[0].parent.data["Attributes"][effect["Taken Attribute"]]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error:",exc_type,e, fname, exc_tb.tb_lineno)
                    print("Invalid Attribute Target")
                    self.caster.data["Attributes"][effect["Name"]]=0
            if "Target" in effect:
                try:
                    self.caster.data["Attributes"][effect["Name"]]=self.effect_target_creatures({"Target":effect["Target"]})
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error:",exc_type,e, fname, exc_tb.tb_lineno)
                    print("Invalid Target")
                    self.caster.data["Attributes"][effect["Name"]]=self.check_for_target()
            print(effect["Name"],self.caster.data["Attributes"][effect["Name"]])
        if effect["Type"]=="Destroy Creature": #Used In Shops, Will be likely removed in total, due to lack of support in general
            destroyable_card=self.effect_target_creatures({"Target":effect["Target"]})
            if len(destroyable_card)>0:
                del destroyable_card[0].parent
                destroyable_card[0].space["Space"].card=None
                del destroyable_card[0]
        if effect["Type"]=="Modify Global Variable":
            if not effect["Name"] in self.data:
                self.data[effect["Name"]]=0
            if effect["Operation"]=="+":
                self.data[effect["Name"]]+=self.get_value(effect["Value"])
            if effect["Operation"]=="-":
                self.data[effect["Name"]]-=self.get_value(effect["Value"])
            if effect["Operation"]=="*":
                self.data[effect["Name"]]*=self.get_value(effect["Value"])
                self.data[effect["Name"]]=round(self.data[effect["Name"]],2)
            if effect["Operation"]=="/":
                self.data[effect["Name"]]/=self.get_value(effect["Value"])
                self.data[effect["Name"]]=round(self.data[effect["Name"]],2)
        if effect["Type"]=="Draw Cards":
            for i in range(effect["Cards Drawn"]):
                self.draw_a_card()
