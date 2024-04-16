from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import random
import math
import hmsysteme

def main():
    RED =       (255,   0,   0)
    size = hmsysteme.get_size()
    # initialize Pygame
    pygame.init()
    #screen=pygame.display.set_mode((0, 0), DOUBLEBUF | OPENGL, pygame.FULLSCREEN)
    screen=pygame.display.set_mode(size,DOUBLEBUF | OPENGL,pygame.NOFRAME)


    pygame.display.set_caption("my game")
    pygame.mouse.set_visible(False)

    # set up the initial camera position
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (size[0]/size[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -30)

    # enable depth testing
    glEnable(GL_DEPTH_TEST)
    # enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glLightfv(GL_LIGHT0, GL_POSITION, [5, 1.0, 1.0, 0.0])  # light position
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # diffuse color
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])  # specular color
    clock=pygame.time.Clock()



    class Ball:
        def __init__(self, position, radius):
            # enable color tracking
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            # set up the sphere
            self.quad = gluNewQuadric()
            #gluQuadricNormals(self.quad, GLU_SMOOTH)
            #gluQuadricTexture(self.quad, GL_TRUE)

            #setup position and radius
            self.position=position
            self.radius=radius

            # set up the rotation parameters
            self.rot_x = 0
            self.rot_y = 0
            self.rot_z = 0
            self.color=random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
            self.exist=True





        def draw(self):

            #glRotatef(self.rot_x, 1, 0, 0)
            #glRotatef(self.rot_y, 0, 1, 0)
            #glRotatef(self.rot_z, 0, 0, 1)
            if self.exist:
                #glMatrixMode(GL_MODELVIEW)
                #glLoadIdentity()

                glPushMatrix()
                glTranslatef(self.position[0], self.position[1], self.position[2])

                # draw the sphere
                glColor3f(self.color[0], self.color[1], self.color[2])
                gluSphere(self.quad, self.radius, 5, 5)
                glPopMatrix()



            # update the rotation parameter
            #self.rot_x += 1
            #self.rot_y += 1
            #self.rot_z += 1

        def print_pygame_coordinates(self):
            self.model_view = glGetDoublev(GL_MODELVIEW_MATRIX)
            self.projection = glGetDoublev(GL_PROJECTION_MATRIX)
            self.viewport = glGetIntegerv(GL_VIEWPORT)

            # Use gluUnProject to convert 3D object coordinates to screen coordinates
            self.win_x, self.win_y, self.win_z = gluProject(self.position[0], self.position[1], self.position[2], self.model_view, self.projection,
                                               self.viewport)

            # Pygame coordinates are flipped vertically
            self.pygame_y = int(self.viewport[3] - self.win_y)
            #print(win_x, pygame_y)
            return self.win_x, self.pygame_y

        def change_color(self):
            self.color=(0,0,0)
            self.exist=False



    # set the light properties
    ball_list=[]
    num=5
    for i in range(-num,num):
        for j in range(-num,num):
            for z in range(-num, num):
                ball_list.append(Ball((i,j,z),0.5))
    #ball_list.append(Ball((8,0,0),0.5))
    #ball_list.append(Ball((-8,0,0),0.5))
    #ball_list.append(Ball((1,0,0),0.5))
    # main loop


    def remove_clicked_ball(balls):
        balls.remove(ball)

    while hmsysteme.game_isactive():


        # clear the screen and set the background color to black
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glMatrixMode(GL_PROJECTION)

        glRotatef(1, 1, 1, 1)

        for ball in ball_list:
            ball.draw()
            #ball.print_pygame_coordinates()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for ball in ball_list:
                    coords=ball.print_pygame_coordinates()
                    dist=math.sqrt((coords[0]-pos[0])**2+(coords[1]-pos[1])**2)
                    #print(dist)
                    if dist<40:
                        print("hit")
                        ball.change_color()

        if hmsysteme.hit_detected():
            pos = hmsysteme.get_pos()
            for ball in ball_list:
                coords=ball.print_pygame_coordinates()
                dist=math.sqrt((coords[0]-pos[0])**2+(coords[1]-pos[1])**2)
                #print(dist)
                if dist<40:
                    print("hit")
                    ball.change_color()



        # update the display
        pygame.display.flip()

        # limit the frame rate
        clock.tick(60)
        print(clock.get_fps())

    pygame.display.quit()
    pygame.quit()

if __name__ == '__main__':

	main()
