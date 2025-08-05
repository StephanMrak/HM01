def startscreen(processname, backgroundqueue,debug_flag):
    import pygame
    import pygame.locals
    import hmsysteme
    import OpenGL.GL
    import OpenGL.GLU
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




    def Cube(logo_data, logo_width, logo_height, logo_id):



        OpenGL.GL.glBindTexture(OpenGL.GL.GL_TEXTURE_2D, logo_id)
        OpenGL.GL.glTexParameteri(OpenGL.GL.GL_TEXTURE_2D, OpenGL.GL.GL_TEXTURE_MIN_FILTER,OpenGL.GL.GL_LINEAR)
        OpenGL.GL.glTexParameteri(OpenGL.GL.GL_TEXTURE_2D, OpenGL.GL.GL_TEXTURE_MAG_FILTER, OpenGL.GL.GL_LINEAR)
        OpenGL.GL.glTexImage2D(OpenGL.GL.GL_TEXTURE_2D, 0, OpenGL.GL.GL_RGBA, logo_width, logo_height, 0, OpenGL.GL.GL_RGBA, OpenGL.GL.GL_UNSIGNED_BYTE, logo_data)
        OpenGL.GL.glBegin(OpenGL.GL.GL_QUADS)

        for i_surface, surface in enumerate(surfaces):
            OpenGL.GL.glNormal3fv(normals[i_surface])

            #for vertex, tex_coord in zip(surface,[(0, 0), (1, 0), (1, 1), (0, 1)]):
            for vertex, tex_coord in zip(surface, [(0, 0), (0, 1), (1, 1), (1, 0)]):
                OpenGL.GL.glTexCoord2f(*tex_coord)
                OpenGL.GL.glVertex3fv(verticies[vertex])
        OpenGL.GL.glEnd()



    def draw_text(text, x, y, color=(255, 255, 255), size=40):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color, (0, 0, 0))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        OpenGL.GL.glRasterPos2f(x, y)
        OpenGL.GL.glDrawPixels(text_surface.get_width(), text_surface.get_height(), OpenGL.GL.GL_RGBA, OpenGL.GL.GL_UNSIGNED_BYTE, text_data)


    logo_texture = pygame.image.load("logo_rotate.jpg")
    pygame.init()

    size = hmsysteme.get_size()
    if debug_flag:
        pygame.display.set_mode(size, pygame.locals.DOUBLEBUF|pygame.locals.OPENGL)
    else:
        pygame.display.set_mode((0, 0), pygame.locals.DOUBLEBUF | pygame.locals.OPENGL | pygame.FULLSCREEN)


    clock = pygame.time.Clock()

    OpenGL.GL.glMatrixMode(OpenGL.GL.GL_PROJECTION)
    OpenGL.GLU.gluPerspective(45, (size[0]/size[1]), 0.1, 50.0)

    OpenGL.GL.glMatrixMode(OpenGL.GL.GL_MODELVIEW)
    OpenGL.GL.glTranslatef(0, 0, -7)

    #glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 1, 0)) # directional light from the front
    OpenGL.GL.glLight(OpenGL.GL.GL_LIGHT0, OpenGL.GL.GL_POSITION,  (0, 0, 20, 0)) # point light from the left, top, front
    OpenGL.GL.glLightfv(OpenGL.GL.GL_LIGHT0, OpenGL.GL.GL_AMBIENT, (0, 0, 0, 1))
    OpenGL.GL.glLightfv(OpenGL.GL.GL_LIGHT0, OpenGL.GL.GL_DIFFUSE, (1, 1, 1, 1))


    OpenGL.GL.glEnable(OpenGL.GL.GL_DEPTH_TEST)
    OpenGL.GL.glEnable(OpenGL.GL.GL_TEXTURE_2D)
    rotate=0
    logo_data = pygame.image.tostring(logo_texture, "RGBA", 1)
    logo_width, logo_height = logo_texture.get_size()
    logo_id = OpenGL.GL.glGenTextures(1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


        OpenGL.GL.glClear(OpenGL.GL.GL_COLOR_BUFFER_BIT|OpenGL.GL.GL_DEPTH_BUFFER_BIT)

        OpenGL.GL.glEnable(OpenGL.GL.GL_LIGHTING)
        OpenGL.GL.glEnable(OpenGL.GL.GL_LIGHT0)
        OpenGL.GL.glEnable(OpenGL.GL.GL_COLOR_MATERIAL)
        OpenGL.GL.glColorMaterial(OpenGL.GL.GL_FRONT_AND_BACK, OpenGL.GL.GL_AMBIENT_AND_DIFFUSE )
        OpenGL.GL.glPushMatrix()
        OpenGL.GL.glRotatef(rotate, 1, 1, 1)
        Cube(logo_data, logo_width,logo_height,logo_id)
        OpenGL.GL.glPopMatrix()
        rotate+=0.5
        OpenGL.GL.glDisable(OpenGL.GL.GL_LIGHT0)
        OpenGL.GL.glDisable(OpenGL.GL.GL_LIGHTING)
        OpenGL.GL.glDisable(OpenGL.GL.GL_COLOR_MATERIAL)
        draw_text("So geht es los: ", -4.5, -1.5)
        draw_text("Verbinden Sie sich mit dem WLAN 'HM01'  ", -4.5, -1.875)
        draw_text("Geben Sie in Ihrem Webbrowser folgendes als URL ein: 192.168.1.1:8081  ", -4.5, -2.25)


        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    startscreen(None,None,True)
