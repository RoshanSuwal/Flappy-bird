import pygame
import random
import os
import time
import numpy as np
from keras.models import load_model

pygame.font.init()

model=load_model('flappy.h5')

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

def draw_window(win, bird, pipes, base, score,pipe_ind):
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
 
    if DRAW_LINES:
        try:
            pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
            pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
        except:
            pass
    # draw bird
    bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.display.update()


def run():

	data=np.empty([1,3])
	data0=np.empty([1,3])
	label=[]

	d=np.loadtxt('data1.txt')
	l=np.loadtxt('label1.txt')

	print(d)
	

	win=WIN
	base = Base(FLOOR)
	pipes = [Pipe(700)]
	score = 0

	flappy_bird=Bird(230,350)

	clock = pygame.time.Clock()

	run = True
	while run:
		clock.tick(300)
		jump=False

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
				break
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_SPACE:
					flappy_bird.jump()
					jump=True

				if event.key==pygame.K_a:
					np.savetxt('label.txt',label,fmt="%d")
					np.savetxt('data.txt',data,fmt="%f")
	    		
		pipe_ind = 0
		if len(pipes) > 1 and flappy_bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
			pipe_ind = 1                                                              # pipe on the screen for neural network input        

		pos=np.array([[flappy_bird.y,abs(flappy_bird.y-pipes[pipe_ind].height),abs(flappy_bird.y-pipes[pipe_ind].bottom)]])
		
		#data.append(pos)
		if len(d)>0:
			d=np.concatenate((d,pos))
		else:
			d=np.array(pos)
		
		if jump:
			data=np.concatenate((data,pos))
			label.append(1)
			l=np.concatenate((l,[1]))
			print(data,1,len(data))
		else:
			data0=np.concatenate((data0,pos))
			label.append(0)
			l=np.concatenate((l,[0]))
			print(pos,0,len(data))


		n_d=np.interp(pos,(40,700),(0,+1))
		output=model.predict(n_d)
		print("output")
		print(output[0][0])
		
		if output>0.1:
			flappy_bird.jump()
		flappy_bird.move()

		base.move()

		rem = []
		add_pipe = False
		for pipe in pipes:
		    pipe.move()
		    # check for collision

		    if pipe.collide(flappy_bird,win):
		    	run=False

		    if pipe.x + pipe.PIPE_TOP.get_width() < 0:
		        rem.append(pipe)

		    if not pipe.passed and pipe.x < flappy_bird.x:
		        pipe.passed = True
		        add_pipe = True

		if add_pipe:
		    score += 1
		    # can add this line to give more reward for passing through a pipe (not required)
		    pipes.append(Pipe(WIN_WIDTH))

		for r in rem:
		    pipes.remove(r)

		if flappy_bird.y+flappy_bird.img.get_height()-10>=FLOOR or flappy_bird.y<-50:
			run=False

		draw_window(WIN, flappy_bird, pipes, base, score,pipe_ind)
	
	

	#d=np.append(d,[data])
	#l=np.append(l,[label])

	#np.savetxt('label1.txt',l,fmt="%d")
	#np.savetxt('data1.txt',d,fmt="%f")

	np.savetxt('data2.txt',data)

	np.savetxt('label2.txt',label)

	np.savetxt('data0.txt',data0)
	
	#print(len(data),len(d),len(label),len(l))


if __name__=='__main__':
	run()


 	
