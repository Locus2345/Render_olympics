import numpy as np
import pygame as pg
import pygame.gfxdraw as gfx

from pygame.locals import *
from tracefuncs import *

if __name__ == '__main__':
    iteration = 0

    res = (360, 360)
    rpp = 48

    scene1 = [np.array([20, 20, 20]), [Sphere(1, np.array([3, -1, 0]), np.array([255, 0, 0]), 424, 0),
                                       Sphere(1, np.array([4, 0, 2]), np.array([0, 255, 0]), 258, 0),
                                       Sphere(1, np.array([4, 0, -2]), np.array([0, 0, 255]), 8, 0),
                                       Sphere(5000, np.array([0, -5001, 0]), np.array([200, 200, 0]), 1024, 0)],
              [],
              [Light("directional", 0.2, np.array([1, -1, 1])),
               Light("ambient", 0.2),
               Light("positional", 0.6, np.array([2, 1, 0]))]]
    '''Torus(0.5, 2, np.array([1, 0, 0]), np.array([9, -.5, 2]), np.array([30, 140, 200]), 10)'''
    scene2 = [np.array([120, 180, 250]), [Sphere(1, np.array([6, 1.1, -1.5]), np.array([55, 104, 183]), 500, 0),
                                          Sphere(1.2, np.array([7, 0.8, -0.7]), np.array([200, 200, 30]), 500, 0),
                                          Sphere(1.3, np.array([8, 1.6, 0]), np.array([40, 40, 50]), 5, 0),
                                          Sphere(1.5, np.array([9.5, 1.25, 1]), np.array([40, 200, 40]), 20, 0),
                                          Sphere(1.8, np.array([11, 2.25, 1.7]), np.array([230, 45, 20]), 1000, 0),
                                          Sphere(4000, np.array([30, -4001, 0]), np.array([200, 200, 200]), 20, 0)],
              [],[
              Light("directional", 0.45, np.array([1, 0.5, 0.8])),
              Light("ambient", 0.25),
              Light("positional", 0.3, np.array([1, 5, 0]))]]
    if iteration == 0:
        focusdist, camera_pos, rotZ, rotY, focus = 1, np.array([0, 0, 0]), 0, 0, 80

    framebuffer = render(scene2, 1, camera_pos, rpp, rotZ, rotY, focus, res, 1)

    FPS = pg.time.Clock()
    display = pg.display.set_mode(res)
    displayloop = True

    while displayloop:
        for event in pg.event.get():
            if event.type == QUIT:
                displayloop = False
        pg.display.flip()
        for x in range(res[0]):
            for y in range(res[1]):
                gfx.pixel(display, x, y, framebuffer[x, y])
        FPS.tick(30)
