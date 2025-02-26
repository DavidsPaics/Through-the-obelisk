import globalState
import pygame, logging, time, useful_stuff

background_texture = pygame.image.load('./assets/not-stolen-background.png')

def mainMenu(screen):
    scaled_background_texture = pygame.transform.scale(background_texture, screen.get_size())
    
    # Initialize font
    font = pygame.font.Font(None, 36)
    
    # Define button properties
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    host_button_rect = pygame.Rect((screen_width - 200) // 2, 250, 200, 50)
    host_button_text = useful_stuff.render_text("Host Game", 22, (255, 255, 255), "arial")
    join_button_rect = pygame.Rect((screen_width - 200) // 2, 320, 200, 50)
    join_button_text = useful_stuff.render_text("Join Game", 22, (255, 255, 255), "arial")

    
    while True:
        screen.blit(scaled_background_texture, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if host_button_rect.collidepoint(event.pos):
                    logging.info("Host Game button clicked")
                    # Add functionality for hosting game here
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F7:
                    globalState.debugMode = not globalState.debugMode

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
        
        if globalState.debugMode:
            useful_stuff.draw_fps_counter(screen, globalState.clock)

        pygame.display.update()
        globalState.clock.tick(60)