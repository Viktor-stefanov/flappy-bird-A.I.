import pygame
import sys
import os


class Bird:
    ''' bird class represents the player bird '''
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 5
        self.imgs = [pygame.image.load(fr"img\bird{n}.png").convert_alpha() for n in range(1, 4)]
        for i in range(len(self.imgs)):
            self.imgs[i] = pygame.transform.scale(self.imgs[i], (60, 40))
        self.current_img_idx = 0

    def animate(self):
        # change the sprite image and create a 'flying' illusion
        self.y += self.velocity
        self.current_img_idx = (self.current_img_idx + 1) % len(self.imgs)

    def jump(self):
        self.velocity = -5
        self.current_img_idx = 0

    def draw(self, win):
        win.blit(self.imgs[self.current_img_idx], (self.x, self.y))


class Pipe:
    def __init__(self):
        self.img = pygame.image.load(os.path.join("img", "pipe.png")).convert_alpha()

    def draw(self, win):
        pass

    def collides_with(self, bird):
        pass


class Background:
    ''' background class that represents the side scrolling background that never ends.
    This is achieved by blitting 2 backgrounds simultaneously moving left '''
    def __init__(self):
        self.first_bg = pygame.transform.scale(pygame.image.load(os.path.join("img", "background.png")), (1000, 800))
        self.second_bg = pygame.transform.scale(pygame.image.load(os.path.join("img", "background.png")), (1000, 800))
        self.x = 0
        self.x_2 = self.second_bg.get_width()
        self.velocity = 10

    def move(self):
        self.x -= self.velocity
        self.x_2 -= self.velocity
        if self.x < self.first_bg.get_width() * -1:
            self.x = self.first_bg.get_width() - self.velocity
        if self.x_2 < self.second_bg.get_width() * -1:
            self.x_2 = self.second_bg.get_width() - self.velocity

    def draw(self, win):
        win.blit(self.first_bg, (self.x, 0))
        win.blit(self.second_bg, (self.x_2, 0))

def setup():
    # set up function to set up the display and return the drawing surface
    pygame.init()
    win = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Flappy Bird Clone")

    icon = pygame.image.load(os.path.join("img", "icon.png"))
    pygame.display.set_icon(icon)

    return win

def redraw_window(win, bird, background):
    # redraw all the changes to the screen and update it
    win.fill((0, 0, 0))
    background.draw(win)
    bird.draw(win)
    pygame.display.update()

def main(win):
    # create a 'clock' to manipulate the game fps
    clock = pygame.time.Clock()
    # hard code the bird (x, y) pos (I feel like that's justified because the screen size is fixed. Create the player bird object
    bird_x = 100
    bird_y = 380
    animation_delay = 0 # animation delay - update the animation if the animation_delay > 10 and then reset animation_delay = 0
    bird = Bird(bird_x, bird_y)
    # create the background
    background = Background()
    # create the main game loop
    while True:
        # fetch all the events and check for specific keypresses, etc...
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(), sys.exit()
                elif event.key == pygame.K_SPACE:
                    bird.jump()

        if animation_delay == 2:
            bird.animate()
            animation_delay = 0
        animation_delay += 1
        # redraw all the images and their changes to the screen
        background.move()
        redraw_window(win, bird, background)
        clock.tick(30)


if __name__ == "__main__":
    window = setup()
    main(window)