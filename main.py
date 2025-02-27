import pygame, logging, time
from networking import Networking
import globalState
from mainMenu import mainMenu
pygame.init()

# Set up the display
screen = pygame.display.set_mode((1080 , 720))
pygame.display.set_caption("Through the Obelisk")

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('log.txt'),
                        logging.StreamHandler()
                    ])
logging.info('Sveiki!')

# networking = Networking(bool(input("Server? (y/n): ") == "y"), port=6969, ip="localhost")

# while not networking.isConnected and networking.isServer:
#     networking.try_accept_connection()
#     time.sleep(0.1)

# logging.info("Connected!")

# Main game loop
running = True
globalState.clock = pygame.time.Clock()
while running:
    dt = globalState.clock.tick(60) # ms

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # if networking.isServer:
    #     data = networking.receive()
    #     if data is not None:
    #         logging.info(f"Received data: {data}")
    # else:
    #     pass

    mainMenu(screen)


    pygame.display.update()

pygame.quit()