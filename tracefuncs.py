import multiprocessing as mp
import time

import numpy as np

from lib import *


def normalise_ra(ray_array):
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
            diffuseDot = np.dot(v_to_light, normal)
            if diffuseDot > 0:
                intensity += light.intensity * diffuseDot

            if shiny != -1:
                reflectionVector = 2 * normal * np.dot(normal, v_to_light) - v_to_light
                reflectionDot = np.dot(reflectionVector, -viewVector)
                if reflectionDot > 0:
                    intensity += light.intensity * pow(reflectionDot, shiny)
    return intensity


def intersect_closest(ray, tmin, spheres: list[Sphere], torii: list[Torus]):
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


def trace(ray, bckgr: np.ndarray, lights: list[Light], spheres: list[Sphere], torii: list[Torus], tmin, depth):
    closest, mindist = intersect_closest(ray, tmin, spheres, torii)
    if closest is None:
        return None
    point = ray[0] + mindist * ray[1]
    normal = closest.normal(point)
    intensity = min(getlighting(point, normal, ray[1], closest.shininess, lights), 1)
    if depth == 0:
        return closest.colour * intensity
    else:
        reflec = np.random.normal(3)
        reflec /= np.linalg.norm(reflec)
        reflec *= copysign(1, np.dot(reflec, normal))
        newray = np.array([point, reflec])
        return trace(newray, bckgr, lights, spheres, torii, 0.001, depth-1)


def getpixel(rpp, ray, bckgr, lights, spheres, torii, depth):
    colour = np.array([0.0, 0.0, 0.0])
    for n in range(rpp):
        colour += trace(ray, bckgr, lights, spheres, torii, 1, depth).real
    colour /= rpp
    return colour


def dispatched(num_assigned, index, qeu: mp.Queue, res, rpp, rays, bckgr, lights, spheres, torii, depth):
    print(index, "started")
    start = num_assigned * index
    count = 0
    for clmn in range(start, start + num_assigned):
        if index == 0:
            progress = floor(80*count/num_assigned)
            remain = 80 - progress
            print(("\rProcess 0 progess: [" + progress*"#" + remain*"-" + "]"), end='')
            count += 1
        for y in range(res[1]):
            qeu.put(getpixel(rpp, rays[clmn, y], bckgr, lights, spheres, torii, depth))
    print("Process", index, "has finished")


def render(scene, focusdist, camera_pos, rpp, rotZ, rotY, focus, res: tuple, depth):
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
            clmns_assigned, index, queues[-1], res, rpp, rays, bckgr, lights, spheres, torii, depth)))
        print(index)
        index += 1

    for proc in processes:
        print(proc)
        proc.start()

    print("started")

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
