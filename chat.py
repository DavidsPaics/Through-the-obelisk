import pygame, logging, time, useful_stuff
from networking import Networking
import globalState
import socket

class Chat:
    def __init__(self):
        self.chat = []
        self.isOpen = False
        self.input_text = ''
        self.active = False
        self.last_activity_time = time.time()
        globalState.networkManager.onEvent("chatMessage", self.addMessage)
        self.addMessage({"name": "Server", "content": "Hello world"})

    def addMessage(self, message):
        self.chat.append(f"{message['name']}: {message['content']}")
        self.isOpen = True
        self.last_activity_time = time.time()

    def sendMessage(self, message):
        if message == "/quit":
            exit()

        hostname = socket.gethostname()
        globalState.networkManager.broadcastEvent("chatMessage", {"name": hostname, "content": message})
        self.addMessage({"name": hostname, "content": message})

    def draw(self, screen):
        if not self.isOpen:
            return

        screen_width = screen.get_width()
        screen_height = screen.get_height()
        chat_box = pygame.Rect(0, 0, screen_width // 3, screen_height // 3)
        self.input_box = pygame.Rect(10, chat_box.height - 50, chat_box.width - 20, 40)
        
        # Draw transparent gray background
        s = pygame.Surface((chat_box.width, chat_box.height), pygame.SRCALPHA)
        s.fill((50, 50, 50, 150))  # RGBA
        screen.blit(s, (0, 0))
        
        # Draw chat messages
        for i, message in enumerate(self.chat[-10:]):  # Show last 10 messages
            text = useful_stuff.render_text(message, 19, (255, 255, 255), "arial")
            screen.blit(text, (10, 10 + i * 20))
        
        # Draw input box
        pygame.draw.rect(screen, (200, 200, 200), self.input_box, border_radius=5)
        txt_surface = useful_stuff.render_text(self.input_text, 19, (0, 0, 0), "arial")
        screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 4))
        pygame.draw.rect(screen, (255, 255, 255) if self.active else (200, 200, 200), self.input_box, 2, border_radius=5)


        if self.isOpen and time.time() - self.last_activity_time > 5:
            self.isOpen = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.last_activity_time = time.time()
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.sendMessage(self.input_text)
                    self.input_text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode
            if not self.isOpen:
                if event.key == pygame.K_SLASH:
                    self.isOpen = True
                    self.input_text = ''
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.last_activity_time = time.time()
            if self.input_box.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False

        elif event.type == pygame.MOUSEMOTION:
            if self.input_box.collidepoint(event.pos):
                self.last_activity_time = time.time()