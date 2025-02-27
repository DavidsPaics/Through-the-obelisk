# import combat
import combat
import globalState
import pygame, logging, time, useful_stuff
from networking import Networking

background_texture = pygame.image.load('./Resources/images/not-stolen-background.png')

def mainMenu(screen):
    scaled_background_texture = pygame.transform.scale(background_texture, screen.get_size())
    
    # Define button properties
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    host_button_rect = pygame.Rect((screen_width - 200) // 2, 250, 200, 50)
    host_button_text = useful_stuff.render_text("Host Game", 22, (255, 255, 255), "arial")
    join_button_rect = pygame.Rect((screen_width - 200) // 2, 320, 200, 50)
    join_button_text = useful_stuff.render_text("Join Game", 22, (255, 255, 255), "arial")
    game_title = useful_stuff.render_text("Through the Obelisk", 50, (255, 255, 255), "arial", bold=True)

    
    while True:
        screen.blit(scaled_background_texture, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if host_button_rect.collidepoint(event.pos):
                    startHostingGame(screen)
                    globalState.networkManager.close()
                if join_button_rect.collidepoint(event.pos):
                    joinGame(screen)
                    globalState.networkManager.close()
                    # Add functionality for hosting game here
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F7:
                    globalState.debugMode = not globalState.debugMode
                elif event.key == pygame.K_F9:
                    combat.combat(screen)
                    exit()

        # Draw buttons with hover effect
        if host_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 0, 0), host_button_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (139, 0, 0), host_button_rect, border_radius=5)
        screen.blit(host_button_text, (host_button_rect.x + 50, host_button_rect.y + 11))

        if join_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 0, 0), join_button_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (139, 0, 0), join_button_rect, border_radius=5)
        screen.blit(join_button_text, (join_button_rect.x + 50, join_button_rect.y + 11))

        screen.blit(game_title, (screen_width // 2 - 220, 100))
        
        if globalState.debugMode:
            useful_stuff.draw_fps_counter(screen, globalState.clock)

        pygame.display.update()
        globalState.clock.tick(60)


def startHostingGame(screen):
    scaled_background_texture = pygame.transform.scale(background_texture, screen.get_size())

    globalState.networkManager = Networking(True)
    
    # Define button properties
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Define background rectangle for text
    text_background_rect = pygame.Rect((screen_width - 320) // 2, 240, 320, 100)

    waiting_text = useful_stuff.render_text("Waiting for connection...", 22, (255, 255, 255), "arial")
    ip_text = useful_stuff.render_text(f"IP: {globalState.networkManager.socket.getsockname()[0]}:{globalState.networkManager.socket.getsockname()[1]}", 22, (255, 255, 255), "arial")

    back_button_rect = pygame.Rect((screen_width - 200) // 2, 350, 200, 50)
    back_button_text = useful_stuff.render_text("Back", 22, (255, 255, 255), "arial")
    
    while True:
        screen.blit(scaled_background_texture, (0, 0))

        if globalState.networkManager.isConnected:
            startGame(screen)
            return
        
        globalState.networkManager.try_accept_connection()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F7:
                    globalState.debugMode = not globalState.debugMode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    return

        pygame.draw.rect(screen, (64,64, 64), text_background_rect, border_radius=5)
        screen.blit(waiting_text, (screen_width // 2 - 100, 250))
        screen.blit(ip_text, (screen_width // 2 - 100, 300))

        if back_button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (100, 0, 0), back_button_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (139, 0, 0), back_button_rect, border_radius=5)
        
        screen.blit(back_button_text, (back_button_rect.x + 75, back_button_rect.y + 11))

        if globalState.debugMode:
            useful_stuff.draw_fps_counter(screen, globalState.clock)

        pygame.display.update()
        globalState.clock.tick(60)

def joinGame(screen):
    scaled_background_texture = pygame.transform.scale(background_texture, screen.get_size())
    
    # Define button properties
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Define background rectangle for text
    text_background_rect = pygame.Rect((screen_width - 320) // 2, 230, 320, 142)

    join_text = useful_stuff.render_text("Enter IP:Port to join", 22, (255, 255, 255), "arial")
    input_box = pygame.Rect((screen_width - 300) // 2, 310, 300, 50)
    input_text = ''
    active = False
    shit = False

    back_button_rect = pygame.Rect((screen_width - 200) // 2, 380, 200, 50)
    back_button_text = useful_stuff.render_text("Back", 22, (255, 255, 255), "arial")

    while True:
        if len(input_text) > 0 or active == False:
            shit = False
        screen.blit(scaled_background_texture, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F7:
                    globalState.debugMode = not globalState.debugMode
                elif active:
                    if event.key == pygame.K_RETURN:
                        # Process the input_text here
                        print(f"Joining game at {input_text}")
                        if ':' not in input_text:
                            logging.error("Invalid IP:Port format")
                            shit = True
                        else:
                            ip, port = input_text.split(":")
                            globalState.networkManager = Networking(False, ip, int(port))
                            startGame(screen)
                            exit()


                        # Add functionality to join the game using input_text
                        input_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False

                if back_button_rect.collidepoint(event.pos):
                    return

        pygame.draw.rect(screen, (64, 64, 64), text_background_rect, border_radius=5)
        screen.blit(join_text, (screen_width // 2 - 100, 250))

        # Render the current text.
        pygame.draw.rect(screen, (128, 128, 128) if not input_box.collidepoint(pygame.mouse.get_pos()) else (115,115,115), input_box, border_radius=5)
        txt_surface = useful_stuff.render_text(input_text, 22, (255, 255, 255), "arial")
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 15))
        pygame.draw.rect(screen, (255, 128, 128) if shit else ((200, 200, 200) if not active else (255, 255, 255)), input_box, 3, border_radius=5)

        if back_button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (100, 0, 0), back_button_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (139, 0, 0), back_button_rect, border_radius=5)
        
        screen.blit(back_button_text, (back_button_rect.x + 75, back_button_rect.y + 11))

        if globalState.debugMode:
            useful_stuff.draw_fps_counter(screen, globalState.clock)

        pygame.display.update()
        globalState.clock.tick(60)

def idk123(data):
    print("yay:", data)

def startGame(screen):
    if globalState.networkManager.isServer:
        globalState.networkManager.broadcastEvent("testEvent", {"hey": "hello"})
    else:
        globalState.networkManager.onEvent("testEvent", idk123)
        while(1):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            globalState.networkManager.handleEvents()
    # combat.combat(screen)