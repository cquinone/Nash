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

def convert_time(time):
	mins = str(int(time/60))
	if len(mins) == 1:
		mins = "0"+mins
	secs = 60*(time/60 - int(time/60))
	secs = str(int(secs))
	if len(secs) == 1:
		secs = "0"+secs
	converted = str(mins)+":"+str(secs)
	return converted

def mask(Nash,xmin,xmax,ymax):
	top_right	= np.array([Nash.pos[0]+xmax,Nash.pos[1]+ymax]) 
	top_left	= np.array([Nash.pos[0]+xmin,Nash.pos[1]+ymax])			
	btm_right	= np.array([Nash.pos[0]+xmax,Nash.pos[1]])		#ymin is assumed to always be 0
	btm_left	= np.array([Nash.pos[0]+xmin,Nash.pos[1]])
	top_right.shape	= (2,1) 
	top_left.shape	= (2,1)
	btm_right.shape	= (2,1)
	btm_left.shape	= (2,1)
	points = [top_left,top_right,btm_right,btm_left]
	poly   = Polygon(points)
	return points, poly

class Scene:
	def __init__(self,width,height):
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

class Title_lvl(Scene):
	def __init__(self,width,height,screen):
		super().__init__(width,height)
		self.blocks = []
		self.over	= False
		self.name = "title"

	def draw(self,screen):
		screen.fill(WHITE)
		nash_intro	= pygame.image.load("pics/nash_final.png").convert_alpha()
		nash_intro	= pygame.transform.scale(nash_intro, [int(1.4*int(300*1.14)),int(1.4*int(250*1.2))])
		screen.blit(nash_intro, [165,100])
		if self.timer < 20:
			start = Startfont.render("[Hit Enter to Play]",True, BLACK) 
			screen.blit(start,[285,535])
			self.timer = self.timer + 1
		else:
			self.timer = self.timer + 1
			if self.timer > 30: #basically saying: dont draw for ten frames, makes flickr effect
				self.timer = 0
		title = Titlefont.render("- FIVE MINUTES -",True, BLACK)
		screen.blit(title, [160, 20])
		authors = Smallfont.render("(Created by Chris Quinones and Co.)", True, BLACK)
		screen.blit(authors, [275,70])

class Level1(Scene):
	def __init__(self,width,height,screen):
		super().__init__(width,height)
		self.blocks = [Block(0,400),Block(50,400), Block(100,400), Block(150,400), Block(265,375),Block(160,580),
						Block(420,340),Block(602,315),Block(652,315),Block(702,315),Block(752,315),Block(110,580),
						Block(60,580),Block(10,580),Block(-40,580)]
		self.end = False
		self.name = "lvl1"

	def draw(self,screen,nash_time):
		screen.fill(WHITE)
		for block in self.blocks:
			screen.blit(block.pic,block.pos)
		time = Titlefont.render(nash_time,True,RED) #convert time puts it in mins:secs
		screen.blit(time, [0,0])

class Level2(Scene):
	def __init__(self,width,height,screen):
		super().__init__(width,height)
		self.blocks = [Block(100,HEIGHT-40),Block(200,HEIGHT-60), Block(200,HEIGHT-80)]
		self.end = False
		self.name = "lvl2"

	def draw(self,screen):
		screen.fill(RED)
		for block in self.blocks:
			screen.blit(block.pic,block.pos)

class Block():
	def __init__(self,x,y):
		self.pos = [x,y]
		self.width 	= 50
		self.height = 20
		self.pic = pygame.image.load("pics/block.png").convert()
		self.pic.set_colorkey(WHITE)
		self.points,self.poly = mask(self,0,50,20) 

class Player():
	def __init__(self):
		self.timer = 0

class Nash(Player):
	def __init__(self,x,y):
		super().__init__()
		self.pos = [x, y]
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
			if self.collide(new_x,new_y,self.fall,lvl):
				self.yvel = 0
				self.jump = False
			else:
				self.pos[1] = new_y	
		else:
			self.yvel	= self.yvel + g*dt
			new_y 		= self.pos[1] + (self.yvel)*dt #check if we are falling by pushing down a lil
			self.fall = True
			if self.collide(new_x,new_y,self.fall,lvl): #not falling
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
		if not self.collide(new_x,new_y,self.fall,lvl):
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

	def collide(self,new_x,new_y,fall,lvl):
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
		return rel[0] == '2' and rel[6] == 'F' #if at least one point is in inside and nothing outside?

def main():
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
	#pygame.mixer.music.load('BeepBox-Song.wav')
	#pygame.mixer.music.play(-1)
	call = pygame.image.load("pics/call.png").convert_alpha() #it image
	call = pygame.transform.scale(call, [WIDTH,HEIGHT+30])
	#add a nash and generate levels
	nash	= Nash(10,100)
	title	= Title_lvl(WIDTH,HEIGHT,screen)
	lvl1	= Level1(WIDTH,HEIGHT,screen)
	lvl2	= Level2(WIDTH,HEIGHT,screen)
	levels	= [lvl1,lvl2]
	r_count = 0  #keep track of what was pressed last
	l_count = 0
	overall_time = 0
	#some things to print later
	it_1 = Midfont.render("Hey, this is Tom from IT.",True, BLACK)
	it_2 = Midfont.render("We to check your laptop.",True, BLACK)
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
						nash.yvel = -30 #this will force update to a jump?
						nash.jump = True
					else:
						nash.jump = False

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
			if keys[pygame.K_r]:
				print("R PRESSED")
				nash.pos = [10,100]  #reset
			if event.type == pygame.KEYUP:
				if not keys[pygame.K_LEFT]:
					l_count = 0
				if not keys[pygame.K_RIGHT]:
					r_count = 0
				if r_count == 0 and l_count == 0:
					nash.dir = "idle"
					nash.walk = False

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

		# Regular gameplay --> if not on intro screen!
		if not intro_trigger and not IT_talk_trigger:
			for lvl in levels:
				if lvl.end == False:
					curr_lvl = lvl
					break
			screen.fill(WHITE) # for now, clean it off so we can redraw --> will need to start event manager? 
			curr_lvl.draw(screen,convert_time(300-overall_time))  # (before nash!)
			nash.update_pos(screen,curr_lvl) #this finds new pos of nash based on inputs, and draws him
		# --- update the screen with what we've drawn.
		pygame.display.flip()
		# --- Limit to 60 frames per second
		clock.tick(60)
		t_1 = time.time()
		if not intro_trigger and not IT_talk_trigger:
			overall_time = overall_time + t_1-t_0
		#---- check if you've run out of time
		if overall_time >= 300 and not intro_trigger and not IT_talk_trigger:   #if you lose
			print("overall_count, nash.timer: ", overall_count, nash.timer)
			print("GAME OVER")
			break
	# Close the window and quit.
	# ---> here put lost end screen (if you ran out of time)
	pygame.quit()
 
if __name__ == "__main__":
	main()
	#pygame.draw.polygon(screen, BLACK,[[self.idle_points[0][0],self.idle_points[0][1]],[self.idle_points[1][0],self.idle_points[1][1]],[self.idle_points[2][0],self.idle_points[2][1]],[self.idle_points[3][0],self.idle_points[3][1]]], 2)