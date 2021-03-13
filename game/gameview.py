import arcade

import game.constants
from game.tanks import Run
from game.ground import Ground
from game.bullet import Bullet
from typing import Optional


class Gameview(arcade.View):
    def __init__(self):
        super().__init__()

        self.setup()
        self.up: bool = False
        self.down: bool = False
        self.right: bool = False
        self.left: bool = False

    
    def setup(self):
        # self.physics_engine = arcade.PymunkPhysicsEngine(damping = 1.0)
        self.tanks = Run()
        self.ground = Ground()
        self.bullet = Bullet()
        # self.physics_engine.add_sprite(self.bullet)
        self.bullet.shoot_bullet()
    
    def on_draw(self):
        self.tanks.sprite_list.draw()
        self.ground.ground_sprite_list.draw()
        self.bullet.bullet_sprite_list.draw()

    def on_update(self, delta_time: float):
        # if self.up:
        #     force = (-8000, 0)
        #     self.physics_engine.apply_force(self.bullet, force)
        self.bullet.bullet_sprite_list.update()
        self.bullet.bullet_sprite_list.update_animation()
        # self.physics_engine.step()
    
    def on_key_press(self, symbol, modifiers):
        """Handle user keyboard input
        Q: Quit the game
        P: Pause/Unpause the game
        W/A/S/D: Move Up, Left, Down, Right
        Arrows: Move Up, Left, Down, Right
        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
            actor -- which sprite will be modified (tank1 or tank2)
        """
        if symbol == arcade.key.Q:
            # Quit immediately
            arcade.close_window()

        if symbol == arcade.key.P:
            self.paused = not self.paused

        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.up = True

        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.down = True

        if symbol == arcade.key.D or symbol == arcade.key.LEFT:
            self.left = True

        if symbol == arcade.key.A or symbol == arcade.key.RIGHT:
            self.right = True
    
    def on_key_release(self, symbol: int, modifiers: int):
        """Undo movement vectors when movement keys are released
        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
            actor -- which will be modified (tank1 or tank2)
        """
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.up = False

        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.down = False
        
        if symbol == arcade.key.D or symbol == arcade.key.LEFT:
            self.left = False

        if symbol == arcade.key.A or symbol == arcade.key.RIGHT:
            self.right = False