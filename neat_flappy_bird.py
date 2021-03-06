import pygame 
import neat 
import time 
import os 
import random 
pygame.font.init()


WIN_WIDTH =  580 
WIN_HEIGHT = 800 
DRAW_LINES = False


WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
#loading assets

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("all_assets","icon","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("all_assets","icon","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("all_assets","icon","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("all_assets","icon","pipe-red.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("all_assets", "icon","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("all_assets","icon","background-night.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

gen = 0
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #how much the bird is tiltilng while  moving up or down
    ROT_VEL = 20        #how much we are going to move bird at each frame 
    ANIMATION_TIME =5  #do the thing of flapping the wings 

    def __init__(self, x,y):
        self.x = x
        self.y = y 
        self.tilt = 0           #image tilting it is zero because the should be looking in the front while starting 
        self.tick_count = 0     #used for finding physics of the bird 
        self.vel = 0            #how fast the bird is moving 
        self.height = self.y     
        self.img_count = 0 
        self.img= self.IMGS[0]

  
    
    def jump(self):
        """
        we have taken the negative velocity because the edge of the flappy bird start from
        0,0 hence hence going upward requires NEGATIVE velocity and POSITIVE for the downward velocity
        and rest are same left -- -ve and right +ve
        """
        self.vel = -10.5 
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1 

        d = self.vel*self.tick_count + 1.5 * self.tick_count**2 

        # here we setting the terminal velocity dont go up and dont go down          
        if d>=16 :
            d = (d/abs(d))*16 
        if d < 0 :
            d -= 2 

        self.y = self.y + d 

        if d < 0 or self.y < self.height + 50 :
            if self.tilt < self.MAX_ROTATION:
                self.tilt= self.MAX_ROTATION
        else:
            if self.tilt >- 90 :
                self.tilt -= self.ROT_VEL
        
        
    def draw(self, win):
        self.img_count += 1 

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        
        elif  self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif  self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME *4: 
            self.img = self.IMGS[1]
        elif  self.img_count < self.ANIMATION_TIME*4+1:
            self.img = self.IMGS[0]
            self.img_count = 0 
        
        if self.tilt <= -80 : 
            self.img = self.IMGS[1]
            self.img_count =  self.ANIMATION_TIME*2 
        
        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

# ----     adding the Property of the pipe -----#
class Pipe:
    GAP = 200 
    VEL = 5 

    def __init__(self, x):
        self.x = x 
        self.height = 0

        self.top = 0 
        self.bottom = 0 
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP,(self.x, self.top))
        win.blit(self.PIPE_BOTTOM,(self.x, self.bottom))

    # Colllison 
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x , self.top -round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom-round(bird.y))
         

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True 
        return False

class Base:
    VEL  = 5 
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y ):
        self.y = y 
        self.x1 = 0
        self.x2 = self.WIDTH 
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0 :
            self.x2 = self.x1 + self.WIDTH 

    def draw(self,win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surfacae and blit it to the  window  
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


def draw_window(win, birds, pipes, base,score,gen,pipe_ind ):
    if gen == 0:
        gen = 1
    
    win.blit(BG_IMG,(0,0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score"+ str(score),1,(255,255,255)) 
    win.blit(text, (WIN_WIDTH - 10- text.get_width(), 10))

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    pygame.display.update()


def main(genomes, config):
    
    global WIN, gen
    win = WIN 
    nets = []
    ge = []
    birds = []

    for _,g in genomes:
        g.fitness = 0 
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(g) 



    base = Base(730)
    pipes = [Pipe(700)]

    clock = pygame.time.Clock()
    pygame.init()
    score = 0

    run = True
    while run and len(birds)>0:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit 
            else:
                run = False
                break

        pipe_ind = 0 
        if len(birds)> 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1 
        

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y- pipes[pipe_ind].bottom) ))
            if output[0] > 0.5 :
                bird.jump()

        base.move()
        add_pipe  = False 
        rem = []
        for pipe in pipes:
            pipe.move()
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1 
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True 
                add_pipe = True 
        
            
        

        if add_pipe:
            score += 1 
            for g in ge:
                g.fitness += 5
                
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)
        
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
                

        #base.move()    
        draw_window(WIN, birds,pipes,base, score, gen, pipe_ind)



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                 neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                  config_path)
    
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)
## -- adding the A.i --##

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)