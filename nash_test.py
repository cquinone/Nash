import pygame,os
import pygame.font
from pygame.locals import *
from shapely.geometry import Polygon,Point
import numpy as np
from matplotlib import pyplot as plt
import math
import time


pygame.init()
pygame.font.init()

#fonts
Startfont = pygame.font.Font(os.path.join(os.sep,"Users", "chrisquinones", "work","prog","pyproj","games","nash","silkscreen",'slkscr.tff'), 22)
Titlefont =  pygame.font.Font(os.path.join(os.sep,"Users", "chrisquinones", "work","prog","pyproj","games","nash","silkscreen",'slkscrb.tff'), 42)
Midfont = pygame.font.Font(os.path.join(os.sep,"Users", "chrisquinones", "work","prog","pyproj","games","nash","silkscreen",'slkscr.tff'), 14)
Smallfont = pygame.font.Font(os.path.join(os.sep,"Users", "chrisquinones", "work","prog","pyproj","games","nash","silkscreen",'slkscr.tff'), 12)

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
 
# Constants
WIDTH = 800
HEIGHT = 600
dt = 1/float(4)
g = 9.8
overall_time = 0


def convert_time(time):
	#convert time from counter to mins:secs
	mins = str(int(time/60))
	if len(mins) == 1:
		mins = "0"+mins
	secs = 60*(time/60 - int(time/60))
	secs = str(int(secs))
	if len(secs) == 1:
		secs = "0"+secs
	converted = str(mins)+":"+str(secs)
	return converted


def mask(nash,xmin,xmax,ymax,ymin):
	#make a polygon that defines collision mask for object
	ymax = ymax - ymin
	top_right	= np.array([nash.pos[0]+xmax,nash.pos[1]+ymax]) 
	top_left	= np.array([nash.pos[0]+xmin,nash.pos[1]+ymax])			
	btm_right	= np.array([nash.pos[0]+xmax,nash.pos[1]])		#ymin is assumed to always be 0
	btm_left	= np.array([nash.pos[0]+xmin,nash.pos[1]])
	top_right.shape	= (2,1) 
	top_left.shape	= (2,1)
	btm_right.shape	= (2,1)
	btm_left.shape	= (2,1)
	points = [top_left,top_right,btm_right,btm_left]
	poly   = Polygon(points)
	return points, poly


def entity_collide(screen,nash,keys,lvl):
	#collision check for items/enemies/special blocks
	collided = False
	
	#get current yvel, jump state
	banjo = False
	jerry = False
	sub = False
	all_entities = []  # list to hold entities + projectiles
	
	#preprocess entities and throw in projectiles
	for entity in lvl.entities:
		all_entities.append(entity)
		if entity.projectiles:
			for projectile in entity.projectiles:
				all_entities.append(projectile)


	for entity in all_entities:
		if nash.jump: #cover jump mask case
			if nash.jump_poly.intersects(entity.poly):
				collided = True
		else:
			if nash.dir == "idle":
				if nash.idle_poly.intersects(entity.poly):
					collided = True
			elif nash.dir == "right" or nash.dir == "left":
				if nash.walk_poly.intersects(entity.poly):
					collided = True		
		
		#if collided with an entity this loop, move nash and act according to entity type
		if collided:
			if entity.type == "FBI":
				#pause for a sec or so, draw FBI caught message
				pygame.time.wait(400)
				collide_text = Startfont.render("The FBI caught you.", True, BLACK)
				screen.fill(WHITE)
				screen.blit(collide_text, [WIDTH/2-100,HEIGHT/2])
				pygame.display.flip()
				pygame.time.wait(1080)
				#set jump and yvel to 0
				nash.jump = False
				nash.yvel = 0
				nash.pos[0] = lvl.start[0]
				nash.pos[1] = lvl.start[1]
			
			elif entity.type == "Ladder":
				if keys[pygame.K_i]:
					#send nash up the ladder
					nash.yvel = -20
					nash.jump = True
			
			elif entity.type == "Banjo":
				collide_text = Midfont.render("Banjo found! +5 seconds!", True, BLACK)
				screen.blit(collide_text, [nash.pos[0], nash.pos[1]-20])
				pygame.display.flip()
				pygame.time.wait(1080)
				lvl.entities.remove(entity)
				banjo = True

			elif entity.type == "Tim" or entity.type == "Puff":
				#pause for a sec or so
				pygame.time.wait(900)
				#set jump and yvel to 0
				nash.jump = False
				nash.yvel = 0
				nash.pos[0] = lvl.start[0] 
				nash.pos[1] = lvl.start[1]

			elif entity.type == "springer":
				collide_text1 = Startfont.render("Watch 5 episodes of The Jerry Springer Show.", True, BLACK)
				collide_text2 = Startfont.render("-20 seconds",True, BLACK)
				screen.fill(WHITE)
				screen.blit(collide_text1, [WIDTH/2-350,HEIGHT/2])
				screen.blit(collide_text2, [WIDTH/2-300,HEIGHT/2 + 40])
				pygame.display.flip()
				pygame.time.wait(1620)
				nash.jump = False
				nash.yvel = 0
				nash.pos[0] = lvl.start[0] 
				nash.pos[1] = lvl.start[1]
				jerry = True

			elif entity.type == "sub":
				collide_text1 = Midfont.render("Grab lunch with Jared Fogle",True, BLACK)
				collide_text2 = Midfont.render("- 1 minute",True, BLACK)
				screen.blit(collide_text1, [nash.pos[0]-5, nash.pos[1]-30])
				screen.blit(collide_text2, [nash.pos[0]+30, nash.pos[1]-10])
				pygame.display.flip()
				pygame.time.wait(1280)
				lvl.entities.remove(entity)
				sub = True

			# now break collision check loop as you've collided with something
			break

	return nash, banjo, jerry, sub


class Scene:
	def __init__(self,width,height):
		#define level boundaries and whether its "over"
		self.width	= width
		self.height	= height
		self.top_right	= np.array([self.width,self.height])  
		self.top_left	= np.array([0,self.height])	 
		self.btm_right 	= np.array([self.width,0])	 
		self.btm_left	= np.array([0,0])
		self.top_right.shape	= (2,1) 
		self.top_left.shape		= (2,1)
		self.btm_right.shape	= (2,1)
		self.btm_left.shape		= (2,1)
		self.points = [self.top_left,self.top_right,self.btm_right,self.btm_left]
		self.poly   = Polygon(self.points)
		self.timer = 0
		self.over = False

	def draw(self,screen,nash_time):
		screen.fill(WHITE)
		# draw blocks/art first
		for piece in self.art:
			screen.blit(piece.pic,piece.pos)

		for block in self.blocks:
			screen.blit(block.pic,block.pos)
		
		# then entities
		for entity in self.entities:
			# make sure to draw projectiles
			if entity.projectiles:
				for projectile in entity.projectiles:
					screen.blit(projectile.pic, projectile.pos)

			screen.blit(entity.pic,entity.pos)
		
		time = Titlefont.render(nash_time,True,RED) #convert time puts it in mins:secs
		screen.blit(time, [0,0])


class Title_lvl(Scene):
	def __init__(self,width,height,screen):
		super().__init__(width,height)
		self.blocks = []
		self.name = "title"

	def title_draw(self,screen):
		screen.fill(WHITE)
		nash_intro	= pygame.image.load("pics/nash_final.png").convert_alpha()
		nash_intro	= pygame.transform.scale(nash_intro, [int(1.4*int(300*1.14)),int(1.4*int(250*1.2))])
		screen.blit(nash_intro, [165,100])
		if self.timer < 20:
			start = Startfont.render("[Hit Enter to Play]",True, BLACK) 
			screen.blit(start,[280,535])
			self.timer = self.timer + 1
		else:
			self.timer = self.timer + 1
			if self.timer > 30: #basically saying: dont draw for X frames, makes flicker effect
				self.timer = 0
		title = Titlefont.render("- FIVE MINUTES -",True, BLACK)
		screen.blit(title, [160, 20])
		authors = Smallfont.render("(Created by Chris Quinones and Co.)", True, BLACK)
		screen.blit(authors, [275,70])

class Level1(Scene):
	def __init__(self,width,height,screen):
		super().__init__(width,height)
		#-----LEVEL CONSTRUCTION-------------------------------------------------------------------------------------------------#
		self.blocks = [Block(0,450),Block(50,450), Block(100,450), Block(150,450), Block(240,405),Block(335,355),Block(160,580),
						Block(425,310),Block(607,315),Block(657,315),Block(707,315),Block(-22,580),Block(28,580),Block(78,580),
						Block(128,580),Block(178,580),Block(228,580),Block(278,580),Block(328,580),Block(378,580),Block(428,580),
						Block(478,580),Block(528,580),Block(578,580),Block(628,580),Block(678,580),Block(728,580),Block(778,580)]
		
		self.art = [Item(630,238,104,78,"pics/doyle.png",[]),Item(165,0,100,100,"pics/sun_boi.png",[])]
		#-----ENEMY/ITEM PLACEMENT-----------------------------------------------------------------------------------------------#
		self.entities = [FBI(561,535.8,"left"),FBI(272,535.8,"right"),Banjo(412,550),Ladder(765,529),Ladder(765,478),Ladder(765,427),
		                 Ladder(765,376),Ladder(765,325)]
		#------------------------------------------------------------------------------------------------------------------------#
		self.pic = pygame.image.load("pics/background1.png").convert_alpha()
		self.pic = pygame.transform.scale(self.pic, [800,600])
		self.finish = [672,260]
		self.start = [10,300]
		self.name = "lvl1"

	def events(self,screen,nash,keys):
		banjo_found = False
		jerry = False
		sub = False
		
		#first check if end of level reached
		if abs(nash.pos[0] - self.finish[0]) <= 10 and abs(nash.pos[1] - self.finish[1]) <= 10:
			self.over = True  #
			#print level end message
			lvl_over_text1 = Midfont.render("Kris Kristofferson's music",True, BLACK)
			lvl_over_text2 = Midfont.render("is not a legitimate excuse",True,BLACK)
			screen.blit(lvl_over_text1, [nash.pos[0]-250,nash.pos[1]-60])
			screen.blit(lvl_over_text2, [nash.pos[0]-250,nash.pos[1]-40])
			pygame.display.flip()
			pygame.time.wait(1320)

		else: # check for collisions with entities (non-blocks), keys = keyboard state			
			nash, banjo_found, jerry, sub = entity_collide(screen,nash,keys,self)
		
		return nash, banjo_found, jerry, sub


class Level2(Scene):
	def __init__(self,width,height,screen):
		super().__init__(width,height)
		#-----LEVEL CONSTRUCTION-------------------------------------------------------------------------------------------------#
		self.blocks = [Block(530,110),Block(480,110),Block(430,110),Block(380,110),Block(500,300),Block(550,300),Block(600,300),
					   Block(450,300),Block(400,300),Block(650,300),Block(700,300),Block(750,300),Block(330,110),Block(280,110),
					   Block(350,300),Block(300,300),Block(230,110),Block(80,110),Block(30,110),Block(-20,110),Block(150,150),
					   Block(212,405),Block(162,405),Block(152,580),Block(202,580),Block(252,580),Block(302,580),Block(352,580),
					   Block(402,580),Block(452,580),Block(502,580),Block(552,580),Block(602,580),Block(652,580),Block(702,580),
					   Block(752,580),Block(560,420),Block(610,420)]
		self.art = [Item(700,492,61,88,"pics/door.png",[])]
		#-----ENEMY/ITEM PLACEMENT-----------------------------------------------------------------------------------------------#
		self.entities = [Tim(500,255, "right"),FBI(730,255,"left"),FBI(165,105,"left"),Springer(0,435),Banjo(30,346),Sub(580,385),
						 Ladder(525,425),Ladder(525,476),Ladder(525,527)]
		#------------------------------------------------------------------------------------------------------------------------#
		self.finish = [721,530]
		self.start = [10,55]
		self.name = "lvl2"

	def events(self,screen,nash,keys):
		banjo_found = False
		jerry = False
		sub = False

		if abs(nash.pos[0] - self.finish[0]) <= 10 and abs(nash.pos[1] - self.finish[1]) <= 10:
			self.over = True
			#print level end message
			lvl_over_text = Midfont.render("TIM GET OUTTA MY HOUSE",True, BLACK)
			screen.blit(lvl_over_text, [nash.pos[0]-250,nash.pos[1]-50])
			pygame.display.flip()
			pygame.time.wait(1220)
		
		else:
			nash, banjo_found, jerry, sub = entity_collide(screen,nash,keys,self)
		
		return nash, banjo_found, jerry, sub


class Item():
	def __init__(self,x,y,w,h,image, projectiles):
		self.pos = [x,y]
		self.width  = w 
		self.height = h
		self.pic = pygame.image.load(image).convert_alpha()
		self.pic = pygame.transform.scale(self.pic, [self.width,self.height])
		self.projectiles = projectiles # only filled for projectile users


class Block(Item):
	def __init__(self,x,y):
		super().__init__(x,y,50,20,"pics/block.png",[])
		self.pic.set_colorkey(WHITE)
		self.points,self.poly = mask(self,0,46,20,0)
 

class FBI(Item):
	def __init__(self,x,y,direction):
		super().__init__(x,y,36,45,"pics/FBI.png",[])
		self.direction = direction
		if direction == "right":
			self.pic = pygame.transform.flip(self.pic,True,False)
		self.points,self.poly = mask(self,0,self.width,1.2*self.height,0) #mask/img go to roughly 36,44
		self.type = "FBI"


class Springer(Item):
	def __init__(self,x,y):
		super().__init__(x,y,153,165,"pics/jerry2.png",[])
		self.points,self.poly = mask(self,0,self.width,self.height,0)
		self.type = "springer"


class Sub(Item):
	def __init__(self,x,y):
		super().__init__(x,y,80,32,"pics/sub.png",[])
		self.points,self.poly = mask(self,0,self.width,self.height,0)
		self.type = "sub"

class Ladder(Item):
	def __init__(self,x,y):
		super().__init__(x,y,30,51,"pics/ladder.png",[])
		self.points,self.poly = mask(self,0,.85*self.width,self.height,0)  #mask is thinner to prevent climbing side rails
		self.type = "Ladder"


class Banjo(Item):
	def __init__(self,x,y):
		super().__init__(x,y,54,16,"pics/banjo.png",[])
		self.points,self.poly = mask(self,0,self.width,self.height,0) 
		self.type = "Banjo"


class Extra_Credit():
	def __init__(self,x,y):
		self.pos = [x,y]


class Tim(Item):
	def __init__(self,x,y,direction):
		super().__init__(x,y,33,43,"pics/tim.png",[])
		self.start = True
		self.track = [i * .8 for i in range(self.pos[0], self.pos[0]+50)]  # range of steps, each .1 long
		self.step = 20
		self.puff_buffer = 0  # timer for how long before creating another puff
		if direction == "right":
			self.pic = pygame.transform.flip(self.pic,True,False)			# adjust image oritentation
		self.points,self.poly = mask(self,0,self.width,.9*self.height,0)
		self.type = "Tim"

	def update(self):
		# here we update pos based on loop, if start = True, go forward
		if self.start:
			if self.step + 1 <= len(self.track) - 1:
				self.step = self.step + 1
				self.pos[0] = self.track[self.step]
			else:
				self.start = False
		
		else:
			if self.step - 1 >= 0:
				self.step = self.step - 1
				self.pos[0] = self.track[self.step]
			else:
				self.start = True

		# now update mask position
		self.points,self.poly = mask(self,0,self.width,.9*self.height,0)

		# update how many puffs
		if self.puff_buffer > 0:
			self.puff_buffer = self.puff_buffer - 1
		else:
			if len(self.projectiles) < 2:
				self.projectiles.append(Puff(self.pos[0]+32,self.pos[1]+28))
				self.puff_buffer = 25
		
		# update puff positions / masks
		for puff in self.projectiles:
			puff.points, puff.poly = mask(puff,0,puff.height,puff.width,0)
			if puff.step <= len(puff.track) - 1:
				puff.pos[0],puff.pos[1] = puff.track[puff.step][0], puff.track[puff.step][1]
				puff.step = puff.step + 1
			else:
				self.projectiles.remove(puff)


class Puff(Item):
	def __init__(self,x,y):
		super().__init__(x,y,20,17,"pics/puff.png",[])
		self.type = "Puff"
		self.step = 0
		self.track = [(i,y + 3*math.sin(i)) for i in range(int(self.pos[0]), int(self.pos[0]+120))]
		self.points,self.poly = mask(self,0,46,20,0)


class Player():
	def __init__(self):
		self.timer = 0


class Nash(Player):
	def __init__(self,x,y):
		super().__init__()
		self.pos = [x,y]
		self.width  = 38 #1.6 multiplied by 24x34 (the actual size of nash image, not canvas)
		self.height = 54
		self.name	= "Nash"
		self.pic_right_idle 	= pygame.image.load("pics/nash_side.png").convert_alpha()
		self.pic_right_idle 	= pygame.transform.scale(self.pic_right_idle, [self.width,self.height])
		self.pic_left_idle		= pygame.transform.flip(self.pic_right_idle,True,False)

		self.pic_right_walk 	= pygame.image.load("pics/nash_walk.png").convert_alpha()
		self.pic_right_walk 	= pygame.transform.scale(self.pic_right_walk, [self.width,self.height])
		self.pic_left_walk		= pygame.transform.flip(self.pic_right_walk,True,False)
		
		self.jump_pic_right		= pygame.image.load("pics/nash_jump_right.png").convert_alpha()
		self.jump_pic_right 	= pygame.transform.scale(self.jump_pic_right, [self.width,self.height])
		self.jump_pic_left	 	= pygame.transform.flip(self.jump_pic_right, True,False)
		
		self.idle_points,self.idle_poly = mask(self,8,30,54,0)   #make vectors/poly for idle mask polygon, for now leave as square
		self.walk_points,self.walk_poly = mask(self,7,29,54,0)   #5-19 is nash image (24x34 canvas), mult by 1.6 -> 8x30
		self.jump_points,self.jump_poly = mask(self,0,38,54,0)
		self.yvel = 0									  	   
		self.old_dir = "right"
		self.dir = "idle"
		self.fall = False
		self.still_fall = False #extra bool to cover falling case after jump
		self.jump = True
		self.walk = False #False means idle, True means walk image
		self.stand_count = 0
		self.walk_timer = 5

	def update_pos(self,screen,lvl):
		new_x = self.pos[0] #default values
		new_y = self.pos[1]
		
		#first check if you're jumping still
		if self.jump:
			self.yvel = self.yvel + g*dt
			new_y = self.pos[1] + self.yvel*dt
			if self.collide(new_x,new_y,lvl):
				self.yvel = 0
				self.jump = False
			else:
				self.pos[1] = new_y	
		else:
			self.yvel	= self.yvel + g*dt
			new_y 		= self.pos[1] + (self.yvel)*dt  #check if we are falling by pushing down a lil
			self.fall = True
			if self.collide(new_x,new_y,lvl):  #not falling
				self.yvel = 0
				self.fall = False
				self.still_fall = False
			else:
				self.still_fall = True
				self.pos[1] = new_y
				self.fall = False
		if self.dir == "right":
			new_x = self.pos[0] + 6
		if self.dir == "left":
			new_x = self.pos[0] - 6
		
		#now finally check if new_x will cause a collision
		if not self.collide(new_x,new_y,lvl):
			self.pos[0] = new_x
		
		#now update masks!
		self.idle_points,self.idle_poly = mask(self,8,30,54,0)
		self.walk_points,self.walk_poly = mask(self,7,29,54,0)
		self.jump_points,self.jump_poly = mask(self,0,38,54,0)
		
		#now draw nash in new pos, with correct image for state
		if self.dir == "right":
			if not self.jump: #otherwise do jumping pic
				if self.walk_timer == 0:
					self.walk = False
				if self.walk == False or self.yvel != 0: #also capture no walking in air!
					screen.blit(self.pic_right_idle,self.pos)
					self.walk = True
					if self.stand_count == 4:
						self.walk_timer = 5
						self.stand_count = 0
					else:
						self.stand_count += 1
				else:
					screen.blit(self.pic_right_walk,self.pos)
					self.walk_timer -= 1
			else:
				screen.blit(self.jump_pic_right,self.pos)

		if self.dir == "left":
			if not self.jump:
				if self.walk_timer == 0:
					self.walk = False
	
				if self.walk == False or self.yvel != 0:
					screen.blit(self.pic_left_idle,self.pos)
					self.walk = True
					if self.stand_count == 4:
						self.walk_timer = 5
						self.stand_count = 0
					else:
						self.stand_count += 1
				else:
					screen.blit(self.pic_left_walk,self.pos)
					self.walk_timer -= 1
			else:
				screen.blit(self.jump_pic_left,self.pos)

		if self.dir == "idle":
			self.walk = False
			self.walk_timer = 4
			if self.old_dir == "left":
				if self.yvel != 0 and self.jump:
					screen.blit(self.jump_pic_left,self.pos)
				else:
					screen.blit(self.pic_left_idle,self.pos)
			if self.old_dir == "right":
				if self.yvel != 0 and self.jump:
					screen.blit(self.jump_pic_right,self.pos)
				else:
					screen.blit(self.pic_right_idle,self.pos)
		if self.dir != "idle":
			self.old_dir = self.dir

	def collide(self,new_x,new_y,lvl):
		old_x = self.pos[0]   #save old position
		old_y = self.pos[1]	
		for block in lvl.blocks:
			#save old pos, check with masks updated for new one
			if self.jump: 
				self.pos[1] = new_y
				self.jump_points,self.jump_poly = mask(self,0,38,54,0)
				if self.jump_poly.intersects(block.poly) or not self.outside(lvl,self.jump_poly):  #outside_check covers level collisions
					self.pos[1] = old_y
					self.jump_points,self.jump_poly = mask(self,0,38,54,0)
					return True
			else:
				self.pos[0] = new_x
				if self.fall:
					self.pos[1] = new_y
				self.idle_points,self.idle_poly = mask(self,8,30,54,0)	
				self.walk_points,self.walk_poly = mask(self,7,29,54,0)
				if self.dir == "idle":
					if self.idle_poly.intersects(block.poly)or not self.outside(lvl,self.idle_poly):
						if self.fall:
							self.pos[1] = old_y
						self.pos[0] = old_x
						self.idle_points,self.idle_poly = mask(self,8,30,54,0)
						self.walk_points,self.walk_poly = mask(self,7,29,54,0)
						return True
				if self.dir == "right" or self.dir == "left":
					if self.walk_poly.intersects(block.poly) or not self.outside(lvl,self.walk_poly):
						if self.fall:
							self.pos[1] = old_y
						self.pos[0] = old_x
						self.idle_points,self.idle_poly = mask(self,8,30,54,0)
						self.walk_points,self.walk_poly = mask(self,7,29,54,0)
						return True
		#fallback for no collisions
		return False

	def outside(self,lvl,nash_poly):
		rel = lvl.poly.relate(nash_poly)
		return rel[0] == '2' and rel[6] == 'F' #if at least one point is in inside and nothing outside


# Set the width and height of the screen [width, height]
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)	 
pygame.display.set_caption("NASH")
# Loop until the user clicks the close button.
done = False 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
intro_trigger = True
IT_talk_trigger = False
flickr_count = 0
#music
pygame.mixer.music.load('BeepBox-Song.wav')
#pygame.mixer.music.play(-1)
call = pygame.image.load("pics/call.png").convert_alpha() #IT image
call = pygame.transform.scale(call, [WIDTH,HEIGHT+30])
#add a nash and generate levels
nash	= Nash(10,300)
title	= Title_lvl(WIDTH,HEIGHT,screen)
lvl1	= Level1(WIDTH+5,HEIGHT,screen)   #+5 on width to prevent sticking on walls
lvl2	= Level2(WIDTH+5,HEIGHT,screen)
levels	= [lvl1,lvl2]
curr_lvl = None
r_count = 0  #keep track of what was pressed last
l_count = 0
pause = False
#some things to blit to screen
pause_text = Titlefont.render("PAUSED",True,RED)
it_1 = Midfont.render("Hey, this is Tom from IT.",True, BLACK)
it_2 = Midfont.render("We need to check your laptop.",True, BLACK)
it_3 = Midfont.render("Nash - I mean ASAP",True, BLACK)
nash_ansr1 = Midfont.render("Uhhhh ....",True, BLACK)
nash_ansr2 = Midfont.render("fine.",True,BLACK)
nash_ansr3 = Midfont.render("Just give me five minutes.",True,BLACK)

# -------- Main Program Loop -----------
while not done:
	t_0 = time.time()
	# --- Main event loop --> runs every time, getting event that's happened?
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
			break
		keys = pygame.key.get_pressed()
		if event.type == pygame.KEYDOWN:
			if intro_trigger == True and event.key == pygame.K_RETURN:
				intro_trigger = False
				IT_talk_trigger = True
				IT_countr = 0 
			if keys[pygame.K_i] and nash.jump == False:
				if nash.still_fall == False:
					nash.yvel = -36 #scale of jump height
					nash.jump = True
				else:
					nash.jump = False
			if event.key == pygame.K_p:
				if pause == False:
					pause = True
				elif pause == True:
					pause = False

		if keys[pygame.K_l]:	#continually search for depression of right/left
			nash.dir = "right"
			r_count = r_count + 1
		if keys[pygame.K_j]:
			nash.dir = "left"
			l_count = l_count + 1
		if keys[pygame.K_l] and keys[pygame.K_j]:
			if r_count < l_count:
				nash.dir = "right"
			if l_count < r_count:
				nash.dir = "left"
			else:
				nash.dir = "right"

		if event.type == pygame.KEYUP:
			if not keys[pygame.K_j]:
				l_count = 0
			if not keys[pygame.K_l]:
				r_count = 0
			if r_count == 0 and l_count == 0:
				nash.dir = "idle"
				nash.walk = False

	# Pause page (check first!)
	if pause:
		screen.fill(WHITE)
		screen.blit(pause_text,[(WIDTH/2)-100,HEIGHT/2])
	else:
	    # Intro Page ---> Runs if no ENTER key events have happened
		if intro_trigger and not IT_talk_trigger:
			title.title_draw(screen)
		#Secondary intro page  ---> runs after enter key, before lvls
		if IT_talk_trigger:
			screen.fill(WHITE)
			screen.blit(call, [0,0])
			IT_countr += 1
			#draw the IT stuff and text
			if IT_countr >= 20:
				screen.blit(it_1, [220, 40])
			if IT_countr >= 50:
				screen.blit(it_2, [220, 60])
			if IT_countr >= 70:
				screen.blit(it_3, [230, 80])
			if IT_countr >= 100:
				screen.blit(nash_ansr1, [330,460])
			if IT_countr >= 130:
				screen.blit(nash_ansr2, [410,460])
			if IT_countr >= 160:
				screen.blit(nash_ansr3, [330,480])
			if IT_countr >= 5:  #195
				IT_talk_trigger = False

		# Regular gameplay --> if not on an intro screen!
		if not intro_trigger and not IT_talk_trigger:
			for lvl in levels:
				if lvl.over == False:
					curr_lvl = lvl
					break
			screen.fill(WHITE) # for now, clean it off so we can redraw 
			
			# draw level before nash is drawn
			curr_lvl.draw(screen,convert_time(300-overall_time))

			# update nash's position
			nash.update_pos(screen,curr_lvl) #this finds new pos of nash based on inputs, and draws him
			
			# trigger events for the level
			#nash.pos[0], nash.pos[1],nash.jump,nash.yvel,banjo_found,jerry = curr_lvl.events(screen,nash,keys) #handle events -> item collisions, level "over"
			nash, banjo_found, jerry, sub = curr_lvl.events(screen,nash,keys)

			if curr_lvl.over and curr_lvl.name != "lvl5":
				#move nash to start postion of next level on level finish (before next level actually starts)
				nash.pos[0] = levels[(levels.index(curr_lvl) + 1)].start[0]
				nash.pos[1] = levels[(levels.index(curr_lvl) + 1)].start[1]

			# update enemies (only tim for right now)
			for entity in curr_lvl.entities:
				if entity.type == "Tim":
					entity.update()
	
	# --- update the screen with what we've drawn.
	pygame.display.flip()
	
	# --- Limit to 60 frames per second
	clock.tick(60)
	t_1 = time.time()
	if not intro_trigger and not IT_talk_trigger and not pause:
			overall_time = overall_time + (t_1-t_0)
			if banjo_found:
				overall_time = overall_time - 5
			if jerry:
				overall_time = overall_time + 20
			if sub:
				overall_time = overall_time + 60
	
	#---- check if you've run out of time
	if overall_time >= 300 and not intro_trigger and not IT_talk_trigger:   #if you lose
		print("nash.timer: ", nash.timer)
		print("GAME OVER")
		done = True

# Close the window and quit.
# ---> here put lost end screen (if you ran out of time)
pygame.quit()