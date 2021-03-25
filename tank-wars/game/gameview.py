import arcade
from time import sleep
from game.score import Score
import game.constants as constants
from game.tanks import Run
from game.ground import Ground
from game.bullet import Bullet
from game.powerups import SpawnRandom
from game.explosion import Explosion
from game.game_over_view import GameOverView
from typing import Optional
import math

class GameView(arcade.View):
    """ Game view for Tank Wars
    Stereotype:
        Controller
    Attributes:
        _score (Score): initalizes the score class
        texture (arcade.load_texture): load background texture
        physicis_engine (None): declares physics engine variable
        physics_engine2 (None): declares physics engine 2 variable
        bullet_list (None): declares bullet list bariable
        explosion_list (None): declares explosion list variable
    Contributors:
        Reed Hunsaker
        Adrianna Lund
        Isabel Aranguren
        Jordan 
    """
    def __init__(self):
        super().__init__()
        
        self._score = Score()
        self.texture = arcade.load_texture(constants.BACKGROUND)
        
        self.window.set_mouse_visible(False)
        self.physics_engine = None
        self.physics_engine2 = None
        self.bullet_list = None
        self.explosions_list = None
        self.all_sprites = arcade.SpriteList(use_spatial_hash= True)
        
        self.powerup_sound = arcade.load_sound(constants.POWERUPS_SOUND)
        self.powerdown_sound = arcade.load_sound(constants.POWERDOWN_SOUND)
        self.tank_explode = arcade.load_sound(constants.EXPLOSION_SOUND)
        self.explosion_texture_list = []

        columns = 16
        self.count = 18
        sprite_width = 256
        sprite_height = 256
        file_name = ":resources:images/spritesheets/explosion.png"

        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, self.count)


    def setup(self):
        """
        Set up the game and initialize the variables.
        """
        self.tanks = Run()
        self.ground = Ground()
        self.bullet = Bullet()

        self.power = SpawnRandom()
        self.explosion_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.physics_engine = arcade.PhysicsEngineSimple(self.tanks.player1, self.ground.ground_sprite_list)
        self.physics_engine2 = arcade.PhysicsEngineSimple(self.tanks.player2, self.ground.ground_sprite_list)

    def on_draw(self):
        arcade.start_render()

        self.wrap()
        self.texture.draw_sized(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2,
                                constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        self.tanks.sprite_list.draw()
        
        for tank in self.tanks.sprite_list:
            tank.draw_life_bar()
            tank.draw_life_number()
        
        self.ground.ground_sprite_list.draw()
        self.power.sprite_list.draw()
        
        if self.bullet.bullet_sprite_list is not None:
            self.bullet.bullet_sprite_list.draw()
        if self.explosions_list is not None:
            self.explosions_list.draw()

    def on_update(self, delta_time: float):
        
        self.physics_engine.update()
        self.physics_engine2.update()
        self.explosions_list.update()
        
        bullets = len(self.bullet.bullet_sprite_list)

        if bullets > 0:
            for bullet in self.bullet.bullet_sprite_list:
                hit_list_wall = arcade.check_for_collision_with_list(bullet, self.ground.ground_sprite_list)
                hit_list_tank = arcade.check_for_collision_with_list(bullet, self.tanks.sprite_list)

                if len(hit_list_wall) > 0:
                    self.bullet.bullet_bounce(bullet, bullet.angle)
                    
                if len(hit_list_tank) > 0:    
                    explosion = Explosion(self.explosion_texture_list)
                    # set explosion center to location of first hit in list
                    explosion.center_x = hit_list_tank[0].center_x
                    explosion.center_y = hit_list_tank[0].center_y

                    # update explosion (sets first image)
                    explosion.update()
                    self.explosions_list.append(explosion)

                elif bullet.bottom > constants.SCREEN_HEIGHT or bullet.top < 0 or bullet.right < 0 or bullet.left > constants.SCREEN_WIDTH:
                    bullet.kill()
                    bullets -= 1
                
                for tank in hit_list_tank:
                    tank.set_life(-25)
                    arcade.play_sound(self.tank_explode,.5)
                    bullet.kill()
                    bullets -= 1

        powers = len(self.power.sprite_list)

        if powers > 0:
            for power in self.power.sprite_list:
                hit_list_wall = arcade.check_for_collision_with_list(power, self.ground.ground_sprite_list)
                hit_list_tank = arcade.check_for_collision_with_list(power, self.tanks.sprite_list)
                hit_list_bullet = arcade.check_for_collision_with_list(power, self.bullet.bullet_sprite_list)

                if len(hit_list_wall) > 0:
                    power.kill()
                    powers -= 1
                    self.power = SpawnRandom()
                    # self.power_down = SpawnPowerDown()

                # Paired with checker above in bullet collision checks. destroys/blocks bullet
                if len(hit_list_bullet) > 0:
                    power.kill()
                    powers -= 1
                    self.power = SpawnRandom()

                for tank in hit_list_tank:
                    # We should combine the entire powerups checker to work for any amount of powerups.
                    if self.power.sprite_list[-1].get_value() == 0:
                        print("Tis a bomb")
                        tank.set_life(-25)
                        arcade.play_sound(self.powerdown_sound,.8)
                    if self.power.sprite_list[-1].get_value() == 1:
                        print("Tis a power up")
                        tank.set_life(50)
                        arcade.play_sound(self.powerup_sound)
                        # this next if statement is still experimental. it needs delays between shots
                    if self.power.sprite_list[-1].get_value() == 2:
                        for _ in range(1, 5):
                            self.bullet.shoot_bullet(tank._get_center_x(), tank._get_center_y(), tank.angle)
                    power.kill()
                    powers -= 1
                    self.power = SpawnRandom()


        for tank in self.tanks.sprite_list:
            alive = tank.is_alive()
            if alive == False:
                # self.count = 75
                # explosion = Explosion(self.explosion_texture_list)
                # explosion.center_x = tank.center_x
                # explosion.center_y = tank.center_y

                # explosion.update()
                # self.explosions_list.append(explosion)
                name = tank.name
                tank.kill()
                self.switch_game_over_view(name)
                
        
    def wrap(self):
        
        # Check player1 for out-of-bounds
        if self.tanks.player1.left < 0:
            self.tanks.player1.left = 0
        elif self.tanks.player1.right > constants.SCREEN_WIDTH - 1:
            self.tanks.player1.right = constants.SCREEN_WIDTH - 1

        if self.tanks.player1.bottom < 0:
            self.tanks.player1.bottom = 0
        elif self.tanks.player1.top > constants.SCREEN_HEIGHT - 1:
            self.tanks.player1.top = constants.SCREEN_HEIGHT - 1

        # Check player2 for out of bounds    
        if self.tanks.player2.left < 0:
            self.tanks.player2.left = 0
        elif self.tanks.player2.right > constants.SCREEN_WIDTH - 1:
            self.tanks.player2.right = constants.SCREEN_WIDTH - 1

        if self.tanks.player2.bottom < 0:
            self.tanks.player2.bottom = 0
        elif self.tanks.player2.top > constants.SCREEN_HEIGHT - 1:
            self.tanks.player2.top = constants.SCREEN_HEIGHT - 1

        self.tanks.player1.update()
        self.tanks.player2.update()
        if self.bullet.bullet_sprite_list is not None:
            self.bullet.bullet_sprite_list.update()
            self.bullet.bullet_sprite_list.update_animation()
        if self.explosions_list is not None:
            self.explosions_list.update()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        # Forward/back
        if key == arcade.key.DOWN:
            self.tanks.player1.speed = constants.TANK_SPEED
        elif key == arcade.key.UP:
            self.tanks.player1.speed = -constants.TANK_SPEED
        elif key == arcade.key.SPACE:
            self.bullet.shoot_bullet(self.tanks.player1._get_center_x(), self.tanks.player1._get_center_y(), self.tanks.player1.angle)


        elif key == arcade.key.S:
            self.tanks.player2.speed = constants.TANK_SPEED
        elif key == arcade.key.W:
            self.tanks.player2.speed = -constants.TANK_SPEED
        elif key == arcade.key.Q:
            self.bullet.shoot_bullet(self.tanks.player2._get_center_x(), self.tanks.player2._get_center_y(), self.tanks.player2.angle)

        # Rotate left/right
        elif key == arcade.key.LEFT:
            self.tanks.player1.change_angle = constants.TANK_ANGLE_SPEED
        elif key == arcade.key.RIGHT:
            self.tanks.player1.change_angle = -constants.TANK_ANGLE_SPEED
        
        elif key == arcade.key.A:
            self.tanks.player2.change_angle = constants.TANK_ANGLE_SPEED
        elif key == arcade.key.D:
            self.tanks.player2.change_angle = -constants.TANK_ANGLE_SPEED

        elif key == arcade.key.ESCAPE:
            quit()
    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.tanks.player1.speed = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.tanks.player1.change_angle = 0
        
        elif key == arcade.key.W or key == arcade.key.S:
            self.tanks.player2.speed = 0
        elif key == arcade.key.A or key == arcade.key.D:
            self.tanks.player2.change_angle = 0
    
    def switch_game_over_view(self, loser):
        game_over = GameOverView(loser)
        self.window.show_view(game_over)
