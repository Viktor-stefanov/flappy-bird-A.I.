import pygame
import random
import sys
import os
from score_actions import *

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 600, 800
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")

icon = pygame.image.load(os.path.join("img", "icon.png"))
pygame.display.set_icon(icon)

background_img = pygame.transform.scale(pygame.image.load(os.path.join("img", "bg.png")).convert_alpha(), (1000, 800))
base_img = pygame.transform.scale(pygame.image.load(os.path.join("img", "base.png")).convert_alpha(), (1000, 112))
bird_imgs = [pygame.transform .scale(pygame.image.load(fr"img\bird{n}.png").convert_alpha(), (60, 40)) for n in range(1, 4)]
pipe_img = pygame.image.load(os.path.join("img", "pipe.png")).convert_alpha()
restart_img = pygame.image.load(os.path.join("img", "restart_button.png")).convert_alpha()
menu_img = pygame.transform.scale(pygame.image.load(os.path.join("img", "menu.png")).convert_alpha(), (300, 400))
menu_img.set_colorkey((255, 255, 255))

score_font = pygame.font.SysFont("ComicSansMS", 40)

class Bird(pygame.sprite.Sprite):
    ''' bird class represents the player bird '''
    imgs = bird_imgs
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.velocity = 1
        self.animation_add = 1 # variable exists so as to be able to do 0 - 1 - 2 - 1 - 0 animations with the current_animation variable
        self.current_animation = 0
        self.rect = self.imgs[self.current_animation].get_rect()
        self.mask = pygame.mask.from_surface(self.imgs[self.current_animation])
        self.rect[0] = x
        self.rect[1] = y
        self.tilt = 0
        self.tilt_delay = 0
        self.jump_ticks = -102
        self.jump_direction = 0

    def update(self):
        # if the bird is titled downwards increase the speed - OBVIOUSLY
        if self.tilt < 0:
            self.velocity = 5 + (self.tilt * -0.05)
        self.rect.y += self.velocity

        # if the bird is not jumping and is headed downwards (hence self.velocity > 0 [positive -> down]) tilt it :D
        if self.velocity > 0 and self.tilt > -90 and self.jump_ticks == -16:
            if self.tilt_delay > 12:
                self.tilt -= 6.25
            self.tilt_delay += 1
        # reset the tilt delay on maximally tilting the bird
        if self.tilt == -95:
            self.tilt_delay = 0

        # handle jumping
        if self.jump_ticks >= -15:
            if self.jump_ticks < 0:
                self.velocity = -5 * (self.jump_ticks * 0.1)
            else:
                self.velocity = -5 * (self.jump_ticks * 0.15)
            self.jump_ticks += 1 * self.jump_direction

    def animate(self):
        if self.current_animation == 2 and self.animation_add == 1:
            self.animation_add = -1
        elif self.current_animation == 0 and self.animation_add == -1:
            self.animation_add = 1

        if self.tilt == -95:
            self.current_animation = -1
        self.current_animation = (self.current_animation + self.animation_add) % len(self.imgs)

    def jump(self):
        self.tilt_delay = 0
        self.tilt = 30
        self.current_animation = 0
        self.jump_ticks = 15
        self.jump_direction = -1 # -1 = up, 1 = down

    def draw(self, win):
        current_img = self.imgs[self.current_animation]
        # rotate the image and make it's rect's center to the non-rotated image's center so the collision works better
        rotated_image = pygame.transform.rotate(current_img, self.tilt)
        rotated_image_rect = rotated_image.get_rect(center=self.rect.center)
        win.blit(rotated_image, rotated_image_rect)


class Pipe(pygame.sprite.Sprite):
    img = pipe_img
    def __init__(self, other_pipe=None):
        pygame.sprite.Sprite.__init__(self)
        self.pipe = self.generate_pipe(other_pipe)
        self.mask = pygame.mask.from_surface(self.img)
        self.rect = self.pipe.get_rect()
        self.rect[0] = SCREEN_WIDTH
        self.passed = False
        if other_pipe is None:
            pipe_y = SCREEN_HEIGHT - (base_img.get_height() + self.pipe.get_height())
            self.rect[1] = pipe_y
        else:
            self.rect[1] = 0

    def generate_pipe(self, other_pipe):
        width = 100
        height = random.randint(50, 400)
        if other_pipe is not None:
            # the height of the inverted pipe is equal to the screen height - the base height - the height of the first pipe - double the bird sprite height
            height = (SCREEN_HEIGHT - base_img.get_height()) - other_pipe.rect[3] - (bird_imgs[0].get_height() * 4)
            pipe = pygame.transform.scale(self.img, (width, height))
            pipe = pygame.transform.flip(pipe, False, True)
        else:
            pipe = pygame.transform.scale(self.img, (width, height))

        return pipe

    def update(self):
        self.rect.x -= 5

    def draw(self, win):
        win.blit(self.pipe, self.rect)


class Base(pygame.sprite.Sprite):
    ''' background class that represents the side scrolling background that never ends.
    This is achieved by blitting 2 backgrounds simultaneously moving left '''
    img = base_img
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.img.get_rect()
        self.rect[1] = 688
        self.x = 0
        self.x_2 = self.img.get_width()
        self.velocity = 5

    def update(self):
        # move the base img to the left and once it is out to the left by the img width move it maximally to the right so it looks like it never ends
        self.x -= self.velocity
        self.x_2 -= self.velocity
        if self.x < self.img.get_width() * -1:
            self.x = self.img.get_width() - self.velocity
        if self.x_2 < self.img.get_width() * -1:
            self.x_2 = self.img.get_width() - self.velocity

    def draw(self, win):
        win.blit(self.img, (self.x, 688))
        win.blit(self.img, (self.x_2, 688))

def respawn_menu(win, scr, hs):
    score_label_position = (SCREEN_WIDTH // 2.4, 160)
    score_label = score_font.render("score:", False, (242, 92, 51))
    score_position = (SCREEN_WIDTH // 2.1, 205)
    score = score_font.render(str(scr), False, (255, 255, 255))
    high_score_label_position = (SCREEN_WIDTH // 2.9, 250)
    high_score_label = score_font.render("high score:", False, (242, 92, 51))
    high_score_position = (SCREEN_WIDTH // 2.1, 295)
    high_score = score_font.render(str(hs), False, (255, 255, 255))
    restart_position = (SCREEN_WIDTH // 2.6, 400)
    menu_label_position = (SCREEN_WIDTH // 4, 120)

    win.blit(menu_img, menu_label_position)
    win.blit(score_label, score_label_position)
    win.blit(score, score_position)
    win.blit(high_score_label, high_score_label_position)
    win.blit(high_score, high_score_position)
    restart_button = win.blit(restart_img, restart_position)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(), sys.exit()
                # use the enter key as a restart button as well
                elif event.key in (pygame.K_RETURN, pygame.K_r):
                    main(win)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    # check if the user clicked on restart
                    mouse_pos = pygame.mouse.get_pos()
                    click = restart_button.collidepoint(mouse_pos[0], mouse_pos[1])
                    if click != 0:
                        main(win)

def redraw_window(win, bird, base, pipes, score=None):
    # redraw all the changes to the screen and update it
    win.fill((0, 0, 0))
    win.blit(background_img, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    if score is not None:
        win.blit(score, (250, 100))
    base.draw(win)
    bird.draw(win)
    pygame.display.update()

def main(win):
    # create a 'clock' object to manipulate how fast/slow the in-game time passes
    clock = pygame.time.Clock()
    # create a sprite group to hold all the images that are on the screen
    all_sprites = pygame.sprite.Group()
    # hard code the bird (x, y) pos (I feel like that's justified because the screen size is fixed. Create the player bird object
    bird_x = 150
    bird_y = 380
    animation_delay = 1 # animation delay - update the animation if the animation_delay == 3 and then reset animation_delay = 0
    bird = Bird(bird_x, bird_y)
    all_sprites.add(bird)
    # create the first pipes and a pipes group
    pipes = pygame.sprite.Group()
    lower_pipe = Pipe()
    upper_pipe = Pipe(lower_pipe)
    for pipe in (lower_pipe, upper_pipe):
        pipes.add(pipe)
        all_sprites.add(pipe)
    # create the base
    base = Base()
    all_sprites.add(base)
    game_started = False
    passed = False
    score = 0
    # create the main game loop
    while True:
        # fetch all the events and check for specific keypresses, etc...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(), sys.exit()
                elif event.key == pygame.K_SPACE:
                    bird.jump()
                    game_started = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    bird.jump()
                    game_started = True

        if game_started is True:
            # handle the animation delay
            if animation_delay == 10:
                bird.animate()
                animation_delay = 0
            animation_delay += 1

            for pipe in pipes:
                # check if the bird has passed a pipe
                if pipe.rect.centerx < bird.rect[0] and pipe.passed is False:
                    passed = True
                    pipe.passed = True
                # check if a pipe has left the screen
                if pipe.rect[0] <= 0 - pipe.rect[2]:
                    pipes.remove(pipe)

            # check for collisions between the bird and the pipes
            hits = pygame.sprite.spritecollideany(bird, pipes, pygame.sprite.collide_rect_ratio(0.99))
            falls = pygame.sprite.collide_rect(bird, base)
            if hits is not None or falls != 0:
                # get the high score and update it if the current score is higher
                high_score = get_high_score()
                if score > high_score:
                    high_score = score
                    update_high_score(str(score))

                respawn_menu(win, score, high_score)

            all_sprites.update()

            # update the score if the player passed a pipe
            if passed is True:
                # generate new pipes
                lower_pipe = Pipe()
                upper_pipe = Pipe(lower_pipe)
                for pipe in (lower_pipe, upper_pipe):
                    pipes.add(pipe)
                    all_sprites.add(pipe)
                # increase the score and don't make the score ever-increasing :D
                score += 1
                passed = False

            score_render = score_font.render(str(score), False, (255, 255, 255))
            redraw_window(win, bird, base, pipes, score_render)
        else:
            if bird.rect.y == 390:
                bird.velocity = -bird.velocity
            elif bird.rect.y == 360:
                bird.velocity = -bird.velocity
            bird.update()

            redraw_window(win, bird, base, pipes)

        clock.tick(60)


if __name__ == "__main__":
    main(surface)