import contextlib

with contextlib.redirect_stdout(None):
    import pygame as pg
    import pygame.gfxdraw as gfx

from pygame.locals import *
from tracefuncs import *

PURPLE = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def quittest(datas: str):
    datas = datas.strip()
    if datas == "q" or datas == "quit":
        return True
    return False


def yesno(datas: str):
    datas = datas.strip()
    if datas == "":
        return -2
    elif datas.lower() in "yes":
        return 1
    elif datas.lower() in "no":
        return 0
    return -1


if __name__ == '__main__':
    pg.init()
    print(YELLOW + "Welcome to the python rendering olympics! \n\n" + ENDC +
          BLUE + "Where the wrong language is used for graphics!\n\n" + ENDC)
    time.sleep(1)

    iteration = 0
    loop = True
    raw = ""

    focusdist, camera_pos, rotZ, rotY, bounces, trace = 1, np.array([0, 0, 0]), 0, 0, 6, False

    res = (360, 360)
    rpp = 16

    scene = 1

    scene1 = [np.array([10, 10, 10]), [Sphere(500, np.array([30, 1000, 200]), np.array([140, 240, 250]), 100, 1),
                                       Sphere(4000, np.array([30, -4001, 0]), np.array([200, 200, 200]), 20, 0.05),
                                       Sphere(1, np.array([3, -1, 0]), np.array([255, 0, 0]), 424, 0),
                                       Sphere(1, np.array([4, 0, 2]), np.array([0, 255, 0]), 258, 0.02),
                                       Sphere(1, np.array([4, 0, -2]), np.array([0, 0, 255]), 8, 0),
                                       Sphere(5000, np.array([0, -5001, 0]), np.array([200, 200, 0]), 1024, 0.03)],
              [], [Light("directional", 0.45, np.array([1, 0.5, 0.8])),
              Light("ambient", 0.25),
              Light("positional", 0.3, np.array([1, 5, 0]))]]

    scene2 = [np.array([120, 180, 250]), [Sphere(1, np.array([6, 1.1, -1.5]), np.array([55, 104, 183]), 500, 0),
                                          Sphere(1.2, np.array([7, 0.8, -0.8]), np.array([200, 200, 30]), 500, 0),
                                          Sphere(1.3, np.array([8, 1.6, 0]), np.array([40, 40, 50]), 5, 0),
                                          Sphere(1.5, np.array([9.5, 1.25, 1]), np.array([40, 200, 40]), 20, 0),
                                          Sphere(1.7, np.array([11, 2, 2]), np.array([230, 45, 20]), 1000, 0),
                                          Sphere(4000, np.array([30, -4001, 0]), np.array([200, 200, 200]), 20, 0.1),
                                          Sphere(8000, np.array([0, 10000, 0]), np.array([230, 255, 250]), 20, 1)],
              [], [
              Light("directional", 0.45, np.array([1, 0.5, 0.8])),
              Light("ambient", 0.25),
              Light("positional", 0.3, np.array([1, 5, 0]))]]

    scene3 = [np.array([130, 200, 220]), [Sphere(4000, np.array([30, -4001, 0]), np.array([200, 200, 200]), 20, 0),
                                          Sphere(1.5, np.array([6, 0, 2]), np.array([200, 35, 60]), 20, 0),
                                          Sphere(1.5, np.array([6, 0, -2]), np.array([66, 142, 26]), 40, 0),
                                          Sphere(1.5, np.array([-6, 0, 2]), np.array([183, 158, 207]), 80, 0),
                                          Sphere(1.5, np.array([-6, 0, -2]), np.array([210, 237, 235]), 100, 0),
                                          Sphere(1.5, np.array([2, 0, 6]), np.array([14, 135, 177]), 120, 0),
                                          Sphere(1.5, np.array([2, 0, -6]), np.array([16, 43, 32]), 140, 0),
                                          Sphere(1.5, np.array([-2, 0, 6]), np.array([122, 118, 69]), 160, 0),
                                          Sphere(1.5, np.array([-2, 0, -6]), np.array([198, 137, 0]), 180, 0),
                                          Sphere(50, np.array([0, 500, 0]), np.array([225, 197, 63]), 400, 1)],
              [], [Light("directional", 0.45, np.array([1, 0.5, 0.8])),
                   Light("ambient", 0.25),
                   Light("positional", 0.3, np.array([1, 5, 0]))]]

    scenes = [scene1, scene2, scene3]

    while loop:
        focusdist, camera_pos, rotZ, rotY, bounces, trace = 1, np.array([0, 0, 0]), 0, 0, 6, False

        res = (360, 360)
        rpp = 16

        scene = 1
        if iteration == 0:
            print("Our first render will be at 360x360 pixels, using the plain render engine. \n"
                  "Press escape or close the pygame window to continue to the next loop after admiring the render\n")
        elif iteration == 1:
            print("\nThat was a 360x360 image of scene 1, rendered using the basic method. "
                  "Now, you will be able to choose some parameters. \n"
                  "First, you can choose the rendering method. \"no\" will use the same method as before, \n"
                  "and \"yes\" will do path tracing. Path tracing uses bouncing light in a random direction, \n"
                  "and thus is very noisy due to randomness. Therefore, multiple rays are sent per pixel, \n"
                  "and their colour is averaged. More rays per pixel (rpp) is smoother image, \nbut "
                  "you effectively multiply the time to render by rpp.\n")
            print("Please read the README if you haven't already\n")
            raw = input((BLUE + "Use path tracing? [yes/no] : " + ENDC))
            print("")
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            data = yesno(raw)
            if data == -1:
                print(RED + "\nInput not recognised, skipping iteration\n" + ENDC)
                continue
            elif data == -1:
                print(YELLOW + "\nInput not recognised, using default = no\n" + ENDC)
                trace = False
            else:
                trace = data

            raw = input((BLUE + "Input number of rays per pixel: " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                rpp = int(sqrt(int(raw.strip()))**2)
            except:
                print(YELLOW + "\nInput not recognised, using default = 16\n" + ENDC)

        elif iteration >= 2:
            if iteration == 2:
                print("\nNow you can decide on all variables!\n")

            raw = input((BLUE + "Input horizontal resolution (multiple of 12) :"))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                data = int(raw.strip()) + 0 * sqrt(int(raw.strip()))
            except:
                print(RED + "\nInput not recognised, skipping iteration\n" + ENDC)
                continue
            if data % 12 != 0 or data < 1:
                print(RED + "\nInput was not an appropriate value, skipping iteration\n" + ENDC)
                continue
            res = (data, data)

            raw = input((BLUE + "Use path tracing? [yes/no] : " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                break
            print("")
            data = yesno(raw)
            if data == -1:
                print(RED + "\nInput not recognised, skipping iteration\n" + ENDC)
                continue
            trace = data

            raw = input((BLUE + "Input number of rays per pixel: " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                rpp = int(sqrt(int(raw.strip()))**2)
            except:
                print(YELLOW + "\nInput not recognised, using default = 16\n" + ENDC)

            raw = input((BLUE + "Input max. number of bounces: " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                bounces = int(sqrt(int(raw.strip()))**2)
            except:
                print(YELLOW + "\nInput not recognised, using default = 6\n" + ENDC)

            raw = input((BLUE + "Input scene number (1, 2, 3) : " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                scene = int(sqrt(int(raw.strip())) ** 2)
            except:
                print(YELLOW + "\nInput not recognised, using default = 1\n" + ENDC)
            if scene not in [1, 2, 3]:
                print(YELLOW + "\nInput not in specified range, using default = 1\n" + ENDC)

            raw = input((BLUE + "Input camera x : " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                camera_pos[0] = float(raw.strip())
            except:
                print(YELLOW + "\nInput not recognised, using default = 0\n" + ENDC)

            raw = input((BLUE + "Input camera y : " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                camera_pos[1] = float(raw.strip())
            except:
                print(YELLOW + "\nInput not recognised, using default = 0\n" + ENDC)

            raw = input((BLUE + "Input camera z : " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                camera_pos[2] = float(raw.strip())
            except:
                print(YELLOW + "\nInput not recognised, using default = 0\n" + ENDC)

            raw = input((BLUE + "Input camera z rotation in radians : " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                rotZ = float(raw.strip())
            except:
                print(YELLOW + "\nInput not recognised, using default = 0\n" + ENDC)

            raw = input((BLUE + "Input camera y rotation in radians : " + ENDC))
            if quittest(raw):
                print(PURPLE + "\nExiting...\n" + ENDC)
                loop = False
                continue
            try:
                rotY = float(raw.strip())
            except:
                print(YELLOW + "\nInput not recognised, using default = 0\n" + ENDC)

        res = (int(res[0]), int(res[1]))

        framebuffer = render(scenes[scene-1], 1, camera_pos, rpp, rotZ, rotY, bounces, res, 6, trace)
        time.sleep(1.3)
        FPS = pg.time.Clock()
        display = pg.display.set_mode(res)
        displayloop = True

        maxcolor = np.max(framebuffer)
        framebuffer = framebuffer * 255/maxcolor

        res = (int(res[0]), int(res[1]))

        while displayloop:
            for event in pg.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    displayloop = False
            pg.display.flip()

            for x in range(res[0]):
                for y in range(res[1]):
                    # print(framebuffer[x, y])
                    gfx.pixel(display, x, y, framebuffer[x, y])
            FPS.tick(30)
        iteration += 1
pg.quit()
