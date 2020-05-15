import math
from auxiliary.algebra import *


class Concentrated:
    forceVector: Vector3 = None
    magnitude: float = None
    angle: float = None

    def __init__(self, magnitude : float, angle : float):
        self.magnitude = magnitude
        self.angle = angle

        # Getting Force Vector from Magnitude and Angle
        self.forceVector = Vector3(
            magnitude * math.cos(angle),
            magnitude * math.sin(angle),
            0,
        )


class Distributed:
    length : float = None
    polynomial : Polynomial = Polynomial()
    angle : float = None
    equivalent : Concentrated = None

    def __init__(self, p1 : float, p2: float, p : Polynomial, a : float):
        self.length = abs(p2 - p1)
        self.polynomial = p
        self.angle = a
        self.equivalent = Concentrated(p.integrate(0, abs(p2 - p1)), a)


class Momentum:
    magnitude: float = None

    def __init__(self, magnitude : float):
        self.magnitude = magnitude


a = Concentrated(10, 1)
print(a.forceVector)
