import numpy as np
from math import *
from quartlib import eps, single_quartic


class Sphere:
    def __init__(self, r, origin: np.ndarray, colour: np.ndarray, shininess: float, luminance: float):
        self.origin = origin
        self.r = r
        self.colour = colour
        self.shininess = shininess
        self.luminance = luminance

    def normal(self, p: np.ndarray):
        rad = p - self.origin
        return rad / np.linalg.norm(rad)

    def collide(self, ray, tmin):
        A = np.dot(ray[1], ray[1])
        co = ray[0] - self.origin
        B = 2 * np.dot(co, ray[1])
        C = np.dot(co, co) - self.r ** 2
        D = B ** 2 - 4 * A * C
        if D < 0:
            return inf
        elif D == 0:
            distance = -B / (2 * A)
            if distance >= tmin:
                return distance
        else:
            distance = (-B - sqrt(D)) / (2 * A)
            if distance >= tmin:
                return distance
            else:
                distance = (-B - sqrt(D)) / (2 * A)
                if distance >= tmin:
                    return distance
        return inf


class Torus:
    def __init__(self, r: float, R: float, directoin: np.ndarray, origin: np.ndarray, colour: np.ndarray, shininess: float):
        self.origin = origin
        self.x_ = directoin
        self.y_ = np.linalg.cross(np.array([0, 0, 1]), directoin)
        self.y_ = self.y_ / np.linalg.norm(self.y_)
        self.z_ = np.linalg.cross(self.x_, self.y_)
        self.r = r
        self.R = R
        self.colour = colour
        self.shininess = shininess
        # print(self.x_, self.y_, self.z_)

    def normal(self, p: np.ndarray):
        DxP = np.linalg.cross(self.x_, p)
        p_align = np.linalg.cross(DxP, self.x_)
        circlePoint = self.R * p_align/np.linalg.norm(p_align)
        norm = p - circlePoint
        return norm/np.linalg.norm(norm)

    def collide(self, ray, tmin):
        """
        This function does not work. the quartic does get solved correctly (thanks to NKrvavica's MIT licensed code),
        only THE QUARTIC IS WRONG.
        First, the ray and origin get converted to the torus's coordinate system (defined in __init__)
        Then, (a + jt - x) etc gets put into this equation:

        (x^2 + y^2 + z^2 + R^2 - r^2)^2 = 4*R^2*(y^2 + z^2)

        This equation should be true for points on a torus with the relevant radii, and situated at the origin,
        symettric around the x-axis. It's almost straight from Wikipedia, so I don't think there are any issues with it.
        Four solutions correspond to the maximum of 4 intersection points of the ray and torus

        The (a+jt) is the point on the ray, and the (-x) results in the torus being at
        the origin.
        This mess of an expression ((a+jt-x)^2+(b+kt-y)^2+(c+lt-z)^2+R^2-r^2)^2-4R^2((b+kt-y)^2+(c+lt-z)^2)
        then gets shoved into WolframAlpha, and the plaintext output gets parsed in two stages.
        I am confident that the parsing functions properly.

        The fact that the t still remains is solved by setting it to 1 in the code, so it should not be messing stuff
        up

        it should return either inf or the first real root above 1

        For the test case here, it should have the real roots t=4 and t=6, but wrong polynomial :(
        """
        # A*t^4 + Bt^3 + Ct^2 + Dt+ E
        # for torus symmetric around x-axis
        changeMatrix = np.array([self.x_, self.y_, self.z_])
        changeMatrix = np.linalg.inv(changeMatrix)
        # print(changeMatrix)
        ray[0] = np.matmul(changeMatrix, ray[0])
        ray[1] = np.matmul(changeMatrix, ray[1])
        x, y, z = np.matmul(changeMatrix, self.origin)
        a, b, c = ray[0, 0], ray[0, 1], ray[0, 2]
        j, k, l = ray[1, 0], ray[1, 2], ray[1, 2]
        r, R, t = self.r, self.R, 1
        # print("torus origin", x, y, z, self.origin)
        # print("ray origin", a, b, c, ray[0])
        # print("ray direction", j, k, l, ray[1])
        # print("minor radius, major radius, multiplicative noop", r, R, t)
        A = - 4*x*(a**3) + 2*(b**2)*(a**2) + 2*(c**2)*(a**2) - 2*(r**2)*(a**2) + 2*(R**2)*(a**2) + 6*(x**2)*(a**2) + 2*(y**2)*(a**2) + 2*(z**2)*(a**2) - 4*b*y*(a**2) - 4*c*z*(a**2) - 4*(x**3)*a - 4*x*(y**2)*a - 4*x*(z**2)*a - 4*(b**2)*x*a - 4*(c**2)*x*a + 4*(r**2)*x*a - 4*(R**2)*x*a + 8*b*x*y*a + 8*c*x*z*a + (b**4) + (c**4) + (r**4) + (R**4) + (x**4) + (y**4) + (z**4) - 4*b*(y**3) - 4*c*(z**3) + 2*(b**2)*(c**2) - 2*(b**2)*(r**2) - 2*(c**2)*(r**2) - 2*(b**2)*(R**2) - 2*(c**2)*(R**2) - 2*(r**2)*(R**2) + 2*(b**2)*(x**2) + 2*(c**2)*(x**2) - 2*(r**2)*(x**2) + 2*(R**2)*(x**2) + 6*(b**2)*(y**2) + 2*(c**2)*(y**2) - 2*(r**2)*(y**2) - 2*(R**2)*(y**2) + 2*(x**2)*(y**2) + 2*(b**2)*(z**2) + 6*(c**2)*(z**2) - 2*(r**2)*(z**2) - 2*(R**2)*(z**2) + 2*(x**2)*(z**2) + 2*(y**2)*(z**2) - 4*b*y*(z**2) - 4*(b**3)*y - 4*b*(c**2)*y + 4*b*(r**2)*y + 4*b*(R**2)*y - 4*b*(x**2)*y - 4*(c**3)*z + 4*c*(r**2)*z + 4*c*(R**2)*z - 4*c*(x**2)*z - 4*c*(y**2)*z - 4*(b**2)*c*z + 8*b*c*y*z
        B = - 4*j*(r**2)*t*a + 4*j*(R**2)*t*a + 4*(b**2)*j*t*a + 4*(c**2)*j*t*a - 4*b*k*(r**2)*t - 4*c*l*(r**2)*t - 4*b*k*(R**2)*t - 4*c*l*(R**2)*t + 4*(b**3)*k*t + 4*b*(c**2)*k*t + 4*(c**3)*l*t + 4*(b**2)*c*l*t + 4*j*(r**2)*t*x - 4*j*(R**2)*t*x - 4*(b**2)*j*t*x - 4*(c**2)*j*t*x + 4*k*(r**2)*t*y + 4*k*(R**2)*t*y - 1*2*(b**2)*k*t*y - 4*(c**2)*k*t*y - 8*b*c*l*t*y + 4*l*(r**2)*t*z + 4*l*(R**2)*t*z - 8*b*c*k*t*z - 4*(b**2)*l*t*z - 1*2*(c**2)*l*t*z
        C = + 6*(j**2)*(t**2)*(a**2) + 2*(k**2)*(t**2)*(a**2) + 2*(l**2)*(t**2)*(a**2) + 8*b*j*k*(t**2)*a + 8*c*j*l*(t**2)*a - 1*2*(j**2)*(t**2)*x*a - 4*(k**2)*(t**2)*x*a - 4*(l**2)*(t**2)*x*a - 8*j*k*(t**2)*y*a - 8*j*l*(t**2)*z*a + 2*(b**2)*(j**2)*(t**2) + 2*(c**2)*(j**2)*(t**2) + 6*(b**2)*(k**2)*(t**2) + 2*(c**2)*(k**2)*(t**2) + 2*(b**2)*(l**2)*(t**2) + 6*(c**2)*(l**2)*(t**2) - 2*(j**2)*(r**2)*(t**2) - 2*(k**2)*(r**2)*(t**2) - 2*(l**2)*(r**2)*(t**2) + 2*(j**2)*(R**2)*(t**2) - 2*(k**2)*(R**2)*(t**2) - 2*(l**2)*(R**2)*(t**2) + 8*b*c*k*l*(t**2) + 6*(j**2)*(t**2)*(x**2) + 2*(k**2)*(t**2)*(x**2) + 2*(l**2)*(t**2)*(x**2) + 2*(j**2)*(t**2)*(y**2) + 6*(k**2)*(t**2)*(y**2) + 2*(l**2)*(t**2)*(y**2) + 2*(j**2)*(t**2)*(z**2) + 2*(k**2)*(t**2)*(z**2) + 6*(l**2)*(t**2)*(z**2) - 8*b*j*k*(t**2)*x - 8*c*j*l*(t**2)*x - 4*b*(j**2)*(t**2)*y - 1*2*b*(k**2)*(t**2)*y - 4*b*(l**2)*(t**2)*y - 8*c*k*l*(t**2)*y + 8*j*k*(t**2)*x*y - 4*c*(j**2)*(t**2)*z - 4*c*(k**2)*(t**2)*z - 1*2*c*(l**2)*(t**2)*z - 8*b*k*l*(t**2)*z + 8*j*l*(t**2)*x*z + 8*k*l*(t**2)*y*z
        D = + 4*(j**3)*(t**3)*a + 4*j*(k**2)*(t**3)*a + 4*j*(l**2)*(t**3)*a + 4*b*(k**3)*(t**3) + 4*c*(l**3)*(t**3) + 4*b*k*(l**2)*(t**3) + 4*b*(j**2)*k*(t**3) + 4*c*(j**2)*l*(t**3) + 4*c*(k**2)*l*(t**3) - 4*(j**3)*(t**3)*x - 4*j*(k**2)*(t**3)*x - 4*j*(l**2)*(t**3)*x - 4*(k**3)*(t**3)*y - 4*k*(l**2)*(t**3)*y - 4*(j**2)*k*(t**3)*y - 4*(l**3)*(t**3)*z - 4*(j**2)*l*(t**3)*z - 4*(k**2)*l*(t**3)*z
        E = + (j**4)*(t**4) + (k**4)*(t**4) + (l**4)*(t**4) + 2*(j**2)*(k**2)*(t**4) + 2*(j**2)*(l**2)*(t**4) + 2*(k**2)*(l**2)*(t**4)

        # print(A, "t^4 +", B, "t^3 +", C, "t^2 +", D, "t + ", E)
        if fabs(A) < eps:
            # print("cubic")
            if fabs(B) < eps:
                # print("quadratic")
                if fabs(C) < eps:
                    # print("linear")
                    if fabs(D) < eps:
                        # print("oops")
                        return inf
                    return -E/D
                Discr = D**2 - 4*C*E
                if Discr < 0:
                    return inf
                x1, x2 = (-D + sqrt(Discr))/(2*C), (-D - sqrt(Discr))/(2*C)
                if x2 >= tmin:
                    return x2
                elif x1 >= tmin:
                    return x1
                return inf
        roots = single_quartic(A, B, C, D, E)
        # print("roots are", roots)
        realroots = []
        for root in roots:
            if abs(root.imag) < eps:
                realroots.append(float(root.real))
        realroots.sort()
        for realroot in realroots:
            if realroot >= tmin:
                return realroot
        return inf


# suck = Torus(1, 2, np.array([1, 0, 0]), np.array([5, 0, 0]), np.array([200, 200, 200]), 50)
# dist = suck.collide(np.array([[0, 2, 0], [1, 0, 0]]))
# print(dist)


class Light:
    def __init__(self, Ltype: str, intensity: float, vector: np.ndarray = np.array([0, 0, 0])):
        self.type = Ltype
        self.intensity = intensity
        if Ltype == "directional":
            self.direction = vector / np.linalg.norm(vector)
        elif Ltype == "positional":
            self.position = vector
