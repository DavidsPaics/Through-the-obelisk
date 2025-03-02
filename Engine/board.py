from Engine.card import *
import Engine.creature as creature
import Engine.spell as spell
import sys
import logging
import os
import Engine.pile
class Board:
    def __init__(self,inherited_screen_size=(1920,1080)):
        self.locations={  #Contains all the data about where cards can exist
            "Board":[],
            "OnTable":[]
        }
        self.card_piles={} #Stored as a dict so that you can get a card pile by its name
        self.surface=pygame.Surface((1920,1080))
        self.camera_x=0
        self.camera_y=0 #Puts the camera about right

        self.mouse_pos=[0,0] #Set to this for now, as it causes a crash if unset
        self.r_mouse_pos=[0,0]
        self.mouse_pos_multiplier=[[1920,1080][i]/inherited_screen_size[i] for i in range(2)] #Adjusts the mouse correctly
        self.drag_screen_allowed=True #Sets whether or not if you drag something, it will be dragged across the screen
        self.mouse_down=[False for i in range(3)]
        self.ctimer=[0,0,0]
        self.mcctimer=0
        self.click=[False,False,False] #Can accurately detect the first frame when the mouse button is clicked
        self.game_over=False
        self.open_GUIs={}

        loadCardImages()

        self.time_passed=0
        self.tech={} #Current Effects happening on board
    
        self.hand=None
    def setup_hand(self,max_cards=10):
        self.hand=Engine.pile.Hand((0,500),max_cards)
    def setup_card_pile(self,card_pile_name="Deck",pos=(900,0),custom_size=(210,320)):
        self.card_piles[card_pile_name]=Engine.pile.Pile(card_pile_name,pos,custom_size=custom_size)
        #self.card_piles.append(card_pile_name)
    def draw(self,delta=1):

        #The fuck are these things? Why would someone multiply the camera pos by something? i'm keeping this as a fun artifact. 
        #self.camera_x*=1.01
        #self.camera_y*=1.01
        self.time_passed+=delta
        self.drag_screen_allowed=False
        self.surface.fill((25,5,5)) #Fills the board with a nice color to draw on
        
        for i in self.locations["OnTable"]:
            i["Card"].draw(delta=delta)
            #logging.info(i)
            #pygame.image.save(i["Card"].sprite,"test.png")
            center(i["Card"].sprite,self.surface,i["Position"][0],i["Position"][1])
        
        for iterated_card_pile in self.card_piles: #Draws the top card of every card pile
            self.card_piles[iterated_card_pile].draw(self.surface)
        if self.hand!=None:
            self.hand.draw(self,delta=delta)
        
        #cooler cursor
        mc_size=10-(min(self.mcctimer/6,1)/1)**2*8 #adding a smooth easing motion for more fun
        #pygame.draw.circle(self.surface,(255,255,255),self.mouse_pos,mc_size+3,2)
        for i in range(6):
            pygame.draw.polygon(self.surface,(255,255,255),[
            (
                self.mouse_pos[0]+cos(self.time_passed/40+2*pi/6*i)*mc_size,
                self.mouse_pos[1]+sin(self.time_passed/40+2*pi/6*i)*mc_size,
            ),
            (
                self.mouse_pos[0]+cos(self.time_passed/40+2*pi/6*i+pi/20)*(mc_size+5),
                self.mouse_pos[1]+sin(self.time_passed/40+2*pi/6*i+pi/20)*(mc_size+5),
            ),
            (
                self.mouse_pos[0]+cos(self.time_passed/40+2*pi/6*i)*(mc_size+10),
                self.mouse_pos[1]+sin(self.time_passed/40+2*pi/6*i)*(mc_size+10),
            ),
            (
                self.mouse_pos[0]+cos(self.time_passed/40+2*pi/6*i-pi/20)*(mc_size+5),
                self.mouse_pos[1]+sin(self.time_passed/40+2*pi/6*i-pi/20)*(mc_size+5),
            )
            
            ])
        
    def update(self,delta): #Updates the board so that 
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
        if self.mouse_down[0]:
            self.mcctimer=min(6,self.mcctimer+delta)
        else:
            if self.mcctimer>0:
                self.mcctimer-=delta
            else:
                self.mcctimer=0
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
        if len(self.card_piles[from_pile].cards)>0:
            drawn_card=self.card_piles[from_pile].cards.pop(0)
            if len(self.hand.cards)<self.hand.max_cards:
                self.hand.cards.append(drawn_card)
                drawn_card.vector_space_element=Vector_Element()
                drawn_card.vector_space_element.setup(self.card_piles[from_pile].pos[0],self.card_piles[from_pile].pos[1])
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
        if not to_card_pile in self.card_piles:
            self.setup_card_pile(to_card_pile)
        for iterated_card_packed in json_deck_list:
            new_card=self.add_card_to_game(iterated_card_packed["ID"],iterated_card_packed["Type"])
            new_card.iflip("Back")
            self.card_piles[to_card_pile].cards.append(new_card)
    def shuffle_card_pile(self,card_pile="Deck"):
        shuffle(self.card_piles[card_pile].cards)
    def check_for_target(self,locations=[]):
        #Currently this is somehow pretty fucking useless, i'll fix it once we add proper effect building
        possible_cards=[]
        #First finds all the cards, then removes all the ones that don't count.
        for iterated_card_pile in self.card_piles:
            possible_cards.extend(self.card_piles[iterated_card_pile].cards) 
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
