def main():  
	import pymunk               # Import pymunk..
	import pygame
	import random
	import time
	import math
	import time
	import hmsysteme
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
	if not names:
		names = "dummy"
	points = []
	for i in range(0, len(names)):
		points.append(0)
	curr_player = 0
	shooting_objects=[]
	static_bodys=[]
	

	pygame.init()
	screen=pygame.display.set_mode(size, pygame.NOFRAME)
	pygame.display.set_caption("my game")
	pygame.mouse.set_visible(False)
	clock = pygame.time.Clock()

	space = pymunk.Space()      # Create a Space which contain the simulation
	space.gravity = 0,981      # Set its gravity

	
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
			#self.shape=pymunk.Circle(self.body,self.radius)
			self.vertices=[(0,0),(50,0),(50,50),(0,50)]
			#self.vertices2 = [[10, 10], [20, 10], [20, 15], [10, 15]]
			#print(self.vertices2)
			self.shape = pymunk.Poly(self.body, self.vertices)
			self.shape.mass=1
			self.shape.elasticity = 0.5
			self.shape.friction = 10
			self.blast=False
			self.blast_counter=0



			self.rscale=1
			space.add(self.body,self.shape)
			self.color=WHITE
			
		def f(self):
			#self.pos_x=int(self.body.position.x)
			#self.pos_y=int(self.body.position.y)


			self.verts = []
			for v in self.shape.get_vertices():
				x = v.rotated(self.shape.body.angle)[0] + self.shape.body.position[0]
				y = v.rotated(self.shape.body.angle)[1] + self.shape.body.position[1]
				self.verts.append((x, y))
			pygame.draw.polygon(screen, [255, 255, 255], self.verts)
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


			#print(self.shape.body.local_to_world(self.shape.center_of_gravity))


			#pygame.draw.polygon(screen, self.color,self.vertices2)
			#pygame.draw.circle(screen,self.color,(self.pos_x,self.pos_y),self.radius)


			
		def hit(self, pos):
			self.radius=25
			self.a=self.shape.body.local_to_world(self.shape.center_of_gravity)
			self.pos_x=self.a[0]
			self.pos_y=self.a[1]
			if ((pos[0] - self.pos_x) ** 2 + (pos[1] - self.pos_y) ** 2) <= self.radius ** 2:
			#if (pos[0]>self.shape.body.position[0] and pos[0]<self.shape.body.position[0]+self.vertices[1][0]):
			#	if (pos[1]>self.shape.body.position[1] and pos[1]<self.shape.body.position[1]+self.vertices[3][1]):
				self.body2 = pymunk.Body(1, 100, body_type=pymunk.Body.STATIC)
				self.blast=True
				self.body2.position =self.a
				self.shape2 = pymunk.Circle(self.body2, 1000)
				self.shape2.mass = 50
				space.add(self.body2, self.shape2)

				self.color = (155,155,155)
				self.destruct = True
				last_hit[0] = 100
				points[curr_player] += last_hit[0]
				font = pygame.font.SysFont(pygame.font.get_fonts()[0], 28)
				text = font.render(str("letzter Treffer : " + str(int(last_hit[0]))), True, BLUE)
				screen.blit(text, (150 - text.get_width() // 2, 240 - text.get_height() // 2))
				self.body.position = size[0]*2,size[1]*2
				del font
				return True
			else:
				return False







	for num in range(0,50):
		shooting_objects.append(shooting_body())
		#static_bodys.append(create_static_body(space))
	
	for num in range(0,3):
		static_bodys.append(rigid_body())

	verticies=[(0,size[1]),(size[0],size[1]),(size[0],size[1]-20),(0,size[1]-20)]
	static_bodys[0].set_verticies(verticies)
	verticies=[(0,0),(0,size[1]-20),(20,size[1]-20),(20,0)]
	static_bodys[1].set_verticies(verticies)
	verticies=[(size[0],size[1]-20),(size[0],0),(size[0]-20,0),(size[0]-20,size[1]-20)]
	static_bodys[2].set_verticies(verticies)

	

	while hmsysteme.game_isactive():
		screen.fill(BLACK)
		font = pygame.font.SysFont(pygame.font.get_fonts()[0], 28)
		pygame.draw.circle(screen, BLUE, [50, 300 + (40 * (curr_player + 1))], 10, 10)
		for i in range(0, len(names)):
			text = font.render(str(names[i] + " " + str(int(points[i]))), True, BLUE)
			screen.blit(text, (200 - text.get_width() // 2, 300 + (40 * (i + 1)) - text.get_height() // 2))
		del font 	
		for i in range(0,len(shooting_objects)):	
			shooting_objects[i].f()
		for i in range(0,len(static_bodys)):
			static_bodys[i].f()

		space.step(1/60)
		if hmsysteme.hit_detected():
			pos = hmsysteme.get_pos()

			for i in range(0, len(arrey)):	
				if arrey[i].hit(pos):
					if curr_player == len(names)-1:
						curr_player = 0
					else:
						curr_player += 1

					hmsysteme.put_rgbcolor(arrey[i].color)
			pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
			hmsysteme.take_screenshot(screen)

		for event in pygame.event.get():            
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = event.pos
				for i in range(0, len(shooting_objects)):
					if shooting_objects[i].hit(pos):
						if curr_player == len(names)-1:
							curr_player = 0
						else:
							curr_player += 1


						#hmsysteme.put_rgbcolor(arrey[i].color)
				pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
				hmsysteme.take_screenshot(screen)
                

		pygame.display.flip()
		# print(clock.get_fps())
		clock.tick(60)

	pygame.display.quit()
	pygame.quit()
    
    
if __name__ == '__main__':
	main()




	


