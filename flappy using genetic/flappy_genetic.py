import pygame
import random
import os
import time
import numpy as np

from keras.models import Sequential
from keras.layers import Dense,Activation

import genetic as g
from genetic import GeneticAlgorithm as GA

pygame.font.init()

WIN_WIDTH=600
WIN_HEIGHT=800
FLOOR=730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

def get_model():
	model=Sequential()
	model.add(Dense(3,activation="relu",input_dim=3))
	model.add(Dense(1,activation="tanh"))
	model.compile(optimizer="adam",
		loss="binary_crossentropy",
		metrics=['accuracy'])
	return model

class Genome:
	def __init__(self):
		self.fitness=0
		self.model=get_model()
	def prediction(self,inputs):
		return self.model.predict(inputs)

class Bird:

	MAX_ROTATION=25
	IMGS=bird_images
	ROT_VEL=20
	ANIMATION_TIME=5

	def __init__(self, x, y):
		self.x=x
		self.y=y
		self.tilt=0 
		self.vel=0
		self.height=self.y
		self.img_count=0
		self.img=self.IMGS[0]
		self.tick_count=0

	def jump(self):
		self.vel=-10.5
		self.tick_count=0
		self.height=self.y
	
	def move(self):
		self.tick_count+=1
		displacement=self.vel*(self.tick_count)+0.5*3*self.tick_count**2

		if displacement>=16:
			displacement=(displacement/abs(displacement))*16

		if displacement<0:
			displacement-=2

		self.y=self.y+displacement

		if displacement<0 or self.y<self.height+50:
			if self.tilt<self.MAX_ROTATION:
				self.tilt=self.MAX_ROTATION
			else:
				if self.tilt>-90:
					self.tilt-=self.ROT_VEL
	
	def draw(self,win):
		self.img_count += 1
		if self.img_count<=self.ANIMATION_TIME:
			self.img=self.IMGS[0]
		elif self.img_count<=self.ANIMATION_TIME*2:
			self.img=self.IMGS[1]
		elif self.img_count<=self.ANIMATION_TIME*3:
			self.img=self.IMGS[2]
		elif self.img_count<=self.ANIMATION_TIME*4:
			self.img=self.IMGS[1]
		elif self.img_count<=self.ANIMATION_TIME*4+1:
			self.img=self.IMGS[0]
			self.img_count=0
		if self.tilt<=-80:
			self.img=self.IMGS[1]
			self.img_count=self.ANIMATION_TIME*2
		blitRotateCenter(win,self.img,(self.x,self.y),self.tilt)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)
    	

class Pipe():
	GAP=200
	vel=5

	def __init__(self,x):
		self.x=x
		self.height=0
		self.top=0
		self.bottom=0
		self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
		self.PIPE_BOTTOM=pipe_img
		self.passed=False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP
	def move(self):
		self.x-=self.vel
	def draw(self,win):
		win.blit(self.PIPE_TOP,(self.x,self.top))
		win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))
	def collide(self,bird,win):
		bird_mask=bird.get_mask()
		top_mask=pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM)
		top_offset=(self.x-bird.x,self.top-round(bird.y))
		bottom_offset=(self.x-bird.x,self.bottom-round(bird.y))

		b_point=bird_mask.overlap(bottom_mask,bottom_offset)
		t_point=bird_mask.overlap(top_mask,top_offset)

		if b_point or t_point:
			return True

		return False

class Base:
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score,pipe_ind,generation):
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    for bird in birds:
    	if DRAW_LINES:
    		try:
    			pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
    			pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
    		except:
    			pass
    	bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))
    gen=STAT_FONT.render("Generation: "+str(generation),1,(255,255,255))
    win.blit(gen,(10,10))
    pygame.display.update()


def run(genomes,nos,generation):
	win=WIN
	base = Base(FLOOR)
	pipes = [Pipe(700)]
	score = 0

	##code for genetic algorithm implementation
	birds=[]
	parents=[]

	for i in range(nos):
		birds.append(Bird(230,350))
		#genomes.append(Genome())

	clock = pygame.time.Clock()

	run = True
	while run and len(birds)>0:
		clock.tick(300)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
				break
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_SPACE:
					flappy_bird.jump()
	    		
		pipe_ind = 0
		if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
			pipe_ind = 1                                                              # pipe on the screen for neural network input        

		for x,bird in enumerate(birds):
			bird.move()

			pos=np.array([[bird.y,abs(bird.y-pipes[pipe_ind].height),abs(bird.y-pipes[pipe_ind].bottom)]])
			output=genomes[birds.index(bird)].prediction(pos)

			if output>0.5:
				bird.jump()

		#pos=np.array([[flappy_bird.y,abs(flappy_bird.y-pipes[pipe_ind].height),abs(flappy_bird.y-pipes[pipe_ind].bottom)]])
	
		#flappy_bird.move()

		base.move()

		rem = []
		add_pipe = False
		for pipe in pipes:
		    pipe.move()
		    # check for collision

		    for bird in birds:
		    	if pipe.collide(bird,win):
		    		if len(birds)<10:
		    			parents.append(genomes.pop(birds.index(bird)))
		    		else:
		    			genomes.pop(birds.index(bird))
		    		birds.pop(birds.index(bird))
		    		print(len(birds),len(genomes))

		    if pipe.x + pipe.PIPE_TOP.get_width() < 0:
		        rem.append(pipe)

		    if not pipe.passed and pipe.x < bird.x:
		        pipe.passed = True
		        add_pipe = True

		if add_pipe:
		    score += 1
		    # can add this line to give more reward for passing through a pipe (not required)
		    pipes.append(Pipe(WIN_WIDTH))

		for r in rem:
		    pipes.remove(r)

		for bird in birds:
			if bird.y+bird.img.get_height()-10>=FLOOR or bird.y<-50:
				if len(birds)<10:
					parents.append(genomes.pop(birds.index(bird)))
				else:
					genomes.pop(birds.index(bird))
				birds.pop(birds.index(bird))
				print(len(birds),len(genomes),"boundary")
					

		draw_window(WIN, birds, pipes, base, score,pipe_ind,generation)
		#print(score)
	
	return parents

def config():
	genomes=[]
	for i in range(20):
		genomes.append(Genome())

	listofGenome=genomes.copy()
	ga=GA()
	generation=10

	while generation>0:
		parents=run(genomes,20,generation)

if __name__=='__main__':
	generation=10
	genomes=[]
	ga=GA()
	for i in range(20):
		genomes.append(Genome())

	ls=genomes.copy()


	while generation>0:
		print("length of genomes",len(genomes))
		parents=run(genomes,20,generation)
		print("next generation",generation)
		best_gene=parents[0]
		ref_weights=best_gene.model.get_weights()
		fp=[g.flatten_weights(m1.model.get_weights()) for m1 in parents]
		nw=ga.applyGenetic(fp,fp[-1],20)
		print(len(parents),len(ls))
		for i in range(20):
			ls[i].model.set_weights(g.unflatten_weights(ref_weights,nw[i]))
		genomes=ls.copy()
		
		print(len(genomes),len(parents))
		generation-=1


 	
