class Concentrated:
    x, y = None
    magnitude = None
    angle = None

    def __init__(self, _x, _y, _magnitude, _angle):
        self.x = _x
        self.y = _y
        self.magnitude = _magnitude
        self.angle = _angle


class Distributed:
    x1, y1 = None, None
    x2, y2 = None, None
    magnitude = None
    angle = None

    def __init__(self, _x1, _y1, _x2, _y2, _magnitude, _angle):
        self.x1 = _x1
        self.y1 = _y1
        self.x2 = _x2
        self.y2 = _y2
        self.magnitude = _magnitude
        self.angle = _angle


class Momentum:
    x, y = None
    magnitude = None
    angle = None

    def __init__(self, _x, _y, _magnitude, _angle):
        self.x = _x
        self.y = _y
        self.magnitude = _magnitude
        self.angle = _angle
