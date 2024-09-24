def main():  
	import pymunk               # Import pymunk..
	import pygame
	import random
	import time
	import math
	import time
	import hmsysteme
	import os
	import platform
	WHITE = (255, 255, 255)
	BLACK = (0, 0, 0)
	BLUE= (0, 191, 255)
	RED = (255, 0, 0)
	GREEN = (124, 252, 0)
	arrey = []
	anzahl = 10
	last_hit = []
	last_hit.append(0)
	size = hmsysteme.get_size()
	print(size)
	pos = ([0, 0])
	names = hmsysteme.get_playernames()
	hmsysteme.put_button_names(["reset"])

	if not names:
		names = "dummy"
	points = []
	for i in range(0, len(names)):
		points.append(0)
	curr_player = 0
	shooting_objects=[]
	static_bodys=[]
	numofbodies=10


	pygame.init()
	screen=pygame.display.set_mode(size)
	#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	pygame.display.set_caption("my game")
	pygame.mouse.set_visible(False)
	clock = pygame.time.Clock()

	space = pymunk.Space()      # Create a Space which contain the simulation
	space.gravity = 0,981      # Set its gravity

	path = os.path.realpath(__file__)
	print(path)

	if 'Linux' in platform.uname():
		path = path.replace('physics4.py', '')
	else:
		path = path.replace('physics4.py', '')

	# define masks
	Diabolo = pygame.image.load(os.path.join(path, "pics/Schuss.png"))
	Diabolo_Mask = pygame.mask.from_surface(Diabolo)
	Diabolo_Rect = Diabolo.get_rect()
	
	class rigid_body():
		def __init__(self):
			self.body= pymunk.Body(body_type=pymunk.Body.STATIC)
			self.body.position = random.randint(0,size[1]),100      # Set the position of the body
			self.radius=50		
			self.rscale=1
			self.color=(100,100,100)
			self.verticies=0
			
		def set_verticies(self, verticies):
			self.verticies=verticies
			self.shape=pymunk.Poly(space.static_body,self.verticies)
			self.shape.elasticity = 0.0
			self.shape.friction = 10
			space.add(self.body,self.shape)
			

		def f(self):
			self.pos_x=int(self.body.position.x)
			self.pos_y=int(self.body.position.y) 
			
			#pygame.draw.rect(screen,self.color,pygame.Rect(0,size[1]-20,size[0],20))
			pygame.draw.polygon(screen, self.color, self.verticies, 0)
			#pygame.draw.rect(screen,self.color,pygame.Rect(self.verticies[3][0],self.verticies[3][1],self.verticies[1][0]-self.verticies[0][0],self.verticies[1][1]-self.verticies[2][1]))

	class shooting_body():
		def __init__(self):
			self.body= pymunk.Body(1,100, body_type=pymunk.Body.DYNAMIC)
			self.body.position = random.randint(500,1000),random.randint(200,500)      # Set the position of the body
			self.radius=random.randint(40,120)
			self.color=[255, 255, 255]
			self.initposition=0
			self.initheight=0
			self.initwidth=0
			self.destruct=False
			self.dose = pygame.image.load(os.path.join(path, "pics/Dose.jpg"))
			self.mask_dose = pygame.mask.from_surface(self.dose)




			#self.shape=pymunk.Circle(self.body,self.radius)

			
		def f(self):
			#if self.body.kinetic_energy>10000:
			#	self.color=[0,255,0]
			self.verts = []
			self.dose2 = pygame.transform.rotate(self.dose, 90)
			self.mask_dose = pygame.mask.from_surface(self.dose2)
			screen.blit(self.dose2,(self.shape.body.position[0],self.shape.body.position[1]))
			try:
				for v in self.shape.get_vertices():
					x = v.rotated(self.shape.body.angle)[0] + self.shape.body.position[0]
					y = v.rotated(self.shape.body.angle)[1] + self.shape.body.position[1]
					self.verts.append((x, y))
				pygame.draw.polygon(screen, self.color, self.verts)
			except:
				pass

			if self.blast==True:
				#space.remove(self.body2, self.shape2)
				#self.blast=False
				self.blast_counter+=1
				self.pos_x_n=int(self.body2.position.x)
				self.pos_y_n=int(self.body2.position.y)
				#pygame.draw.circle(screen,RED,(self.pos_x_n,self.pos_y_n),1000)
				if self.blast_counter==5:
					space.remove(self.body2, self.shape2)
					self.blast=False

		def reset(self):

			self.body.position = self.initposition
			self.height=self.initheight
			self.width=self.initwidth
			self.body.velocity=(0,0)
			self.body.angular_velocity=(0)
			self.body.angle=0
			if self.destruct==True:
				self.destruct= False



		def set_parameters(self, position, height, width):
			self.body.position = position
			self.height=height
			self.width=width
			self.initposition=position
			self.initheight=height
			self.initwidth=width
			self.vertices=[(0,0),(self.width,0),(self.width,self.height),(0,self.height)]
			#self.vertices2 = [[10, 10], [20, 10], [20, 15], [10, 15]]
			#print(self.vertices2)
			self.shape = pymunk.Poly(self.body, self.vertices)
			self.shape.mass=1
			self.shape.elasticity = 0.5
			self.shape.friction = 0.5
			self.blast=False
			self.blast_counter=0
			self.destruct=False
			self.radius = height

			self.rscale=1
			space.add(self.body,self.shape)
			self.color=WHITE



		def hit(self, pos):


			self.a=self.shape.body.local_to_world(self.shape.center_of_gravity)
			self.pos_x=self.a[0]
			self.pos_y=self.a[1]
			self.offset_Dose = (pos[0] - self.shape.body.position[0], pos[1] - self.shape.body.position[1])
			if self.mask_dose.overlap(Diabolo_Mask, self.offset_Dose):
				print("S")
				return True
			else:
				return False







	height=100
	width=50
	i=0
	numofbodies= int((size[1]-200)/height)
	numofbodies=1
	print(numofbodies)
	factocenterbodies=(size[0]-((numofbodies-1)*width*1.5+width))/2
	for num in range(0,numofbodies):
		for num2 in range(num,numofbodies):
			shooting_objects.append(shooting_body())
			shooting_objects[i].set_parameters(((((width+width/2)*num2)-(width*0.75*num)+factocenterbodies), (size[1]-height-20)-(height*num)), height, width)
			#shooting_objects[i].set_parameters((((int((size[0]) / (numofbodies)) * (num2))) - (width / 1.5 * num) + 200,(size[1] - height) - (int((size[1] - 200) / numofbodies) * num)),height, width)
			i += 1

	
	for num in range(0,1):
		static_bodys.append(rigid_body())

	verticies=[(400,size[1]),(size[0]-400,size[1]),(size[0]-400,size[1]-20),(400,size[1]-20)]
	static_bodys[0].set_verticies(verticies)

	#verticies=[(0,size[1]+100),(size[0],size[1]+100),(size[0],size[1]-20+100),(0,size[1]-20+100)]
	#static_bodys[1].set_verticies(verticies)
	#verticies=[(0,0),(0,size[1]-20),(20,size[1]-20),(20,0)]
	#static_bodys[2].set_verticies(verticies)
	#verticies=[(size[0],size[1]-20),(size[0],0),(size[0]-20,0),(size[0]-20,size[1]-20)]
	#static_bodys[3].set_verticies(verticies)




	

	while hmsysteme.game_isactive():
		#print(os.environ["hm_GameIsActive"])
		screen.fill(BLACK)
		font = pygame.font.SysFont(pygame.font.get_fonts()[0], 28)
		pygame.draw.circle(screen, BLUE, [50, 300 + (40 * (curr_player + 1))], 10, 10)
		for i in range(0, len(names)):
			text = font.render(str(names[i] + " " + str(int(points[i]))), True, BLUE)
			screen.blit(text, (200 - text.get_width() // 2, 300 + (40 * (i + 1)) - text.get_height() // 2))
		del font
		a = hmsysteme.get_action()
		for i in range(0,len(shooting_objects)):	
			shooting_objects[i].f()
			if a==1:
				shooting_objects[i].reset()
		for i in range(0,len(static_bodys)):
			static_bodys[i].f()

		space.step(1/60)
		if hmsysteme.hit_detected():
			pos = hmsysteme.get_pos()
			for i in range(0, len(shooting_objects)):
				if shooting_objects[i].hit(pos):
					if curr_player == len(names) - 1:
						curr_player = 0
					else:
						curr_player += 1

					#hmsysteme.put_rgbcolor(arrey[i].color)
			pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
			hmsysteme.take_screenshot(screen)

		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.display.quit()
				pygame.quit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = event.pos
				for i in range(0, len(shooting_objects)):
					if shooting_objects[i].hit(pos):
						if curr_player == len(names)-1:
							curr_player = 0
						else:
							curr_player += 1


						#hmsysteme.put_rgbcolor(arrey[i].color)
				mausx = event.pos[0]  # pos = pygame.mouse.get_pos() MAUSPOSITION ingame
				mausy = event.pos[1]
				Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)

				#pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
				hmsysteme.take_screenshot(screen)

		if hmsysteme.hit_detected():
			pos = hmsysteme.get_pos()
			for i in range(0, len(shooting_objects)):
				if shooting_objects[i].hit(pos):
					if curr_player == len(names) - 1:
						curr_player = 0
					else:
						curr_player += 1
			pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
			hmsysteme.take_screenshot(screen)

		screen.blit(Diabolo, Diabolo_Rect)
		pygame.display.flip()
		# print(clock.get_fps())
		clock.tick(60)

	pygame.display.quit()
	pygame.quit()


if __name__ == '__main__':
	main()




	


