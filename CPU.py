import pygame

from pygame import key
from random import randint

#################CONSTANTS#######################
TIMER = pygame.USEREVENT + 1

MAX_MEMORY = 4096

KEY_MAPPINGS = {

	0x1: pygame.K_4,
	0x2: pygame.K_5,
	0x3: pygame.K_6,
	0xC: pygame.K_7,
	0x4: pygame.K_r,
	0x5: pygame.K_t,
	0x6: pygame.K_y,
	0xD: pygame.K_u,
	0x7: pygame.K_f,
	0x8: pygame.K_g,
	0x9: pygame.K_h,
	0xE: pygame.K_j,
	0xA: pygame.K_v,
	0x0: pygame.K_b,
	0xB: pygame.K_n,
	0xF: pygame.K_m
}

fonts = [ 
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

FONT_START_ADDRESS = 0x0


PROGRAM_COUNTER_START = 0x200

#################CLASSES#################

class CPU(object):

	def __init__(self, screen):
		self.sound_timer = 0
		self.delay_timer = 0
		self.V = [0]*16
		self.I = 0
		self.sp = 0
		self.stack = [0]
		self.pc = 0x200
		self.memory = [0]*4096
		self.screen = screen
		self.reset()
		self.running = True
		self.operand = 0
		self.keyboard = [False]*16

		for i in range(len(fonts)):
			self.memory[i] = fonts[i]

	def execute_instruction(self,operand=None):
		
		##pass operand in for testing purposes
		if operand:
			self.operand = operand
		else:
			self.operand = self.memory[self.pc]
			self.operand = self.operand << 8
			self.operand += self.memory[self.pc + 1]
			self.pc += 2

		operation = (self.operand & 0xF000) >> 12

		print(hex(self.operand))
		##check for one of the hex chars that have repeats
		if operation == 0x0:
			last_nib = (self.operand & 0x000F)
			if last_nib == 0x0:
				self.screen.clear_screen()
			if last_nib == 0xE:
				self.return_from_subroutine()

		if operation == 0x1:
			self.jump_to_location()

		if operation == 0x2:
			self.call_subroutine()

		if operation == 0x3:
			self.skip_next_instruction_reg_eq_val()

		if operation == 0x4:
			self.skip_next_instruction_reg_not_val()

		if operation == 0x5:
			self.skip_next_instruction_reg_eq_reg()

		if operation == 0x6:
			self.set_reg_to_val()

		if operation == 0x7:
			self.add_val_to_reg()

		if operation == 0x8:
			last_nib = (self.operand & 0x000F)
			if last_nib == 0x0:
				self.reg_eq_reg()
			elif last_nib == 0x1:
				self.bitwise_or_reg()
			elif last_nib == 0x2:
				self.bitwise_and_reg()
			elif last_nib == 0x3:
				self.bitwise_xor_reg()
			elif last_nib == 0x4:
				self.add_reg_to_reg()
			elif last_nib == 0x5:
				self.sub_reg_from_reg()
			elif last_nib == 0x6:
				self.shift_right()
			elif last_nib == 0x7:
				self.sub_regx_from_regy()
			elif last_nib == 0xE:
				self.shift_left()

		if operation == 0x9:
			self.skip_next_instruction_reg_not_reg()

		if operation == 0xA:
			self.set_index_val()

		if operation == 0xB:
			self.jump_to_offset()

		if operation == 0xC:
			self.reg_eq_rand()

		if operation == 0xD:
			self.draw_sprite()

		if operation == 0xE:
			last_nib = (self.operand & 0x000F)

			if last_nib == 0x1:
				self.skip_next_instruction_key_not_press()
			elif last_nib == 0xE:
				self.skip_next_instruction_key_press()

		if operation == 0xF:
			last_two = (self.operand & 0x00FF)
			if last_two == 0x07:
				self.set_reg_delay_timer()
			elif last_two == 0x0A:
				self.wait_key_press()
			elif last_two == 0x15:
				self.set_delay_timer_reg()
			elif last_two == 0x18:
				self.set_sound_timer_reg()
			elif last_two == 0x1E:
				self.add_reg_to_index()
			elif last_two == 0x29:
				self.set_index_sprite_location()
			elif last_two == 0x33:
				self.store_bcd()
			elif last_two == 0x55:
				self.store_regs_index()
			elif last_two == 0x65:
				self.read_index_to_reg()

		return self.operand

	#00EE
	def return_from_subroutine(self):
		self.pc = self.stack.pop()
		self.sp -= 1

	#1nnn
	def jump_to_location(self):
		self.pc = (self.operand & 0x0FFF)


	#2nnn
	def call_subroutine(self):
		self.sp +=1
		self.stack.append(self.pc)
		self.pc = (self.operand & 0x0FFF)

	#3xkk
	def skip_next_instruction_reg_eq_val(self):
		x_reg = (self.operand & 0x0F00) >> 8
		my_const = (self.operand & 0x00FF)
		if self.V[x_reg] == my_const:
			self.pc += 2

	#4xkk
	def skip_next_instruction_reg_not_val(self):
		x_reg = (self.operand & 0x0F00) >> 8
		if self.V[x_reg] != (self.operand & 0x00FF):
			self.pc +=2

	#5xy0
	def skip_next_instruction_reg_eq_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		if self.V[x_reg] == self.V[y_reg]:
			self.pc +=2

	#6xkk
	def set_reg_to_val(self):
		x_reg = (self.operand & 0x0F00) >> 8
		self.V[x_reg] = (self.operand & 0x00FF)

	#7xkk
	def add_val_to_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		my_const = (self.operand & 0x00FF)
		if self.V[x_reg] + my_const < 256:
			self.V[x_reg] += my_const
		else:
			self.V[x_reg] = (self.V[x_reg] + my_const) - 256
			self.V[0xF] = 1

	#8xy0
	def reg_eq_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		self.V[x_reg] = self.V[y_reg]

	#8xy1
	def bitwise_or_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		self.V[x_reg] |= self.V[y_reg]

	#8xy2
	def bitwise_and_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		self.V[x_reg] &= self.V[y_reg]

	#8xy3
	def bitwise_xor_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		self.V[x_reg] ^= self.V[y_reg]

	#8xy4
	def add_reg_to_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		if self.V[x_reg] + self.V[y_reg] > 255:
			self.V[0xF] = 1
			self.V[x_reg] = (self.V[x_reg] + self.V[y_reg]) - 256
		else:
			self.V[0xF] = 0
			self.V[x_reg] = self.V[x_reg] + self.V[y_reg]

	#8xy5
	def sub_reg_from_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		if self.V[x_reg] > self.V[y_reg]:
			self.V[0xF] = 1
		else:
			self.V[0xF] = 0
		self.V[x_reg] = self.V[x_reg] - self.V[y_reg]

	#8xy6
	def shift_right(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		least_bit = (self.V[x_reg] & 0x1)
		self.V[0xF] = least_bit
		self.V[x_reg] /= 2

	#8xy7
	def sub_regx_from_regy(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		if self.V[y_reg] > self.V[x_reg]:
			self.V[0xF] = 1
		else:
			self.V[0xF] = 0
		self.V[x_reg] = self.V[y_reg] - self.V[x_reg]

	#8xyE
	def shift_left(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		most_bit = (self.V[x_reg] & 0x80) >> 7
		self.V[0xF] = most_bit
		self.V[x_reg] *= 2

	#9xy0
	def skip_next_instruction_reg_not_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		if self.V[x_reg] != self.V[y_reg]:
			self.pc += 2

	#Annn
	def set_index_val(self):
		self.I = (self.operand & 0x0FFF)

	#Bnnn
	def jump_to_offset(self):
		self.pc = ((self.operand & 0x0FFF) + self.V[0x0])  

	#Cxkk
	def reg_eq_rand(self):
		x_reg = (self.operand & 0x0F00) >> 8
		my_const = (self.operand & 0x00FF)
		self.V[x_reg] = (my_const & randint(0, 255))

	#Dxyn
	def draw_sprite(self):
		x_reg = (self.operand & 0x0F00) >> 8
		y_reg = (self.operand & 0x00F0) >> 4
		n = (self.operand & 0x000F)
		screen_start_index = ((self.V[y_reg]*64)+self.V[x_reg])
		x_pos = (self.V[x_reg] % 64)
		y_pos = (self.V[y_reg] % 32)
		self.V[0xF] = 0
		#Compare first row of sprite with current screen
		for row in range(0,n):
			spriteByte = self.memory[self.I + row]
			y_coord = y_pos + row
			y_coord %= 32
			for col in range(0,8):
				x_coord = x_pos + col
				x_coord %= 64
				current_color = self.screen.get_pixel(x_coord, y_coord)
				color = ((spriteByte & (0x80 >> col)) >> (7-col))
				#print(color, current_color)
				if current_color == 1 and color == 1:
					self.V[0xF] = 1
					color ^= current_color 
				elif current_color == 0 and color == 1:
					color ^= current_color 
					self.V[0xF] = 0

				
				#print(x_reg, y_reg)
				self.screen.draw_pixel(x_coord,y_coord,color)

		self.screen.update()


				#screenPixel = self.screen.display[screen_start_index + col + row*64]
				


	#Ex9E
	def skip_next_instruction_key_press(self):
		check_key = (self.operand & 0x0F00) >> 8
		key_down = key.get_pressed()
		if key_down[KEY_MAPPINGS[check_key]]:
			print(KEY_MAPPINGS[check_key])
		# if self.keyboard[check_key]:
			self.pc += 2

	#ExA1
	def skip_next_instruction_key_not_press(self):
		check_key = (self.operand & 0x0F00) >> 8
		key_down = key.get_pressed()
		if not key_down[KEY_MAPPINGS[check_key]]:
		# if self.keyboard[check_key]:
			self.pc += 2

	#Fx07
	def set_reg_delay_timer(self):
		x_reg = (self.operand & 0x0F00) >> 8
		self.V[x_reg] = self.delay_timer

	#Fx0A
	def wait_key_press(self):
		x_reg = (self.operand & 0x0F00) >> 8
		key_pressed = False
		while not key_pressed:
			event = pygame.event.wait()
			if event.type == pygame.KEYDOWN:
				key_down = key.get_pressed()
				for key_hex, key_char in KEY_MAPPINGS.items():
					if key_down[key_char]:
						self.V[x_reg] = key_hex
						key_pressed = True
						break

		# key_pressed = False
		# while not key_pressed:
		# 	for i in range(len(self.keyboard)):
		# 		if self.keyboard[i]:
		# 			self.V[x_reg] = i
		# 			print(self.keyboard[i])
		# 			key_pressed = True
		# 			break
					




	#Fx15
	def set_delay_timer_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		self.delay_timer = self.V[x_reg]

	#Fx18
	def set_sound_timer_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		self.sound_timer = self.V[x_reg]


	#Fx1E
	def add_reg_to_index(self):
		x_reg = (self.operand & 0x0F00) >> 8
		self.I += self.V[x_reg]

	#Fx29
	def set_index_sprite_location(self):
		x_reg = (self.operand & 0x0F00) >> 8
		sprite_digit = self.V[x_reg]
		self.I = FONT_START_ADDRESS + (5 * sprite_digit)

	#Fx33
	def store_bcd(self):
		x_reg = (self.operand & 0x0F00) >> 8
		number = self.V[x_reg]
		self.memory[self.I + 2] = number % 10
		number = number // 10
		self.memory[self.I + 1] = number % 10
		number = number //10
		self.memory[self.I] = number % 10

	#Fx55
	def store_regs_index(self):
		x_reg = (self.operand & 0x0F00) >> 8
		for reg in range(0,x_reg+1):
			self.memory[self.I + reg] = self.V[reg]

	#Fx65
	def read_index_to_reg(self):
		x_reg = (self.operand & 0x0F00) >> 8
		for reg in range(0,x_reg+1):
			self.V[reg] = self.memory[self.I + reg]

	def reset(self):
		self.V = [0] * 16
		self.I = 0
		self.pc = 0x200
		self.sp = 0
		self.delay_timer = 0
		self.sound_timer = 0

	def load_rom(self, filename, location=0x200):
		rom = open(filename, "rb").read()
		for index, val in enumerate(rom):
			self.memory[0x200 + index] = val

	def decrement_timers(self):
		if self.delay_timer != 0:
			self.delay_timer -= 1 
		if self.sound_timer != 0:
			self.sound_timer -= 1

	def handle_keys(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				key_down = key.get_pressed()
				if key_down[pygame.K_ESCAPE]:
					self.running = False
				for key_hex, key_char in KEY_MAPPINGS.items():
					if key_down[key_char]:
						self.keyboard[key_hex] = True
			elif event.type == pygame.KEYUP:
				key_down = key.get_pressed()
				for key_hex, key_char in KEY_MAPPINGS.items():
					if not key_down[key_char]:
						self.keyboard[key_hex] = False
			elif event.type == TIMER:
				self.decrement_timers()
			elif event.type == pygame.QUIT:
				self.running = False

		print(self.keyboard)




	
	



		

		
































