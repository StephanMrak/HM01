import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

verticies = (
    ( 1, -1, -1), # 0
    ( 1,  1, -1), # 1
    (-1,  1, -1), # 2
    (-1, -1, -1), # 3
    ( 1, -1,  1), # 4
    ( 1,  1,  1), # 5
    (-1, -1,  1), # 6
    (-1,  1,  1), # 7
    )



surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6),
    )

normals = [
    ( 0,  0, -1),  # surface 0
    (-1,  0,  0),  # surface 1
    ( 0,  0,  1),  # surface 2
    ( 1,  0,  0),  # surface 3
    ( 0,  1,  0),  # surface 4
    ( 0, -1,  0)   # surface 5
]

colors = (
    (1,1,1),
    (0,1,0),
    (0,0,1),
    (0,1,0),
    (0,0,1),
    (1,0,1),
    (0,1,0),
    (1,0,1),
    (0,1,0),
    (0,0,1),
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7),
    )




def Cube(logo_texture):


    logo_data = pygame.image.tostring(logo_texture, "RGBA", 1)
    logo_width, logo_height = logo_texture.get_size()
    logo_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, logo_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, logo_width, logo_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, logo_data)

    glBegin(GL_QUADS)
    for i_surface, surface in enumerate(surfaces):
        x = 0
        glNormal3fv(normals[i_surface])

        #for vertex, tex_coord in zip(surface,[(0, 0), (1, 0), (1, 1), (0, 1)]):
        for vertex, tex_coord in zip(surface, [(0, 0), (0, 1), (1, 1), (1, 0)]):
            glTexCoord2f(*tex_coord)
            glVertex3fv(verticies[vertex])
    glEnd()

    #glColor3fv(colors[0])
   # glBegin(GL_LINES)
   # for edge in edges:
   #     for vertex in edge:
   #         glVertex3fv(verticies[vertex])
   # glEnd()

def draw_text(text, x, y):
    font = pygame.font.Font(None, 40)
    text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2f(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def check_click(cube_pos, cube_size):
    viewport = glGetIntegerv(GL_VIEWPORT)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)

    # get the mouse position
    mouse_pos = pygame.mouse.get_pos()

    # convert the mouse position to normalized device coordinates
    mouse_pos_ndc = [
        2.0 * mouse_pos[0] / viewport[2] - 1.0,
        1.0 - 2.0 * mouse_pos[1] / viewport[3],
        0.0,
    ]
    #print(mouse_pos_ndc)
    # convert the mouse position from NDC to world coordinates
    viewport = glGetIntegerv(GL_VIEWPORT)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)

    mouse_pos_world= gluUnProject(mouse_pos_ndc[0], mouse_pos_ndc[1], mouse_pos_ndc[2], modelview, projection, viewport)
    print(mouse_pos_world)


    # check if the mouse position is inside the cube
    x, y, z = mouse_pos_world
    cx, cy, cz = cube_pos
    sx, sy, sz = cube_size
    if (cx - sx/2) < x < (cx + sx/2) and \
       (cy - sy/2) < y < (cy + sy/2) and \
       (cz - sz/2) < z < (cz + sz/2):
        print("Cube clicked!")
        return True
    else:
        return False

def main():
    global surfaces
    cube_pos=(0,0,0)
    cube_size=(10,10,10)
    logo_texture = pygame.image.load("logo_rotate.jpg")
    pygame.init()
    display = (1366,768)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    clock = pygame.time.Clock()

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0, 0, -7)

    #glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 1, 0)) # directional light from the front
    glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 20, 0)) # point light from the left, top, front
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))


    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    rotate=0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if pygame.mouse.get_pressed()[0]:
            check_click(cube_pos, cube_size)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
        glPushMatrix()
        glRotatef(rotate, 1, 1, 1)
        Cube(logo_texture)
        glPopMatrix()
        rotate+=0.5
        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
        draw_text("So geht es los: ", -4.5, -1.5)
        draw_text("Verbinden Sie sich mit dem WLAN 'HM01'  ", -4.5, -1.875)
        draw_text("Geben Sie in Ihrem Webbrowser folgendes als URL ein: 192.168.1.1:8081  ", -4.5, -2.25)

        pygame.display.flip()
        clock.tick(30)

main()