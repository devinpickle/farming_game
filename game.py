"""
Example of Pymunk Physics Engine Platformer
"""
import math
from typing import Optional
import arcade

################
    #Constants
################

SCREEN_TITLE = "Farm Game"

# Size of screen to show, in pixels
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SPRITE_IMAGE_SIZE = 128

# Scale sprites up or down
SPRITE_SCALING_PLAYER = 0.8
SPRITE_SCALING_ANIMALS = 0.7
SPRITE_SCALING_TILES = 0.5

# Scaled sprite size for tiles
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * 0.5)

# Size of grid to show on screen, in number of tiles
SCREEN_GRID_WIDTH = 25
SCREEN_GRID_HEIGHT = 16

# Size of screen to show, in pixels
SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

# Physics
GRAVITY = 0
PLAYER_MOVEMENT_SPEED = 800
PLAYER_MOVE_FORCE = 3500
PLAYER_FRICTION = 2.0
PLAYER_MASS = 2.0
PLAYER_DAMPING = 0.0005


class GameWindow(arcade.Window):
    """ Main Window """

    def __init__(self, width, height, title):
        """ Create the variables """

        # Init the parent class
        super().__init__(width, height, title)

        # Player Sprite
        self.player_sprite = None

        # Sprite lists
        self.player_list = None
        self.wall_list = None
        self.animal_list = None
        self.break_object_list = None

        # Track which key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Track which way player is facing
        self.player_face = "right"

        # Map
        with open("assets/maps/testmap.csv") as f:
            self.map = f.readlines()

        # Background Color
        arcade.set_background_color(arcade.color.DARK_GREEN)

    def setup(self):
        """ Set up everything with the game """

        # Create Sprite Lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.animal_list = arcade.SpriteList()
        self.break_object_list = arcade.SpriteList()

        # Create the player sprite
        self.player_sprite = arcade.Sprite("assets/images/player.png", SPRITE_SCALING_PLAYER)

        
        # Create the Map based off the csv file
        wall_y = 0
        for x in self.map:
            wall_x = 0
            wall_y += 64
            for item in x:
                if item == "0":
                    wall_x += 64
                elif item == "1":
                    wall = arcade.Sprite("assets/images/brick.png", SPRITE_SCALING_TILES)
                    wall.center_x = wall_x
                    wall.center_y = wall_y
                    self.wall_list.append(wall)
                    wall_x += 64
                elif item == "5":
                    animal = arcade.Sprite("assets/images/cow.png", SPRITE_SCALING_ANIMALS)
                    animal.center_x = wall_x
                    animal.center_y = wall_y
                    self.animal_list.append(animal)
                    wall_x += 64
                elif item == "3" :
                    self.player_sprite.center_x = wall_x
                    self.player_sprite.center_y = wall_y
                    self.player_list.append(self.player_sprite)
                    wall_x += 64

        # Setup the physics engine
        damping = PLAYER_DAMPING
        gravity = (0, GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping = damping, gravity = gravity)

        # Add player to physics engine
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction = PLAYER_FRICTION,
                                       mass = PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MOVEMENT_SPEED,
                                       max_vertical_velocity=PLAYER_MOVEMENT_SPEED)
        
        # Add walls to physics engine
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction = PLAYER_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        # Add animals to physics engine
        self.physics_engine.add_sprite_list(self.animal_list, friction=PLAYER_FRICTION, collision_type = "animal")

        # Add breaking wall objects to physics engine
        self.physics_engine.add_sprite_list(self.break_object_list,
                                            friction = PLAYER_FRICTION,
                                            collision_type="break",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)


        # Set up collisions
        def wall_break_handler(break_wall_sprite, wall_sprite, _arbiter, _space, _data):
            """ Called for breakable wall collision """
            print("break wall")
            wall_sprite.remove_from_sprite_lists()
            break_wall_sprite.remove_from_sprite_lists()
            

        self.physics_engine.add_collision_handler("break", "wall", post_handler=wall_break_handler)
        print("added wall break handler")


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.player_face = "left"
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.player_face = "right"
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
            self.player_face = "up"
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
            self.player_face = "down"
        elif key == arcade.key.J:
            brick_sound = arcade.load_sound("assets/hit_sound.wav")
            arcade.play_sound(brick_sound)
            wall = arcade.Sprite("assets/images/brick.png", SPRITE_SCALING_TILES)
            wall.center_x = self.player_sprite.center_x
            wall.center_y = self.player_sprite.center_y
            self.wall_list.append(wall)
            self.physics_engine.add_sprite(wall,
                                            friction = PLAYER_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        elif key == arcade.key.K:
            if self.player_face == "up":
                break_wall = arcade.Sprite("assets/images/brick.png", SPRITE_SCALING_TILES)
                break_wall.center_x = self.player_sprite.center_x
                break_wall.center_y = self.player_sprite.center_y + 40
                self.break_object_list.append(break_wall)
            elif self.player_face == "down":
                break_wall = arcade.Sprite("assets/images/brick.png", SPRITE_SCALING_TILES)
                break_wall.center_x = self.player_sprite.center_x
                break_wall.center_y = self.player_sprite.center_y - 40
                self.break_object_list.append(break_wall)
            elif self.player_face == "left":
                break_wall = arcade.Sprite("assets/images/brick.png", SPRITE_SCALING_TILES)
                break_wall.center_x = self.player_sprite.center_x - 40
                break_wall.center_y = self.player_sprite.center_y
                self.break_object_list.append(break_wall)
            elif self.player_face == "right":
                break_wall = arcade.Sprite("assets/images/brick.png", SPRITE_SCALING_TILES)
                break_wall.center_x = self.player_sprite.center_x + 40
                break_wall.center_y = self.player_sprite.center_y
                self.break_object_list.append(break_wall)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False

    def on_update(self, delta_time):
        """ Movement and game logic """
        # Update the physics engine
        self.physics_engine.step()

        # Move the player
        if self.left_pressed and not self.right_pressed:
            force = (-PLAYER_MOVE_FORCE, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            force = (PLAYER_MOVE_FORCE, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.up_pressed and not self.down_pressed:
            force = (0, PLAYER_MOVE_FORCE)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.down_pressed and not self.up_pressed:
            force = (0, -PLAYER_MOVE_FORCE)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            self.physics_engine.set_friction(self.player_sprite, 10.0)

        if len(self.break_object_list) >= 1:
            self.break_object_list.pop()

        
            
        

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.wall_list.draw()
        self.player_list.draw()
        self.animal_list.draw()
        self.break_object_list.draw()


def main():
    """ Main function """
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()