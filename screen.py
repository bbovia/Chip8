from pygame import display, HWSURFACE, DOUBLEBUF, Color, draw

########################## CONSTANTS ########################## 
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 320
PIXEL_COLORS = {
	0: Color(0,0,0),
	1: Color(255,255,255)
}




########################## CLASSES ########################## 
class chip8Screen(object):
	def __init__(self,height=SCREEN_HEIGHT, width=SCREEN_WIDTH):
		self.height = height
		self.width = width
		self.surface = None

	def init_display(self):
		display.init()
		self.surface = display.set_mode((self.width, self.height))
		display.set_caption("Chip8 Emulator")
		self.clear_screen()
		self.update()

	def draw_pixel(self,x_pos,y_pos,pixel_color):
		draw.rect(self.surface, PIXEL_COLORS[pixel_color], (x_pos*10,y_pos*10,10,10))

	def get_pixel(self,x_pos,y_pos):
		x_scale = (x_pos*10)  
		y_scale = (y_pos*10) 
		pixel_color = self.surface.get_at((x_scale,y_scale))
		if pixel_color == PIXEL_COLORS[0]:
			color = 0
		else:
			color = 1
		return color

	def clear_screen(self):
		self.surface.fill(PIXEL_COLORS[0])

	def update(self):
		display.flip()

	def destroy(self):
		display.quit()














