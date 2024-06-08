import multiprocessing as mp
import time

import numpy as np

from lib import *


def normalise_ra(ray_array):
    # makes unit vector
    lengths = np.sqrt(np.sum(ray_array[:, :, 1] * ray_array[:, :, 1], -1))
    ray_array[:, :, 1, 0] = ray_array[:, :, 1, 0] / lengths
    ray_array[:, :, 1, 1] = ray_array[:, :, 1, 1] / lengths
    ray_array[:, :, 1, 2] = ray_array[:, :, 1, 2] / lengths


def getlighting(point: np.ndarray, normal: np.ndarray, viewVector: np.ndarray, shiny, lights: list[Light]):
    intensity = 0
    for light in lights:
        if light.type == "ambient":
            intensity += light.intensity
        else:
            if light.type == "positional":
                v_to_light = light.position - point
                v_to_light = v_to_light / np.linalg.norm(v_to_light)
            else:
                v_to_light = -light.direction

            # this makes the object brighter the closer the light vector is to the surface normal
            diffuseDot = np.dot(v_to_light, normal)

            if diffuseDot > 0:
                intensity += light.intensity * diffuseDot

            if shiny != -1:
                # here the same is done with the view vector and the light vector reflected across the normal, and
                # this effectively cosine weighted distribution is raised to the power of "shiny" to control
                # the specular highlights.
                reflectionVector = 2 * normal * np.dot(normal, v_to_light) - v_to_light
                reflectionDot = np.dot(reflectionVector, -viewVector)
                if reflectionDot > 0:
                    intensity += light.intensity * pow(reflectionDot, shiny)
    return intensity


def intersect_closest(ray, tmin, spheres: list[Sphere], torii: list[Torus]):
    """
    returns the closest object and the distance to it as long as the distance is greater than tmin (in graphics
    programming terms I think this is called the near clipping plane). The tmin cutoff makes close objects not render
    instead of rendering as a distorted mess.
    """
    mindist = inf
    closest = None
    for sphere in spheres:
        distance = sphere.collide(ray, tmin)
        if distance < mindist:
            mindist = distance
            closest = sphere
    for torus in torii:
        distance = torus.collide(ray, tmin)
        if distance < mindist:
            mindist = distance
            closest = torus
    return closest, mindist


def trace(ray, bckgr: np.ndarray, lights: list[Light], spheres: list[Sphere], torii: list[Torus], tmin):
    """
    traces the ray once, calculates the lighting intensity and multiplies the colour of the collided object with the
    lighting intensity. This function, contrary to its name, only does simple rendering. I found it easier to implement
    a similar function again to get multiple bounces.
    """
    closest, mindist = intersect_closest(ray, tmin, spheres, torii)
    if closest is None:
        return bckgr
    point = ray[0] + mindist * ray[1]
    normal = closest.normal(point)
    intensity = min(getlighting(point, normal, ray[1], closest.shininess, lights), 1)
    return closest.colour * intensity


def getcolour(ray, bckgr, lights, spheres, torii, depth):
    """
    this is the function used for the path tracing. It starts with no incoming light, and a colour which has not yet/
    will not be subtracted from by reflections. As bounces occur, incoming light gets added, and future incoming light
    gets dimmed and tinted by the colour of the object it bounces off. Only the first bounce has a significant near
    clipping plane. The bounces occur in a random direction in the hemisphere around the normal at the bounce.
    The distribution is probably not equal (I don't have a proper game engine to render
    the distribution and spot patterns), but when I used a normal distribution which plays better with spheres, I got
    an error
    """
    tmin = 1
    inLight = np.array([0.0, 0.0, 0.0])
    colourf = np.array([1., 1., 1.])
    for d in range(depth):
        closest, mindist = intersect_closest(ray, tmin, spheres, torii)
        tmin = 1e-5
        if closest is not None:
            point = ray[0] + mindist * ray[1]
            reflec = np.random.standard_normal(3)
            reflec /= np.linalg.norm(reflec)
            reflec = reflec * copysign(1, np.linalg.vecdot(reflec, closest.normal(point)))
            ray = np.array([point, reflec])
            emitted_light = closest.colour * closest.luminance/255
            inLight += emitted_light * colourf
            colourf *= closest.colour/255.
            # print(inLight, colourf)
        else:
            break
    return inLight


def getpixel(rpp, ray, bckgr, lights, spheres, torii, depth):
    colour = np.array([0.0, 0.0, 0.0])
    for n in range(rpp):
        colour += 255*getcolour(ray, bckgr, lights, spheres, torii, depth)
    colour /= rpp
    return colour


def getpixelb(rpp, ray, bckgr, lights, spheres, torii):
    colour = trace(ray, bckgr, lights, spheres, torii, 1)
    return colour


def dispatched(num_assigned, index, qeu: mp.Queue, res, rpp, rays, bckgr, lights, spheres, torii, depth, dotrace):
    # print(index, "started")
    start = num_assigned * index
    count = 0
    count2 = 0
    for clmn in range(start, start + num_assigned):
        if index == 0:
            count += 1

        for y in range(res[1]):
            if index == 5:
                progress = round(80 * (count*res[1]+y) / (num_assigned*res[1]))
                remain = 80 - progress
                match count2:
                    case 0:
                        print(("\rProcess 5 progess: / [" + progress * "#" + remain * "-" + "]"), end='')
                    case 1:
                        print(("\rProcess 5 progess: - [" + progress * "#" + remain * "-" + "]"), end='')
                    case 2:
                        print(("\rProcess 5 progess: \\ [" + progress * "#" + remain * "-" + "]"), end='')
                    case 3:
                        print(("\rProcess 5 progess: | [" + progress * "#" + remain * "-" + "]"), end='')
                count2 = (count2 + 1) % 4
            if dotrace:
                qeu.put(getpixel(rpp, rays[clmn, y], bckgr, lights, spheres, torii, depth))
            else:
                qeu.put(getpixelb(rpp, rays[clmn, y], bckgr, lights, spheres, torii))
    print("Process", index, "has finished")

# / - \ |


def render(scene, focusdist, camera_pos, rpp, rotZ, rotY, focus, res: tuple, depth, dotrace):
    # setup scene objects
    bckgr = scene[0]
    spheres: list[Sphere] = scene[1]
    torii: list[Torus] = scene[2]
    lights: list[Light] = scene[3]

    # output object
    framebuffer = np.zeros((res[0], res[1], 3))
    # print(res)

    # background colour
    bckgr = np.array([20, 20, 20])

    f_field_w = focusdist * 1
    f_field_h = focusdist * 1

    ul_ray = np.array([focusdist, f_field_h / 2, -f_field_w / 2])
    dl_ray = np.array([focusdist, -f_field_h / 2, -f_field_w / 2])
    ur_ray = np.array([focusdist, f_field_h / 2, f_field_w / 2])
    dr_ray = np.array([focusdist, -f_field_h / 2, f_field_w / 2])

    cornerRays = np.array([ul_ray, dl_ray, ur_ray, dr_ray])

    # calculate rotation matrices
    rotY_m = np.array([[cos(rotY), 0, sin(rotY)], [0, 1, 0], [-sin(rotY), 0, cos(rotY)]])
    rotZ_m = np.array([[cos(rotZ), -sin(rotZ), 0], [sin(rotZ), cos(rotZ), 0], [0, 0, 1]])

    # rotate the corner rays
    for j in range(4):
        cornerRays[j] = np.matmul(rotY_m, np.matmul(rotZ_m, cornerRays[j]))

    # sets one ray per pixel, ray is [origin, direction]
    rays = np.linspace(np.linspace(np.array([camera_pos, cornerRays[0]]),
                                   np.array([camera_pos, cornerRays[1]]), res[1]),
                       np.linspace(np.array([camera_pos, cornerRays[2]]),
                                   np.array([camera_pos, cornerRays[3]]), res[1]), res[0])
    # creates an effect where the focus field is most in focus
    # offsets = np.random.rand(res[0], res[1], 3)/focus
    # rays[:, :, 0, :] += offsets
    # rays[:, :, 1, :] -= offsets

    # normalise direction vectors
    normalise_ra(rays)

    print("Multiprocessing start")

    # multiprocessing stuff
    processes = []
    nprocesses = 12
    clmns_assigned = ceil(res[0] / nprocesses)
    queues = []
    index = 0

    for pnum in range(nprocesses):
        queues.append(mp.Queue())
        processes.append(mp.Process(target=dispatched, args=(
            clmns_assigned, index, queues[-1], res, rpp, rays, bckgr, lights, spheres, torii, depth, dotrace)))
        # print(index)
        index += 1

    for proc in processes:
        # print(proc)
        proc.start()

    print("All processes started")

    pid = 0
    time.sleep(3)

    for proc in processes:
        proc.join(0)
        for x in range(clmns_assigned * pid, clmns_assigned * (pid + 1)):
            for y in range(res[1]):
                framebuffer[x, y] = queues[pid].get()
        # print("pid", pid, "done")
        pid += 1
    return framebuffer
