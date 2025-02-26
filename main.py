import pygame
import socket
import card
pygame.init()

# Set up the display
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
pygame.display.set_caption("Through the Obelisk")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a color (e.g., white)
    screen.fill((255, 255, 255))

    # Update the display
    pygame.display.flip()

pygame.quit()