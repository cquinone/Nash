import pygame,os
import pygame.font
from pygame.locals import *
from shapely.geometry import Polygon,Point
import numpy as np
from matplotlib import pyplot as plt
import copy

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
 
# Constants
WIDTH = 700
HEIGHT = 500
dt = 1/float(4)
g = 9.8

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

class Level1():
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
		self.blocks = [Block(100,HEIGHT-40),Block(200,HEIGHT-60), Block(200,HEIGHT-100)]

	def draw(self,screen):
		for block in self.blocks:
			screen.blit(block.pic,block.pos)
			pygame.draw.polygon(screen, RED,[[block.points[0][0],block.points[0][1]],[block.points[1][0],block.points[1][1]],[block.points[2][0],block.points[2][1]],[block.points[3][0],block.points[3][1]]], 2)

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
	def __init__(self):
		super().__init__()
		self.pos = [250, 250]
		self.width  = 38 #1.6 multiplied by 24x34 (the actual size of nash image, not canvas)
		self.height = 54
		self.name		= "Nash"
		self.pic_right_idle 	= pygame.image.load("pics/nash_side_back.png").convert()
		self.pic_right_idle.set_colorkey(WHITE)
		self.pic_right_idle 	= pygame.transform.scale(self.pic_right_idle, [self.width,self.height])
		self.pic_left_idle		= pygame.transform.flip(self.pic_right_idle,True,False)

		self.pic_right_walk 	= pygame.image.load("pics/nash_walk_arms.png").convert()
		self.pic_right_walk.set_colorkey(WHITE)
		self.pic_right_walk 	= pygame.transform.scale(self.pic_right_walk, [self.width,self.height])
		self.pic_left_walk		= pygame.transform.flip(self.pic_right_walk,True,False)
		
		self.jump_pic_right		= pygame.image.load("pics/nash_jump_right.png").convert()
		self.jump_pic_right.set_colorkey(WHITE)
		self.jump_pic_right 	= pygame.transform.scale(self.jump_pic_right, [self.width,self.height])
		self.jump_pic_left	 	= pygame.transform.flip(self.jump_pic_right, True,False)
		
		self.idle_points,self.idle_poly = mask(self,8,30,54)   #make vectors/poly for idle mask polygon, for now leave as square
		self.walk_points,self.walk_poly = mask(self,7,29,54)   #5-19 is nash image (24x34 canvas), mult by 1.6 -> 8x30
		self.jump_points,self.jump_poly = mask(self,0,38,54)
		self.yvel = 0									  	   
		self.old_dir = "right"
		self.dir = "idle"
		self.fall = False
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
			else:
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
					pygame.draw.polygon(screen, BLACK,[[self.idle_points[0][0],self.idle_points[0][1]],[self.idle_points[1][0],self.idle_points[1][1]],[self.idle_points[2][0],self.idle_points[2][1]],[self.idle_points[3][0],self.idle_points[3][1]]], 2)
					self.walk = True
					if self.stand_count == 4:
						self.walk_timer = 5
						self.stand_count = 0
					else:
						self.stand_count += 1
				else:
					screen.blit(self.pic_right_walk,self.pos)
					pygame.draw.polygon(screen, BLACK,[[self.walk_points[0][0],self.walk_points[0][1]],[self.walk_points[1][0],self.walk_points[1][1]],[self.walk_points[2][0],self.walk_points[2][1]],[self.walk_points[3][0],self.walk_points[3][1]]], 2)
					self.walk_timer -= 1
			else:
				screen.blit(self.jump_pic_right,self.pos)
				pygame.draw.polygon(screen, BLACK,[[self.jump_points[0][0],self.jump_points[0][1]],[self.jump_points[1][0],self.jump_points[1][1]],[self.jump_points[2][0],self.jump_points[2][1]],[self.jump_points[3][0],self.jump_points[3][1]]], 2)

		if self.dir == "left":
			if not self.jump:
				if self.walk_timer == 0:
					self.walk = False
	
				if self.walk == False or self.yvel != 0:
					screen.blit(self.pic_left_idle,self.pos)
					pygame.draw.polygon(screen, BLACK,[[self.idle_points[0][0],self.idle_points[0][1]],[self.idle_points[1][0],self.idle_points[1][1]],[self.idle_points[2][0],self.idle_points[2][1]],[self.idle_points[3][0],self.idle_points[3][1]]], 2)
					self.walk = True
					if self.stand_count == 4:
						self.walk_timer = 5
						self.stand_count = 0
					else:
						self.stand_count += 1
				else:
					screen.blit(self.pic_left_walk,self.pos)
					pygame.draw.polygon(screen, BLACK,[[self.walk_points[0][0],self.walk_points[0][1]],[self.walk_points[1][0],self.walk_points[1][1]],[self.walk_points[2][0],self.walk_points[2][1]],[self.walk_points[3][0],self.walk_points[3][1]]], 2)
					self.walk_timer -= 1
			else:
				screen.blit(self.jump_pic_left,self.pos)
				pygame.draw.polygon(screen, BLACK,[[self.jump_points[0][0],self.jump_points[0][1]],[self.jump_points[1][0],self.jump_points[1][1]],[self.jump_points[2][0],self.jump_points[2][1]],[self.jump_points[3][0],self.jump_points[3][1]]], 2)

		if self.dir == "idle":
			self.walk = False
			self.walk_timer = 4
			if self.old_dir == "left":
				if self.yvel != 0 and self.jump:
					screen.blit(self.jump_pic_left,self.pos)
					pygame.draw.polygon(screen, BLACK,[[self.jump_points[0][0],self.jump_points[0][1]],[self.jump_points[1][0],self.jump_points[1][1]],[self.jump_points[2][0],self.jump_points[2][1]],[self.jump_points[3][0],self.jump_points[3][1]]], 2)
				else:
					screen.blit(self.pic_left_idle,self.pos)
					pygame.draw.polygon(screen, BLACK,[[self.idle_points[0][0],self.idle_points[0][1]],[self.idle_points[1][0],self.idle_points[1][1]],[self.idle_points[2][0],self.idle_points[2][1]],[self.idle_points[3][0],self.idle_points[3][1]]], 2)
			if self.old_dir == "right":
				if self.yvel != 0 and self.jump:
					screen.blit(self.jump_pic_right,self.pos)
					pygame.draw.polygon(screen, BLACK,[[self.jump_points[0][0],self.jump_points[0][1]],[self.jump_points[1][0],self.jump_points[1][1]],[self.jump_points[2][0],self.jump_points[2][1]],[self.jump_points[3][0],self.jump_points[3][1]]], 2)
				else:
					screen.blit(self.pic_right_idle,self.pos)
					pygame.draw.polygon(screen, BLACK,[[self.idle_points[0][0],self.idle_points[0][1]],[self.idle_points[1][0],self.idle_points[1][1]],[self.idle_points[2][0],self.idle_points[2][1]],[self.idle_points[3][0],self.idle_points[3][1]]], 2)
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
	pygame.init()
	# Set the width and height of the screen [width, height]
	size = (WIDTH, HEIGHT)
	screen = pygame.display.set_mode(size)	 
	pygame.display.set_caption("NASH")
	# Loop until the user clicks the close button.
	done = False 
	# Used to manage how fast the screen updates
	clock = pygame.time.Clock()
	# Intro_Trigger is true until the player hits play
	intro_trigger = True
	IT_talk_trigger = False
	#choose_character = False
	flickr_count = 0
	pygame.font.init()
	#fonts
	Startfont = pygame.font.Font(os.path.join(os.sep,"Users", "chrisquinones", "work","prog","pyproj","games","nash","silkscreen",'slkscr.tff'), 22)
	Titlefont =  pygame.font.Font(os.path.join(os.sep,"Users", "chrisquinones", "work","prog","pyproj","games","nash","silkscreen",'slkscrb.tff'), 42)
	smallfont = pygame.font.Font(os.path.join(os.sep,"Users", "chrisquinones", "work","prog","pyproj","games","nash","silkscreen",'slkscr.tff'), 12)
	#music
	#pygame.mixer.music.load('BeepBox-Song.wav')
	#pygame.mixer.music.play(-1)
	#load images
	nash_intro = pygame.image.load("pics/nash_final.png").convert()
	call = pygame.image.load("pics/call.png").convert()
	#add some intial objects
	nash = Nash()
	lvl1 = 	Level1(WIDTH,HEIGHT)
	r_count = 0  #keep track of what was pressed last
	l_count = 0
	# -------- Main Program Loop -----------
	while not done:
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
					nash.jump = True
					nash.yvel = -45 #this will force update to a jump?
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

			if event.type == pygame.KEYUP:
				if not keys[pygame.K_LEFT]:
					l_count = 0
				if not keys[pygame.K_RIGHT]:
					r_count = 0
				if r_count == 0 and l_count == 0:
					nash.dir = "idle"
					nash.walk = False
		# Intro Page ---> Runs if no ENTER KEY events have happened?
		if intro_trigger and not IT_talk_trigger:
			screen.fill(WHITE)
			#screen.blit(nash_real, [0,0])
			screen.blit(nash_intro, [125,100])
 
			if flickr_count < 20:
				start = Startfont.render("[Hit Enter to Play]",True, BLACK) 
				screen.blit(start,[70,410])
				flickr_count += 1
			else:
				flickr_count +=1
				if flickr_count > 30: #basically saying: dont draw for ten frames, makes flickr effect
					flickr_count = 0
			title = Titlefont.render("- FIVE MINUTES -",True, BLACK)
			screen.blit(title, [20, 20])
			authors = smallfont.render("(Created by Chris Quinones and Co.)", True, BLACK)
			screen.blit(authors, [135,70])
		
		#Secondary intro page
		if IT_talk_trigger:
			screen.fill(WHITE)
			screen.blit(call, [0,0])
			IT_countr += 1
			if IT_countr >= 2:
				IT_talk_trigger = False

		# Regular gameplay --> if not on intro screen!
		if not intro_trigger and not IT_talk_trigger:
			screen.fill(WHITE) #for now, clean it off so we can redraw --> will need to start event manager?
			#level.draw()  -> will be draw location for current level (before nash!)
			nash.update_pos(screen,lvl1) #this finds new pos of nash based on inputs, and draws him
			lvl1.draw(screen) #draw level now
		# --- Go ahead and update the screen with what we've drawn.
		pygame.display.flip()
		# --- Limit to 60 frames per second
		clock.tick(60)
		nash.timer = nash.timer + 1
	# Close the window and quit.
	pygame.quit()
 
if __name__ == "__main__":
	main()