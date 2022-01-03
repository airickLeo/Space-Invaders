import pygame
import random
import os
import time

# Initialize pygame
pygame.init()

# Initialize the font
pygame.font.init()

# Set up the width and height of the game screen
width = 800
height = 600

# Create the game screen
screen = pygame.display.set_mode((width, height))

# Create a variable to store the background and transform the png to the matching screen width and height
background = pygame.transform.scale(pygame.image.load('artistic_digital_universe-800x600.jpg'), (width, height))

# Set up the game title and icon
pygame.display.set_caption("Space Shooter")
icon = pygame.image.load('../Space Shooter/001-spaceship.png')
pygame.display.set_icon(icon)

# Load all the png files
red_ship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
green_ship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
blue_ship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
yellow_ship = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Set up for the player spaceship
# playerPng = pygame.image.load('../Space Shooter/001-spaceship.png')
playerPng = yellow_ship


# Class for spaceship
class Spaceship:
    # Define a class variable represents the laser cool down
    coolDown = 200

    # Define a constructor for the class to initialize attributes
    def __init__(self, x_pos, y_pos, health=100):
        # Assign initial attributes for the current object
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down = 0

    # Function that returns the width of the spaceship
    def get_width(self):
        return self.ship_img.get_width()

    # Function that returns the width of the spaceship
    def get_height(self):
        return self.ship_img.get_height()

    # Draw the spaceship and laser
    def draw(self, window):
        window.blit(self.ship_img, (self.x_pos, self.y_pos))
        for laser in self.lasers:
            laser.draw_laser(window)

    # Function that checks if a laser of an enemy has collided with an entity (player)
    def check_collision(self, velocity, entity):
        # Check the current cool down
        self.cool_down_count()

        # Loop through all lasers in the list
        for laser in self.lasers:
            # Move the laser
            laser.laser_movement(velocity)

            # if the laser is off of the screen, remove it
            if laser.off_screen(height):
                self.lasers.remove(laser)

            # else if the laser has collided with an entity
            elif laser.collision(entity):
                entity.health -= 10

                # Remove the laser once it collides with an entity
                self.lasers.remove(laser)

    # Function that handles the cool down
    def cool_down_count(self):
        # When the cooldown reaches the required time limit, reset the cool down
        if self.cool_down >= self.coolDown:
            self.cool_down = 0

        # else if cool_down is not equal to 0 and did not reach the required time limit
        elif self.cool_down > 0:
            self.cool_down += 1

        # Do not make any changes to cool_down if it is equal to 0
        # (we can now shoot a new laser)


# Create a Player subclass of the Spaceship base class
class Player(Spaceship):

    # Define a constructor for the class to initialize attributes
    def __init__(self, x_pos, y_pos, health=100):
        # Inherit all the attributes that are already created within the base class
        super().__init__(x_pos, y_pos, health)

        # Add in new attributes
        self.ship_img = playerPng
        self.laser_img = yellow_laser
        self.max_health = health

        # Pixel perfect collision detection
        self.mask = pygame.mask.from_surface(self.ship_img)

    # Function that makes the lasers
    def make_laser(self):
        # If the cooldown is over
        if self.cool_down == 0:
            # initialize the laser object
            laser = Laser(self.x_pos, self.y_pos, self.laser_img)

            # Append the new laser to the list of lasers
            self.lasers.append(laser)

            # Reset the cooldown
            self.cool_down = 1

    # Overridden function that checks if the player's laser collided with an enemy
    def check_collision(self, velocity, entities):
        # Check the current cool down
        self.cool_down_count()

        # Loop through all lasers in the list
        for laser in self.lasers:
            # Move the laser
            laser.laser_movement(velocity)

            # if the laser is off of the screen, remove it
            if laser.off_screen(height):
                self.lasers.remove(laser)

            # else, remove the according enemy that was hit by the laser
            else:
                # Loop through all enemies
                for entity in entities:
                    # If a player's laser hits one of the enemies, remove that enemy
                    if laser.collision(entity):
                        entities.remove(entity)

                        # Once the laser collides with an enemy, remove it
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    # Display the health bar
    def health_bar(self, window):
        # Draw the red max_health bar
        pygame.draw.rect(window, (255, 0, 0), (self.x_pos, self.y_pos + self.ship_img.get_height()
                                               + 10, self.ship_img.get_width(), 5))

        # Draw the green health bar representing the current health
        pygame.draw.rect(window, (0, 255, 0), (self.x_pos, self.y_pos + self.ship_img.get_height()
                                               + 10, self.ship_img.get_width() * (self.health / self.max_health), 5))

    # Overridden function that draws the player spaceship and health bar
    def draw(self, window):
        # Access the super class draw function that draws the player spaceship
        super().draw(window)
        # Draw the player health bar
        self.health_bar(window)


# Define the enemy class
class Enemy(Spaceship):
    # Define a class variable that is a dictionary, which returns the
    # matching pair of spaceship and laser based on the inputted colour
    colours_dictionary = {
        "red": (red_ship, red_laser),
        "green": (green_ship, green_laser),
        "blue": (blue_ship, blue_laser)
    }

    # Define a constructor for the class to initialize attributes,
    # with a new attribute, colour
    def __init__(self, x_pos, y_pos, colour, health=100):
        # Inherit all the attributes that are already created within the base class
        super().__init__(x_pos, y_pos, health)

        # Obtain the enemy ship and laser images
        self.ship_img, self.laser_img = self.colours_dictionary[colour]

        # Pixel perfect collision
        self.mask = pygame.mask.from_surface(self.ship_img)

    # Define a function that develops enemy movements
    def enemy_movement(self, velocity):
        # only moving down the game screen
        self.y_pos += velocity

    # Overridden function that makes the lasers for the enemies
    def make_laser(self):
        # If the cooldown is over
        if self.cool_down == 0:
            # initialize the laser object
            laser = Laser(self.x_pos - 16, self.y_pos - 16, self.laser_img)

            # Append the new laser to the list of lasers
            self.lasers.append(laser)

            # Reset the cooldown
            self.cool_down = 1


# Define a class for the lasers
class Laser:
    # Define a constructor that set up the attributes of a laser object
    def __init__(self, x_pos, y_pos, laser_img):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.laser_img = laser_img

        # Pixel perfect collision detection
        self.mask = pygame.mask.from_surface(self.laser_img)

    # Function that draws the laser
    def draw_laser(self, window):
        window.blit(self.laser_img, (self.x_pos, self.y_pos))

    # Function that develops laser movement
    def laser_movement(self, velocity):
        self.y_pos += velocity

    # Function that checks if the laser is off screen by returning a boolean value
    def off_screen(self, height):
        return self.y_pos > height or self.y_pos < 0

    # Function that checks if the laser collided with an entity
    def collision(self, entity):
        return collide(self, entity)


# Define a function checks if two entities collides
def collide(entity1, entity2):
    # Find the offsets of the two entities
    offset_x = entity2.x_pos - entity1.x_pos
    offset_y = entity2.y_pos - entity1.y_pos

    # Return false if the mask of entity1 does not collide with the mask of entity2
    # with the given offset values, true otherwise
    return entity1.mask.overlap(entity2.mask, (offset_x, offset_y)) != None


# Define main
def main():
    # Create a sentinel variable to keep the game running
    running = True

    # Limit the frames per second so that the game stays consistent for any devices
    FPS = 60
    clock = pygame.time.Clock()

    # Set up the level and the number of lives
    level = 0
    lives = 3

    # Set up the fonts
    game_font = pygame.font.SysFont("arial", 20)
    game_over_font = pygame.font.SysFont("comicsans", 40)

    # Determine how many pixels the player can move by pressing a key
    player_velocity = 5

    # Determine how fast the lasers will move
    laser_velocity = 3

    # Enemy laser cool down
    enemy_cool_down = 5

    # Create a player
    player = Player(300, 200)

    # Set the number of enemies that appears in the wave
    num_per_wave = 5

    # Create the velocity of the enemy moving down the game screen
    enemy_velocity = 1

    # Create a dynamic array that stores the positions of all enemies
    enemies = []

    # Variable that tracks if the game is over
    game_over = False

    # Set up a timer for the game over message
    game_over_timer = 0

    # Function that updates the game window
    def update_window():

        # Draw the background
        screen.blit(background, (0, 0))

        # Set up text
        lv_label = game_font.render(f"Level: {level}", 1, (192, 192, 192))
        lives_label = game_font.render(f"Lives: {lives}", 1, (192, 192, 192))

        # Draw the level and lives labels
        screen.blit(lives_label, (10, 10))
        screen.blit(lv_label, (width - (10 + lv_label.get_width()), 10))

        # Draw the enemies onto the screen
        for enemy in enemies:
            enemy.draw(screen)

        # Draw the player by providing it with the surface
        player.draw(screen)

        # Display the loss message
        if game_over:
            game_over_label = game_over_font.render("Game Over!", 1, (192, 192, 192))

            # Blit the game over label onto the surface
            screen.blit(game_over_label, (width / 2 - game_over_label.get_width() / 2, height / 2 - 100))

        # Update the display
        pygame.display.update()

    # While loop that runs the game when running is True
    while running:

        # Set up the frames per second
        clock.tick(FPS)

        # Call the update_window function to redraw the game window
        update_window()

        # If the lives are gone and player health is gone, then end the game
        if lives <= 0 or player.health <= 0:
            game_over = True
            game_over_timer += 1

        # Display the game over message for 4 seconds
        if game_over:
            # If the timer reaches 4 seconds, stop the while loop execution
            if game_over_timer > FPS * 4:
                running = False

            # else, continue the while loop execution from the beginning
            else:
                continue

        # When there are no more enemies, move on to the next level
        if len(enemies) == 0:

            # Move on to the next level
            level += 1

            # Reduce the cool down of enemy every level
            if enemy_cool_down > 2:
                enemy_cool_down -= 1

            # Add 3 more enemies to the next level
            num_per_wave += 3

            # Create num_per_wave many enemies
            for i in range(num_per_wave):
                # Create enemies at random different positions to make them appear
                # as if they spawned at different positions
                enemy = Enemy(random.randrange(80, width - 80),
                              random.randrange(-2000, -100), random.choice(["red", "green", "blue"]))

                # Append the newly created enemy into the list of enemies
                enemies.append(enemy)

        # Iterate through all events
        for event in pygame.event.get():

            # If the QUIT key is pressed, assign running to False
            if event.type == pygame.QUIT:
                # Quit the game
                quit()

        # Obtain a dictionary of all possible keys
        # Using the dictionary method enables the player to press two keys at once,
        # allowing the player to move diagonally
        keys = pygame.key.get_pressed()

        # If the player pressed the a key to move left
        if keys[pygame.K_a] and 0 < player.x_pos - player_velocity:
            player.x_pos -= player_velocity

        # If the player pressed the d key to move right
        if keys[pygame.K_d] and width > player.x_pos + (player.get_width() + player_velocity):
            player.x_pos += player_velocity

        # If the player pressed the w key to move up
        if keys[pygame.K_w] and 0 < player.y_pos:
            player.y_pos -= player_velocity

        # If the player pressed the s key to move down
        if keys[pygame.K_s] and height > player.y_pos + (player.get_height() + player_velocity) + 10:
            player.y_pos += player_velocity

        # If the player pressed j to shoot the laser
        if keys[pygame.K_j]:
            player.make_laser()

        # Move the enemies (the for loop runs on the copy of enemies array)
        for enemy in enemies[:]:
            # Move a single enemy
            enemy.enemy_movement(enemy_velocity)

            # Shoot enemy laser and check collision
            enemy.check_collision(laser_velocity, player)

            # Have the enemies shoot lasers at a random rate
            if random.randrange(0, enemy_cool_down * FPS) == 1:
                enemy.make_laser()

            # Sacrifice health to take down enemies
            if collide(enemy, player):
                player.health -= 20
                enemies.remove(enemy)

            # Remove a life if an enemy moved past the bottom boundary,
            # and remove that enemy from the list of enemies that needs to
            # be displayed onto the screen
            elif enemy.y_pos + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)

            # Shoot player laser and check collision
            player.check_collision(-laser_velocity, enemies)


# Function that create a menu
def menu():
    # Sentinel that keeps the menu running until the user quits
    running = True

    # Create font for the menu
    menu_font = pygame.font.SysFont("arial", 60)

    # Iterates until the user quites the game
    while running:
        # Blit the background
        screen.blit(background, (0, 0))

        # Create the menu label
        menu_label = menu_font.render("Press any mouse button to start", 1, (192, 192, 192))

        # Blit the menu label
        screen.blit(menu_label, (width / 2 - menu_label.get_width() / 2, 200))

        # Update the display
        pygame.display.update()

        # Loop through all events
        for event in pygame.event.get():
            # If the user quits the game, assign running to false
            if event.type == pygame.QUIT:
                running = False

            # Pressing any mouse button will start the game
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Trigger the game loop
                main()

menu()
