from tkinter import *
from ttkthemes import themed_tk as tk
from typing import Deque, List, Tuple, Iterable, Iterator
from enum import IntEnum
from dataclasses import dataclass, field
from system import System
from collections import deque, namedtuple
from math import dist, degrees, atan2, copysign
from auxiliary.algebra import psin, pcos, ptan, Vector3
from functools import partial
from beam import Beam
from PIL import ImageTk, Image

class InsertionMode(IntEnum):
    BEAM = 0
    FORCE = 1
    DISTRIBUTED = 2
    MOMENT = 3
    SUPPORT = 4

class ActionType(IntEnum):
    ADD_BEAM = 0
    ADD_CONCENTRATED = 1
    ADD_DISTRIBUTED = 2
    ADD_MOMENT = 3
    ADD_SUPPORT = 4

@dataclass
class Action:
    related : List[object]
    type : ActionType

Point = namedtuple("Point", ("x", "y"))
sign = partial(copysign, 1)

def trunc(a):
    return round(round(a, 1), 1)

class MainWidget:

    def __init__(self, root):
        self.drawing_area = Canvas(root, width = 1360, height = 768)
        self.drawing_area.pack(fill = BOTH, expand = True, side = TOP)
        
        self.system : System = System()
        self.insertionMode : InsertionMode = InsertionMode.BEAM
        self.actions : Deque[Action] = deque()
        
        self.isMousePressed : bool = False  
        self.currentMousePosition : Point = Point(0, 0)
        self.firstWaypoint : Point = Point(0, 0)
        self.snapPoints : List[Point] = list()
        self.snapIndicators : List = list()

        self.isShiftPressed : bool = False
        self.isCtrlPressed : bool = False

        self.beamPreview = None
        self.labelPreview = None
        self.arcPreview = None
        self.anglePreview = None

        self.insertionText = None
        self.arrowIndicator = None

        self.ownedDomain : List[List[int]] = [[0 for y in range(768)] for x in range(1360)]

        self.drawing_area.bind("<ButtonPress-1>", self.leftMousePressed)
        self.drawing_area.bind("<ButtonRelease-1>", self.leftMouseReleased)
        self.drawing_area.bind("<Motion>", self.mouseMotion)
        self.drawing_area.bind("<Enter>", self.postInit)
        root.bind("<KeyPress>", self.keyboardPress)
        root.bind("<KeyRelease>", self.keyboardRelease)
        root.bind("<Control-z>", self.undo)

    def postInit(self, event = None):
        self.insertionText = self.drawing_area.create_text(20, 20, font = "Helvetica", text = "Modo de Inserção: Barra", anchor = W)

    def drawBeam(self, start : Point, end : Point, beamAngle : float, size : float, event = None) -> Tuple[object, object]:
        if self.beamPreview != None:
            event.widget.delete(self.beamPreview)

        if self.arcPreview != None:
            event.widget.delete(self.arcPreview)

        if self.labelPreview != None:
            event.widget.delete(self.labelPreview)

        if self.anglePreview != None:
            event.widget.delete(self.anglePreview)

        beam = event.widget.create_line((start, end), smooth = True, width = 5, fill="#404040")

        textAngle = beamAngle if 0 <= beamAngle < 90 else beamAngle - 180 if beamAngle > 90 else 360 + beamAngle if - 90 < beamAngle < 0 else beamAngle + 180
        length = event.widget.create_text((start.x + end.x) / 2 - 20 * psin(beamAngle), (start.y + end.y) / 2 - 20 * pcos(beamAngle), font = "Helvetica", text = "{0:1.1f} m".format(size), angle = textAngle)

        return (beam, length)

    def drawBeamPreview(self, start : Point, end : Point, beamAngle : float, size: float, event = None):
        if self.beamPreview != None:
            event.widget.delete(self.beamPreview)

        if self.arcPreview != None:
            event.widget.delete(self.arcPreview)

        if self.labelPreview != None:
            event.widget.delete(self.labelPreview)

        if self.anglePreview != None:
            event.widget.delete(self.anglePreview)

        self.beamPreview = event.widget.create_line((start, end), smooth = True, dash = (10, 10))
        self.arcPreview = event.widget.create_arc(start.x - 20, start.y - 20, start.x + 20, start.y + 20, start = 0, extent = beamAngle)
        self.anglePreview = event.widget.create_text(start.x + 40, start.y + (20 * sign(beamAngle)) if beamAngle != 0 else start.y + 20, font = "Helvetica", text = "{0:.1f}º".format(beamAngle))

        textAngle = beamAngle if 0 <= beamAngle < 90 else beamAngle - 180 if beamAngle > 90 else 360 + beamAngle if - 90 < beamAngle < 0 else beamAngle + 180
        self.labelPreview = event.widget.create_text((start.x + end.x) / 2 - 20 * psin(beamAngle), (start.y + end.y) / 2 - 20 * pcos(beamAngle), font = "Helvetica", text = "{0:1.1f} m".format(size), angle = textAngle)

    def beamParameters(self, start : Point, end : Point) -> Tuple[Point, Point, float, float]:
        angle : float = 0
        nearSnapPoint : bool = False 

        if self.isShiftPressed:
            for point in self.snapPoints:
                if dist(point, end) <= 40 and point != start:
                    nearSnapPoint = True
                    end = point

        angle = atan2(start.y - end.y, end.x - start.x)
        angle = degrees(angle)

        if self.isShiftPressed and not nearSnapPoint:
            snap : float = abs(angle)

            snaps : List[float] = [0, 30, 45, 60, 90, 120, 135, 150, 180]
            transform : List[float] = [snap,  30 - snap, 45 - snap, 60 - snap, 90 - snap, 120 - snap, 135 - snap, 150 - snap, 180 - snap]
            transform = list(map(abs, transform))
            snap = snaps[transform.index(min(transform))]
            angle = snap if angle > 0 else - snap

        end = Point(end.x, start.y - (end.x  - start.x) * ptan(angle)) if abs(angle) != 90 else Point(start.x, end.y)
        length : float = dist(end, start) / 10

        return (start, end, length, angle) 

    def leftMousePressed(self, event = None):
        self.isMousePressed = True
        self.firstWaypoint = Point(trunc(event.x), trunc(event. y))

        if not len(self.snapPoints) == 0:
            for point in self.snapPoints:
                if dist(point, self.firstWaypoint) <= 40 and self.isShiftPressed:
                    self.firstWaypoint = point
                    break

    def leftMouseReleased(self, event = None):
        self.isMousePressed = False

        if self.insertionMode == InsertionMode.BEAM:
            params = self.beamParameters(self.firstWaypoint, self.currentMousePosition)
            (beam, length) = self.drawBeam(params[0], params[1], params[3], params[2], event)

            self.actions.append(Action(related = [beam, length, params[0], params[1]], type = ActionType.ADD_BEAM))
            self.system.beams.append((Beam(params[3]), Vector3(params[0].x, params[0].y, 0), params[2], Vector3(params[1].x, params[1].y, 0)))

            if not params[0] in self.snapPoints:
                self.snapPoints.append(params[0])

            if not params[1] in self.snapPoints:
                self.snapPoints.append(params[1])

            barID = len(self.system.beams)

            rangeX : Iterable = range(int(params[0].x), int(params[1].x) + 1) if params[1].x > params[0].x else range(int(params[1].x), int(params[0].x) + 1) if params[1].x < params[0].x else [params[0].x for o in range(int(abs(params[1].y - params[0].y)) + 1)]
            rangeY : Iterable = range(int(params[0].y), int(params[1].y) + 1) if params[1].y > params[0].y else range(int(params[1].y), int(params[0].y) + 1) if params[1].y < params[0].y else [params[0].y for o in range(int(abs(params[1].x - params[0].x)) + 1)]

            for (x, y) in zip(rangeX, rangeY):
                for w in range(-15, 15):
                    for h in range(-15, 15):
                        if self.ownedDomain[x + w][y + h] == 0:
                            self.ownedDomain[x + w][y + h] = barID

    def mouseMotion(self, event = None):
        self.currentMousePosition = Point(trunc(event.x), trunc(event.y))

        if self.ownedDomain[self.currentMousePosition.x][self.currentMousePosition.y] != 0 and self.insertionMode != InsertionMode.BEAM:
            if self.arrowIndicator != None:
                self.drawing_area.delete(self.arrowIndicator)

            owner : int = self.ownedDomain[self.currentMousePosition.x][self.currentMousePosition.y]
            ownerInstance = self.system.beams[owner - 1]

            start = (ownerInstance[1].x, ownerInstance[1].y)
            end = (ownerInstance[3].x, ownerInstance[3].y)

            self.arrowIndicator = self.drawing_area.create_line((start, end), fill = "blue", width = 4)
        else:
            if self.arrowIndicator != None:
                self.drawing_area.delete(self.arrowIndicator)

        if self.isMousePressed:
            if self.insertionMode == InsertionMode.BEAM:
                params = self.beamParameters(self.firstWaypoint, self.currentMousePosition)
                self.drawBeamPreview(params[0], params[1], params[3], params[2], event)

    def keyboardPress(self, event = None):
        if event.keysym in ("Shift_L", "Shift_R"):
            self.isShiftPressed = True

            for point in self.snapPoints:
                indicator = self.drawing_area.create_oval(point[0] - 20, point[1] - 20, point[0] + 20, point[1] + 20, dash = (1, 2))
                self.snapIndicators.append(indicator)

    def keyboardRelease(self, event = None):
        if event.keysym in ("Shift_L", "Shift_R"):
            self.isShiftPressed = False
            for indicator in self.snapIndicators:
                self.drawing_area.delete(indicator)
        elif event.char == "0":
            self.insertionMode = InsertionMode.BEAM
        elif event.char == "1":
            self.insertionMode = InsertionMode.FORCE
        elif event.char == "2":
            self.insertionMode = InsertionMode.DISTRIBUTED
        elif event.char == "3":
            self.insertionMode = InsertionMode.MOMENT
        elif event.char == "4":
            self.insertionMode = InsertionMode.SUPPORT

        if self.insertionText != None:
            self.drawing_area.delete(self.insertionText)

        insertionModes : List[str] = ["Barra", "Força", "Carga Distribuída", "Momento", "Reforço"]        
        self.insertionText = self.drawing_area.create_text(20, 20, font = "Helvetica", text = f"Modo de Inserção: {insertionModes[self.insertionMode]}", anchor = W)

    def undo(self, event = None):
        if len(self.actions) > 0:
            lastAction : Action = self.actions.pop()

            if lastAction.type == ActionType.ADD_BEAM:
                beam = lastAction.related[0]
                label = lastAction.related[1]
                
                rangeX : Iterable = range(int(lastAction.related[2].x), int(lastAction.related[3].x) + 1) if lastAction.related[3].x > lastAction.related[2].x else range(int(lastAction.related[3].x), int(lastAction.related[2].x) + 1) if lastAction.related[3].x < lastAction.related[2].x else [lastAction.related[2].x for o in range(int(abs(lastAction.related[3].y - lastAction.related[2].y)) + 1)]
                rangeY : Iterable = range(int(lastAction.related[2].y), int(lastAction.related[3].y) + 1) if lastAction.related[3].y > lastAction.related[2].y else range(int(lastAction.related[3].y), int(lastAction.related[2].y) + 1) if lastAction.related[3].y < lastAction.related[2].y else [lastAction.related[2].y for o in range(int(abs(lastAction.related[3].x - lastAction.related[2].x)) + 1)]

                for (x, y) in zip(rangeX, rangeY):
                    for w in range(-15, 15):
                        for h in range(-15, 15):
                            self.ownedDomain[x + w][y + h] = 0

                self.drawing_area.delete(beam)
                self.drawing_area.delete(label)
                self.system.beams.pop()
                self.snapPoints.clear()

                for beam in self.system.beams:
                    if not beam[0] in self.snapPoints:
                        self.snapPoints.append(Point(beam[1].x, beam[1].y))

                    if not beam[3] in self.snapPoints:
                        self.snapPoints.append(Point(beam[3].x, beam[3].y))

if __name__ == "__main__":
    root = tk.ThemedTk()
    root.set_theme("breeze")
    root.title("PEF3208 - Análise de Estruturas 2D")
    root.geometry("1360x768")

    mainWidget : MainWidget = MainWidget(root)
    root.mainloop()
