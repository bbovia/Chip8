import pygame

from CPU import CPU, TIMER
from screen import chip8Screen

########################## CONSTANTS ########################## 
# TIMER = pygame.USEREVENT + 1

########################## FUNCTIONS ########################## 

def main(args):
	screen = chip8Screen()
	screen.init_display()
	cpu = CPU(screen)
	cpu.load_rom(args)
	pygame.time.set_timer(TIMER, 15)
	clock = pygame.time.Clock()



	while cpu.running:
		clock.tick(300)
		cpu.execute_instruction()
		#cpu.handle_keys()

		for event in pygame.event.get():
			if event.type == TIMER: 
				cpu.decrement_timers()
			if event.type == pygame.QUIT:
				cpu.running = False
			if event.type == pygame.KEYDOWN:
				keys_pressed = pygame.key.get_pressed()
				if keys_pressed[pygame.K_ESCAPE]:
					cpu.running = False

main("Breakout [Carmelo Cortez, 1979].ch8")












