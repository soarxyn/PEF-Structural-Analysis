import math
from auxiliary.algebra import Vector3


class Concentrated:
    forceVector: Vector3 = None
    magnitude: float = None
    angle: float = None

    def __init__(self, magnitude: float, angle: float):
        self.magnitude = magnitude
        self.angle = angle

        # Getting Force Vector from Magnitude and Angle
        self.forceVector = Vector3(
            self.magnitude * math.cos(self.angle),
            self.magnitude * math.sin(self.angle),
            0,
        )


class Distributed:
    initialPositionForceVector: Vector3 = None
    finalPositionForceVector: Vector3 = None
    magnitude: float = None
    angle: float = None

    def __init__(self, x1, y1, x2, y2, magnitude, angle):
        self.initialPositionForceVector = Vector3(x1, y1)
        self.finalPositionForceVector = Vector3(x2, y2)
        self.magnitude = magnitude
        self.angle = angle


class Momentum:
    momentumPosition: Vector3 = None
    magnitude: float = None

    def __init__(self, x, y, magnitude):
        self.momentumPosition = Vector3(x, y)
        self.magnitude = magnitude


a = Concentrated(10, 1)
print(a.forceVector)
