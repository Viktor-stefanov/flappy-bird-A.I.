import pygame
import pickle
import random
import neat
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
bird_imgs = [pygame.transform.scale(pygame.image.load(fr"img\bird{n}.png").convert_alpha(), (60, 40)) for n in range(1, 4)]
bird_imgs.extend([pygame.transform.scale(pygame.image.load(fr"img\bird{n}.png").convert_alpha(), (60, 40)) for n in range(2, 0, -1)])
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("img","pipe.png")).convert_alpha())
restart_img = pygame.image.load(os.path.join("img", "restart_button.png")).convert_alpha()
menu_img = pygame.transform.scale(pygame.image.load(os.path.join("img", "menu.png")).convert_alpha(), (300, 400))
menu_img.set_colorkey((255, 255, 255))

score_font = pygame.font.SysFont("ComicSansMS", 40)
small_font = pygame.font.SysFont("ComicSansMS", 22)
GEN = 0

class Bird:
    """ bird class represents the player bird """
    imgs = bird_imgs
    def __init__(self, x, y):
        self.velocity = 1
        self.current_animation = 0
        self.animation_delay = 0
        self.x = x
        self.y = y
        self.tilt = 0
        self.tilt_delay = 0
        self.jump_ticks = -102
        self.jump_direction = 0

    def move(self):
        self.animate()
        # if the bird is titled downwards increase the speed - OBVIOUSLY
        if self.tilt < 0:
            self.velocity = 5 + (self.tilt * -0.05)
        self.y += self.velocity

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
        self.animation_delay += 1
        if self.animation_delay == 10:
            if self.tilt == -95:
                self.current_animation = -1
            self.current_animation = (self.current_animation + 1) % len(self.imgs)
            self.animation_delay = 0

    def jump(self):
        self.tilt_delay = 0
        self.tilt = 30
        self.current_animation = 0
        self.jump_ticks = 15
        self.jump_direction = -1 # -1 = up, 1 = down

    def get_mask(self):
        current_img = self.imgs[self.current_animation]
        tilted_img = pygame.transform.rotate(current_img, self.tilt)
        mask = pygame.mask.from_surface(tilted_img)
        return mask

    def draw(self, win):
        current_img = self.imgs[self.current_animation]
        # rotate the image and make it's rect's center to the non-rotated image's center so the collision works better
        rotated_image = pygame.transform.rotate(current_img, self.tilt)
        rotated_image_rect = rotated_image.get_rect(center=current_img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, rotated_image_rect)


class Pipes:
    img = pipe_img
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.top_y = random.randint(100, 400)
        self.top_pipe = pygame.transform.scale(pygame.transform.flip(self.img, False, True), (100, self.top_y))
        self.bottom_y = int(self.top_y + bird_imgs[0].get_height() * 4.5)
        self.bottom_height = SCREEN_HEIGHT - self.bottom_y - base_img.get_height()
        self.bottom_pipe = pygame.transform.scale(self.img, (100, self.bottom_height))
        self.passed = False

    def move(self):
        self.x -= 5

    def collides_with_bird(self, bird):
        bird_mask = bird.get_mask()
        bottom_mask = pygame.mask.from_surface(self.bottom_pipe)
        top_mask = pygame.mask.from_surface(self.top_pipe)

        top_offset = (self.x - bird.x, -round(bird.y) + 10)
        bottom_offset = (self.x - bird.x, self.bottom_y - round(bird.y) + 8)

        top_collision = bird_mask.overlap(top_mask, top_offset)
        bottom_collision = bird_mask.overlap(bottom_mask, bottom_offset)

        if top_collision or bottom_collision:
            return True

    def draw(self, win):
        win.blit(self.top_pipe, (self.x, 0))
        win.blit(self.bottom_pipe, (self.x, self.bottom_y))


class Base:
    """ background class that represents the side scrolling background that never ends.
    This is achieved by blitting 2 backgrounds simultaneously moving left """
    img = base_img
    def __init__(self):
        self.velocity = 5
        self.x = 0
        self.y = 688
        self.x_2 = self.img.get_width()

    def move(self):
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
                    play_game(win)
                elif event.key == pygame.K_m:
                    main_menu(win)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    # check if the user clicked on restart
                    mouse_pos = pygame.mouse.get_pos()
                    click = restart_button.collidepoint(mouse_pos[0], mouse_pos[1])
                    if click != 0:
                        play_game(win)

def redraw_window(win, bird, base, pipes, score=None):
    # redraw all the changes to the screen and update it
    win.blit(background_img, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    if score is not None:
        win.blit(score, (250, 100))
    base.draw(win)
    bird.draw(win)
    pygame.display.update()

def play_game(win):
    # create a 'clock' object to manipulate how fast/slow the in-game time passes
    clock = pygame.time.Clock()
    # create a sprite group to hold all the images that are on the screen
    # hard code the bird (x, y) pos (I feel like that's justified because the screen size is fixed. Create the player bird object
    bird_x = 200
    bird_y = 380
    bird = Bird(bird_x, bird_y)
    # create the first pipes and a pipes group
    pipes = [Pipes()]
    # create the base
    base = Base()
    game_started = False
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
                elif event.key == pygame.K_m:
                    main_menu(win)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    bird.jump()
                    game_started = True

        if game_started is True:
            for pipe in pipes:
                pipe.move()
                # check if the bird has passed a pipe
                if pipe.x < bird.x and pipe.passed is False:
                    pipe.passed = True
                    score += 1
                    pipes.append(Pipes())
                # check if a pipe has left the screen
                if pipe.x <= 0 - pipe.top_pipe.get_width():
                    pipes.remove(pipe)
                # check for collisions between the bird and the pipes
                hits = pipe.collides_with_bird(bird)
                fall = bird.y + bird_imgs[0].get_height() >= base.y
                if True in (hits, fall):
                    # get the high score and update it if the current score is higher
                    high_score = get_high_score()
                    if score > high_score:
                        high_score = score
                        update_high_score(str(score))

                    respawn_menu(win, score, high_score)

            # bird.animate()
            bird.move()
            base.move()

            score_render = score_font.render(str(score), False, (255, 255, 255))
            redraw_window(win, bird, base, pipes, score_render)
        else:
            if bird.y == 390:
                bird.velocity = -bird.velocity
            elif bird.y == 360:
                bird.velocity = -bird.velocity
            bird.move()

            redraw_window(win, bird, base, pipes)

        clock.tick(60)

def redraw_ai_window(win, birds, pipes, base, score, gen):
    # redraw the window while the AI is playing
    win.blit(background_img, (0, 0))
    base.draw(win)
    for pipe_pair in pipes:
        pipe_pair.draw(win)
    for bird in birds:
        bird.draw(win)

    # render the score, current generation and bird's alive and blit them to the screen
    score_render = score_font.render(f"Score: {score}", False, (255, 255, 255))
    gen_render = score_font.render(f"Generation: {gen}", False, (255, 255, 255))
    bird_count_render = score_font.render(f"Birds alive: {len(birds)}", False, (255, 255, 255))
    win.blit(score_render, (SCREEN_WIDTH - score_render.get_width() * 1.5, 10))
    win.blit(gen_render, (15, 10))
    win.blit(bird_count_render, (15, 50))

    pygame.display.update()

def ai_play_game(genomes, config):
    global GEN
    # clear the screen up to this point and create a clock object
    surface.fill((0, 0, 0))
    clock = pygame.time.Clock()

    # create a container for the birds, their respective neural network and genome
    GEN += 1
    birds = []
    gnms = []
    nets = []
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config) # create the neural network
        genome.fitness = 0 # assign initial fitness to each genome
        gnms.append(genome)
        nets.append(net)
        birds.append(Bird(200, 350))

    pipes = [Pipes()]
    base = Base()

    score = 0
    # main game loop
    while len(birds) > 0:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(), sys.exit()
                elif event.key == pygame.K_m:
                    main_menu(surface)

        # to avoid using the second pipe for input while still haven't passed the first, check on which pipe we are
        pipe_idx = 0
        if len(pipes) > 1 and birds[0].x >= pipes[0].x + 100:
            pipe_idx = 1

        # move the birds and give the activation function input, take the output and take action based on this output - jump? Yes/No
        for idx, bird in enumerate(birds):
            bird.move()
            gnms[idx].fitness += 0.1 # give the bird + 0.1 fitness for each frame it stays alive
            # distance = bird.y - (pipes[pipe_idx].top_y + 120) # Use if # of inputs is 1
            top_pipe_distance = abs(bird.y - pipes[pipe_idx].top_y) # use if # of inputs is 3
            bottom_pipe_distance = abs(bird.y - pipes[pipe_idx].bottom_y) # use if # of inputs is 3

            output = nets[birds.index(bird)].activate([bird.y, top_pipe_distance, bottom_pipe_distance]) # change according to the # of inputs
            if output[0] > 0.5:
                bird.jump()

        # rem = [] # remove things inside the for loop so that the index doesn't break
        add_pipe = False
        for pipe_pair in pipes:
            pipe_pair.move()
            for idx, bird in enumerate(birds):
                collision = pipe_pair.collides_with_bird(bird)
                if collision is True:
                    gnms[idx].fitness -= 2
                    birds.pop(idx)
                    gnms.pop(idx)
                    nets.pop(idx)

            if pipe_pair.x + pipe_img.get_width() < 0:
                pipes.remove(pipe_pair)
                # rem.append(pipe_pair)

            if len(birds) > 0:
                if pipe_pair.passed is False and birds[0].x >= pipe_pair.x:
                    pipe_pair.passed = True
                    add_pipe = True

        # for r in rem:
        #     pipes.remove(r)

        if add_pipe:
            score += 1
            for genome in gnms:
                genome.fitness += 5
            pipes.append(Pipes())

        for bird in birds:
            if bird.y + bird_imgs[0].get_height() - 10 >= 730 or bird.y < -50:
                nets.pop(birds.index(bird))
                gnms.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        base.move()
        redraw_ai_window(surface, birds, pipes, base, score, GEN)

        # save the bird if they reach score > 100
        if score > 100:
            with open("winner", "wb") as f:
                pickle.dump(nets[0], f)

def run():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))

    pop.run(ai_play_game, 50) # eval_genomes = fitness function

def main_menu(win):
    """ function to blit the contents of the main menu to the screen """
    global gen

    gen = 0 # reset the current generation of A.I. birds
    menu_bg = pygame.transform.scale(menu_img, (int(menu_img.get_width() * 1.5), int(menu_img.get_height() * 1.3)))
    menu_bg.set_colorkey((255, 255, 255))
    menu_pos = (SCREEN_WIDTH * 0.12, SCREEN_HEIGHT // 10)
    intro_pos = (SCREEN_WIDTH * 0.23, SCREEN_HEIGHT // 7)
    intro = score_font.render("Flappy Bird Clone", False, (188, 91, 63))
    rndm_pos = (SCREEN_WIDTH * 0.47, SCREEN_HEIGHT // 5)
    rndm = score_font.render("&", False, (188, 91, 63))
    intro2_pos = (SCREEN_WIDTH * 0.35, SCREEN_HEIGHT // 3.9)
    intro2 = score_font.render("NEAT A.I.", False, (188, 91, 63))
    by_pos = (SCREEN_WIDTH * 0.51, SCREEN_HEIGHT // 3.2)
    by = small_font.render("by Viktor Stefanov", False, (188, 91, 63))


    win.blit(background_img, (0, 0))
    win.blit(menu_bg, menu_pos)
    win.blit(intro, intro_pos)
    win.blit(rndm, rndm_pos)
    win.blit(intro2, intro2_pos)
    win.blit(by, by_pos)

    play_color = (250, 100, 85)
    ai_color = (250, 100, 85)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if play.collidepoint(mouse_x, mouse_y):
                        play_game(win)
                    elif ai_play.collidepoint(mouse_x, mouse_y):
                        run()
            elif event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(), sys.exit()

        play_game_pos = (SCREEN_WIDTH // 2.8, SCREEN_HEIGHT // 2.3)
        play_game_opt = score_font.render("Play Game", False, play_color)
        ai_game_pos = (SCREEN_WIDTH // 3.15, SCREEN_HEIGHT // 1.8)
        ai_game = score_font.render("Let A.I. play", False, ai_color)
        play = win.blit(play_game_opt, play_game_pos)
        ai_play = win.blit(ai_game, ai_game_pos)

        # check if the mouse is over the text on the screen and add a hover effect
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if play.collidepoint(mouse_x, mouse_y) != 0:
            play_color = 140, 168, 69
        else:
            play_color = (250, 100, 85)
        if ai_play.collidepoint(mouse_x, mouse_y) != 0:
            ai_color = 140, 168, 69
        else:
            ai_color = (250, 100, 85)

        pygame.display.update()


if __name__ == "__main__":
    main_menu(surface)