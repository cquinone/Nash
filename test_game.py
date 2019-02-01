import pygame,os
import pygame.font
from pygame.locals import *
from stack_queue import Stack



pygame.init()
# Set the width and height of the screen [width, height]
size = (700,500)
screen = pygame.display.set_mode(size)	 
pygame.display.set_caption("Test")
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
r_count = 0
l_count = 0 #keep track of direction keys
r_bool = False
l_bool = False
count = 0
dir = "idle"
# -------- Main Program Loop -----------
while not done:
	# --- Main event loop --> runs every time, getting event that's happened?
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
			break;
		#if event.type == pygame.KEYDOWN:
		keys = pygame.key.get_pressed() 
		if keys[pygame.K_UP]:
			print("JUMP")
		if keys[pygame.K_RIGHT]:
			print("right is pressed")
			dir = "right"
			r_count = r_count + 1
		if keys[pygame.K_LEFT]:
			print("left is pressed")
			dir = "left"
			l_count = l_count + 1
		if keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]:
			if r_count < l_count:
				dir = "right"
			if l_count < r_count:
				dir = "left"
			else:
				dir = "right"

		if event.type == pygame.KEYUP:
			if not keys[pygame.K_LEFT]:
				l_count = 0
			if not keys[pygame.K_RIGHT]:
				r_count = 0
			if r_count == 0 and l_count == 0:
				dir = "idle"
	print("curr dir: ", dir)
	print(count)
	count = count + 1
	clock.tick(60)

pygame.quit()
#a = Stack()