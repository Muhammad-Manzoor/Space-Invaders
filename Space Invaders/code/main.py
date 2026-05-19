import pygame
from os.path import join
from random import randint, uniform
import sys, os

def resource_path(relative_path):
    try:
        return os.path.join(sys._MEIPASS, relative_path)  # for .exe
    except AttributeError:
        return os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), relative_path)  # for .py


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(resource_path('images/player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (win_width/2, win_height/2))
        self.direction = pygame.math.Vector2()
        self.speed = 300

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 800
        
        # mask
        self.mask = pygame.mask.from_surface(self.image)
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True
    
    def update(self, dt):
        # input
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        
        recentKeys = pygame.key.get_just_pressed()
        if recentKeys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
            
        self.cooldown_duration = 800 - current_score // 7
        self.speed = 300 + current_score // 15
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, win_width), randint(0, win_height)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_position = surf
        self.image = self.original_position
        self.rect = self.image.get_frect(center = pos)
        
        # timer
        self.start_timer = pygame.time.get_ticks()
        self.timer_duration = 4000
        
        # movement
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 500)
        
        # rotation
        self.rotational_speed = randint(40, 80)
        self.rotation = 0
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        self.speed = randint(max(int(current_score /  2), 300), max(int(current_score / 2), 400))
        if pygame.time.get_ticks() - self.start_timer >= self.timer_duration:
            self.kill()
            
        self.rotation += self.rotational_speed * dt
        self.image = pygame.transform.rotozoom(self.original_position, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        self.speed = 500
        explosion_sound.play()
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions():
    global running, laser_points
    
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        damage_sound.play()
        pygame.time.wait(200)
        game_music.stop()
        pygame.time.wait(1800)
        running = False 
        
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            laser_points += 10

def display_score():
    global current_score
    current_time =  pygame.time.get_ticks() // 100
    current_score = current_time + laser_points
    text_surf = font.render(str(current_score), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (win_width / 2, win_height - 50))
    
    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 0).move(0, -8), 5, 10)
    display_surface.blit(text_surf, text_rect)

# general setup
pygame.init()
win_width, win_height = 1280, 720
display_surface = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Space shooter")
running = True
clock = pygame.time.Clock()
laser_points = 0

# import
star_surf = pygame.image.load(resource_path('images/star.png')).convert_alpha()
laser_surf = pygame.image.load(resource_path('images/laser.png')).convert_alpha()
meteor_surf = pygame.image.load(resource_path('images/meteor.png')).convert_alpha()
font = pygame.font.Font(resource_path('images/Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(resource_path(f'images/explosion/{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(resource_path('audio/laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(resource_path('audio/explosion.wav'))
damage_sound = pygame.mixer.Sound(resource_path('audio/damage.ogg'))
game_music = pygame.mixer.Sound(resource_path('audio/game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops = -1)


# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
    i == 1
player = Player(all_sprites)



# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

display_score()
while running:
    
    dt = clock.tick() / 1000
    
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, win_width), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    # update
    all_sprites.update(dt = dt)
    collisions()
    
    # draw the game
    display_surface.fill('#3a2e3f')
    all_sprites.draw(display_surface)
    display_score()
    
    pygame.display.update()

pygame.quit() 