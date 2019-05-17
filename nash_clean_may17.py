import pygame,os
import pygame.font
from pygame.locals import *
from shapely.geometry import Polygon,Point
import numpy as np
from matplotlib import pyplot as plt
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


def mask(nash,xmin,xmax,ymax):
	#make a polygon that defines collision mask for object
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
	yvel = nash.yvel
	jump = nash.jump
	banjo = False
	
	#preprocess entities and throw in projectiles
	for entity in lvl.entities:
		if entity.projectiles:
			print("Has some")

	for entity in lvl.entities:
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
				jump = False
				yvel = 0
				return lvl.start[0],lvl.start[1], jump,yvel,banjo
			
			elif entity.type == "Ladder":
				if keys[pygame.K_UP]:
					#send nash up the ladder
					yvel = -20
					jump = True
			
			elif entity.type == "Banjo":
				collide_text = Midfont.render("Banjo found! +5 seconds!", True, BLACK)
				screen.blit(collide_text, [nash.pos[0], nash.pos[1]-20])
				pygame.display.flip()
				pygame.time.wait(1080)
				lvl.entities.remove(entity)
				banjo = True

			#elif entity.type == "Tim":
				# nash gets reset, Tim stays though? -> maybe deleted

			#elif entity.type == "Puff":
				# puff gets deleted, nash gets reset

	return nash.pos[0],nash.pos[1], jump, yvel, banjo


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


class Title_lvl(Scene):
	def __init__(self,width,height,screen):
		super().__init__(width,height)
		self.blocks = []
		self.name = "title"

	def draw(self,screen):
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
			if self.timer > 30: #basically saying: dont draw for ten frames, makes flicker effect
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
		#-----ENEMY/ITEM PLACEMENT-----------------------------------------------------------------------------------------------#
		self.entities = [FBI(561,535.8,"left"),FBI(272,535.8,"right"),Banjo(412,550),Ladder(765,529),Ladder(765,478),Ladder(765,427),
		                 Ladder(765,376),Ladder(765,325)]
		self.pic = pygame.image.load("pics/background1.png").convert_alpha()
		self.pic = pygame.transform.scale(self.pic, [800,600])
		self.finish = [702,260]
		self.start = [10,300]
		self.name = "lvl1"

	def events(self,screen,nash,keys):
		lvl_stats = {"over": False,
		             "banjo": False}
		#first check if end of level reached
		if abs(nash.pos[0] - self.finish[0]) <= 4 and abs(nash.pos[1] - self.finish[1]) <= 4:
			self.over = True
			#print level end message
			lvl_over_text1 = Midfont.render("Kris Kristofferson's music",True, BLACK)
			lvl_over_text2 = Midfont.render("is not a legitimate excuse",True,BLACK)
			screen.blit(lvl_over_text1, [nash.pos[0]-250,nash.pos[1]-50])
			screen.blit(lvl_over_text2, [nash.pos[0]-250,nash.pos[1]-30])
			pygame.display.flip()
			pygame.time.wait(1320)
			return nash.pos[0],nash.pos[1], nash.jump, nash.yvel, lvl_stats
			#check for special objects collisions (keys = keyboard state)
		nash.pos[0],nash.pos[1],nash.jump,nash.yvel, banjo = entity_collide(screen,nash,keys,self)
		lvl_stats["over"] = self.over
		lvl_stats["banjo"] = banjo
		return nash.pos[0],nash.pos[1],nash.jump,nash.yvel,lvl_stats

	def draw(self,screen,nash_time):
		screen.fill(WHITE)
		#screen.blit(self.pic, [0,0])
		for block in self.blocks:
			screen.blit(block.pic,block.pos)
		for entity in self.entities:
			screen.blit(entity.pic,entity.pos)
		time = Titlefont.render(nash_time,True,RED) #convert time puts it in mins:secs
		screen.blit(time, [0,0])


class Level2(Scene):
	def __init__(self,width,height,screen):
		super().__init__(width,height)
		#-----LEVEL CONSTRUCTION-------------------------------------------------------------------------------------------------#
		self.blocks = [Block(100,HEIGHT-40),Block(200,HEIGHT-60)]
		#-----ENEMY/ITEM PLACEMENT-----------------------------------------------------------------------------------------------#
		self.entities = []
		self.finish = [11,101]
		self.start = [10,100]
		self.name = "lvl2"

	def draw(self,screen,nash_time):
		screen.fill(WHITE)
		for block in self.blocks:
			screen.blit(block.pic,block.pos)
		for entity in self.entities:
			screen.blit(entity.pic,entity.pos)
		time = Titlefont.render(nash_time,True,RED) #convert time puts it in mins:secs
		screen.blit(time, [0,0])

	def events(self,screen,nash,keys):
		lvl_stats = {"over": False,
		             "banjo": False}
		if abs(nash.pos[0] - self.finish[0]) <= 4 and abs(nash.pos[1] - self.finish[1]) <= 4:
			self.over = True
			#print level end message
			lvl_over_text = Midfont.render("TIM GET OUTTA MY HOUSE",True, BLACK)
			screen.blit(lvl_over_text, [nash.pos[0]-250,nash.pos[1]-50])
			pygame.display.flip()
			pygame.time.wait(1120)
			return nash.pos[0],nash.pos[1], nash.jump, nash.yvel, lvl_stats
		
		nash.pos[0],nash.pos[1],nash.jump,nash.yvel, banjo = entity_collide(screen,nash,keys,self)
		return nash.pos[0],nash.pos[1],nash.jump,nash.yvel, lvl_stats


class Item():
	def __init__(self,x,y,w,h,image):
		self.pos = [x,y]
		self.width  = w 
		self.height = h
		self.pic = pygame.image.load(image).convert_alpha()
		self.projectiles = [] #auto-gen for all entities, only filled for projectile users


class Block(Item):
	def __init__(self,x,y):
		super().__init__(x,y,50,20,"pics/block.png")
		self.pic.set_colorkey(WHITE)
		self.points,self.poly = mask(self,0,46,20)
 

class FBI(Item):
	def __init__(self,x,y,direction):
		super().__init__(x,y,30,34,"pics/FBI.png")
		self.pic = pygame.transform.scale(self.pic, [int(1.2*self.width),int(1.3*self.height)])
		self.direction = direction
		if direction == "right":
			self.pic = pygame.transform.flip(self.pic,True,False)
		self.points,self.poly = mask(self,0,1.15*self.width,1.25*self.height) #mask/img go to roughly 36,44
		self.type = "FBI"


class Ladder(Item):
	def __init__(self,x,y):
		super().__init__(x,y,30,51,"pics/ladder.png")
		self.pic = pygame.transform.scale(self.pic, [int(self.width),int(self.height)]) 
		self.points,self.poly = mask(self,0,.85*self.width,self.height)  #mask is thinner to prevent climbing side rails
		self.type = "Ladder"


class Banjo(Item):
	def __init__(self,x,y):
		super().__init__(x,y,54.3,16,"pics/banjo.png")
		self.pic = pygame.transform.scale(self.pic, [int(self.width),int(self.height)])
		self.pic = pygame.transform.rotate(self.pic,0)
		self.points,self.poly = mask(self,0,self.width,self.height) 
		self.type = "Banjo"


class Extra_Credit():
	def __init__(self,x,y):
		self.pos = [x,y]


class Tim(Item):
	def __init__(self,x,y):
		super().__init__(x,y,30,34,"pics/FBI.png")
		self.start = x
		self.end = x + 5


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
		
		self.idle_points,self.idle_poly = mask(self,8,30,54)   #make vectors/poly for idle mask polygon, for now leave as square
		self.walk_points,self.walk_poly = mask(self,7,29,54)   #5-19 is nash image (24x34 canvas), mult by 1.6 -> 8x30
		self.jump_points,self.jump_poly = mask(self,0,38,54)
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
			new_y 		= self.pos[1] + (self.yvel)*dt #check if we are falling by pushing down a lil
			self.fall = True
			if self.collide(new_x,new_y,lvl): #not falling
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
		self.idle_points,self.idle_poly = mask(self,8,30,54)
		self.walk_points,self.walk_poly = mask(self,7,29,54)
		self.jump_points,self.jump_poly = mask(self,0,38,54)
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
				self.jump_points,self.jump_poly = mask(self,0,38,54)
				if self.jump_poly.intersects(block.poly) or not self.outside(lvl,self.jump_poly):  #outside_check covers level collisions
					self.pos[1] = old_y
					self.jump_points,self.jump_poly = mask(self,0,38,54)
					return True
			else:
				self.pos[0] = new_x
				if self.fall:
					self.pos[1] = new_y
				self.idle_points,self.idle_poly = mask(self,8,30,54)	
				self.walk_points,self.walk_poly = mask(self,7,29,54)
				if self.dir == "idle":
					if self.idle_poly.intersects(block.poly)or not self.outside(lvl,self.idle_poly):
						if self.fall:
							self.pos[1] = old_y
						self.pos[0] = old_x
						self.idle_points,self.idle_poly = mask(self,8,30,54)
						self.walk_points,self.walk_poly = mask(self,7,29,54)
						return True
				if self.dir == "right" or self.dir == "left":
					if self.walk_poly.intersects(block.poly) or not self.outside(lvl,self.walk_poly):
						if self.fall:
							self.pos[1] = old_y
						self.pos[0] = old_x
						self.idle_points,self.idle_poly = mask(self,8,30,54)
						self.walk_points,self.walk_poly = mask(self,7,29,54)
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
			if keys[pygame.K_UP] and nash.jump == False:
				if nash.still_fall == False:
					nash.yvel = -35 #scale of jump height
					nash.jump = True
				else:
					nash.jump = False
			if event.key == pygame.K_p:
				if pause == False:
					pause = True
				elif pause == True:
					pause = False

		if keys[pygame.K_RIGHT]:	#continually search for depression of right/left
			nash.dir = "right"
			r_count = r_count + 1
		if keys[pygame.K_LEFT]:
			nash.dir = "left"
			l_count = l_count + 1
		if keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]:
			if r_count < l_count:
				nash.dir = "right"
			if l_count < r_count:
				nash.dir = "left"
			else:
				nash.dir = "right"
		if keys[pygame.K_r]: #reset nash pos for debugging
			nash.pos = [10,100]

		if event.type == pygame.KEYUP:
			if not keys[pygame.K_LEFT]:
				l_count = 0
			if not keys[pygame.K_RIGHT]:
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
			title.draw(screen)
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
			if IT_countr >= 195:
				IT_talk_trigger = False

		# Regular gameplay --> if not on an intro screen!
		if not intro_trigger and not IT_talk_trigger:
			for lvl in levels:
				if lvl.over == False:
					curr_lvl = lvl
					break
			screen.fill(WHITE) # for now, clean it off so we can redraw 

			# update enemies before drawing (only tim for right now)
			for entity in curr_lvl.entities:
				if isinstance(entity, Tim):
					print(entity.pos)
					#entity.update()
					# update puff positions for this tim --> in pff update, deal with too many / pos?
					# first puff / adding more puffs / dealing / moving
					# all contained within tim update
					# updates position, projectiles, etc.
			
			# draw level before nash is drawn
			curr_lvl.draw(screen,convert_time(300-overall_time))
			
			# update nash's position
			nash.update_pos(screen,curr_lvl) #this finds new pos of nash based on inputs, and draws him
			
			# trigger events for the level
			nash.pos[0], nash.pos[1],nash.jump,nash.yvel,lvl_stats = curr_lvl.events(screen,nash,keys) #handle events -> item collisions, level "over"
			if lvl_stats["over"] and curr_lvl.name != "lvl5":
				#move nash to start postion of next level on level finish (before next level actually starts)
				nash.pos[0] = levels[(levels.index(curr_lvl) + 1)].start[0]
				nash.pos[1] = levels[(levels.index(curr_lvl) + 1)].start[1]
	
	# --- update the screen with what we've drawn.
	pygame.display.flip()
	
	# --- Limit to 60 frames per second
	clock.tick(60)
	t_1 = time.time()
	if not intro_trigger and not IT_talk_trigger and not pause:
			overall_time = overall_time + (t_1-t_0)
			if lvl_stats["banjo"]:
				overall_time = overall_time - 5
	
	#---- check if you've run out of time
	if overall_time >= 300 and not intro_trigger and not IT_talk_trigger:   #if you lose
		print("nash.timer: ", nash.timer)
		print("GAME OVER")
		break

# Close the window and quit.
# ---> here put lost end screen (if you ran out of time)
pygame.quit()