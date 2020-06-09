from tkinter import *
from ttkthemes import themed_tk as tk
from typing import Deque, List, Tuple, Iterable, Iterator, Optional, Callable
from enum import IntEnum
from dataclasses import dataclass, field
from system import System
from collections import deque, namedtuple
from math import dist, degrees, atan2, copysign
from auxiliary.algebra import psin, pcos, ptan, Vector3, Polynomial
from functools import partial
from beam import Beam
from PIL import ImageTk, Image
from force import Concentrated, Distributed, Moment
from support import Support, SupportType

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
        self.inserting : bool = False

        self.beamPreview = None
        self.labelPreview = None
        self.arcPreview = None
        self.anglePreview = None
        self.forcePreview = None
        self.startLabelPreview = None

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
        if self.insertionText == None:
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
        length : float = round(dist(end, start) / 10, 1)
        print(length)

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

        if self.inserting:
            return

        if self.insertionMode == InsertionMode.BEAM:
            params = self.beamParameters(self.firstWaypoint, self.currentMousePosition)
            (beam, length) = self.drawBeam(params[0], params[1], params[3], params[2], event)
            addedBeam : Beam = Beam(params[2])

            if len(self.system.beams) > 0:
                for beamItem in self.system.beams:
                    if Point(beamItem[1].x, beamItem[1].y) == params[0]:
                        beamItem[0].start[1].append(addedBeam)
                        addedBeam.start[1].append(addedBeam)
                    elif Point(beamItem[1].x, beamItem[1].y) == params[1]:
                        beamItem[0].start[1].append(addedBeam)
                        addedBeam.end[1].append(addedBeam)
                    elif Point(beamItem[3].x, beamItem[3].y) == params[0]:
                        beamItem[0].end[1].append(addedBeam)
                        addedBeam.start[1].append(addedBeam)
                    elif Point(beamItem[3].x, beamItem[3].y) == params[1]:
                        beamItem[0].end[1].append(addedBeam)
                        addedBeam.end[1].append(addedBeam)

            self.actions.append(Action(related = [beam, length, params[0], params[1]], type = ActionType.ADD_BEAM))
            self.system.beams.append((addedBeam, Vector3(params[0].x, params[0].y, 0), params[3], Vector3(params[1].x, params[1].y, 0)))

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
        
        elif self.insertionMode == InsertionMode.FORCE:
            owner : int = self.ownedDomain[self.currentMousePosition.x][self.currentMousePosition.y]
            
            if owner != 0:
                self.inserting = True
                beam = self.system.beams[owner - 1]

                self.forcePreview = self.drawing_area.create_line(beam[1].x, beam[1].y - 50, beam[1].x, beam[1].y, arrow = LAST, width = 4.0, activefill = "blue", smooth = True)
                self.labelPreview = self.drawing_area.create_text(beam[1].x + 10, beam[1].y - 25, font = "Helvetica", text = "1 kN", anchor = W)
                
                support = Toplevel(self.drawing_area)
                self.supportWindow = SupportWidget(support, self, "Parâmetros: Força", self.currentMousePosition.x + 350, self.currentMousePosition.y, InsertionMode.FORCE, force = Point(beam[1].x, beam[1].y), beamAngle = beam[2], beamID = owner)

        elif self.insertionMode == InsertionMode.DISTRIBUTED:
            owner : int = self.ownedDomain[self.currentMousePosition.x][self.currentMousePosition.y]

            if owner != 0:
                self.inserting = True
                beam = self.system.beams[owner - 1]

                self.forcePreview = list()

                support = Toplevel(self.drawing_area)
                self.supportWindow = SupportWidget(support, self, "Parâmetros: Carga Distribuída", self.currentMousePosition.x + 350, self.currentMousePosition.y, InsertionMode.DISTRIBUTED, force = Point(beam[1].x, beam[1].y), beamAngle = beam[2], beamID = owner)

        elif self.insertionMode == InsertionMode.MOMENT:
            owner : int = self.ownedDomain[self.currentMousePosition.x][self.currentMousePosition.y]

            if owner != 0:
                self.inserting = True
                beam = self.system.beams[owner - 1]

                support = Toplevel(self.drawing_area)
                self.supportWindow = SupportWidget(support, self, "Parâmetros: Momento", self.currentMousePosition.x + 350, self.currentMousePosition.y, InsertionMode.MOMENT, force = Point(beam[1].x, beam[1].y), beamAngle = beam[2], beamID = owner, beamEnd = Point(beam[3].x, beam[3].y))

        elif self.insertionMode == InsertionMode.SUPPORT:
            owner : int = self.ownedDomain[self.currentMousePosition.x][self.currentMousePosition.y]

            if owner != 0:
                self.inserting = True
                beam = self.system.beams[owner - 1]

                support = Toplevel(self.drawing_area)
                self.supportWindow = SupportWidget(support, self, "Parâmetros: Reforço", self.currentMousePosition.x + 350, self.currentMousePosition.y, InsertionMode.SUPPORT, force = Point(beam[1].x, beam[1].y), beamAngle = beam[2], beamID = owner, beamEnd = Point(beam[3].x, beam[3].y))

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
        elif self.inserting:
            return
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
        elif event.char == "s":
            polynomials = self.system.solveSystem()

            supportNormal = Toplevel(self.drawing_area)
            supportShear = Toplevel(self.drawing_area)
            supportBending = Toplevel(self.drawing_area)

            normal = ResultWidget(supportNormal, "Normal", self.system.beams.copy(), polynomials, 0)
            shear = ResultWidget(supportShear, "Cortante", self.system.beams.copy(), polynomials, 1)
            bending = ResultWidget(supportBending, "Momento", self.system.beams.copy(), polynomials, 2)

        if self.insertionText != None:
            self.drawing_area.delete(self.insertionText)
            self.insertionText = None

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
                            self.ownedDomain[trunc(x + w)][trunc(y + h)] = 0

                self.drawing_area.delete(beam)
                self.drawing_area.delete(label)
                self.system.beams.pop()
                self.snapPoints.clear()

                for beamItem in self.system.beams:
                    if not beamItem[0] in self.snapPoints:
                        self.snapPoints.append(Point(beamItem[1].x, beamItem[1].y))

                    if not beamItem[3] in self.snapPoints:
                        self.snapPoints.append(Point(beamItem[3].x, beamItem[3].y))

                    if beam in beamItem[0].start[1]:
                        beamItem[0].start[1].remove(beam)

                    elif beam in beamItem[0].end[1]:
                        beamItem[0].end[1].remove(beam)
            
                del beam

            elif lastAction.type == ActionType.ADD_CONCENTRATED:
                self.system.beams[lastAction.related[2] - 1][0].concentratedList.pop()
                self.drawing_area.delete(lastAction.related[0])
                self.drawing_area.delete(lastAction.related[1])

            elif lastAction.type == ActionType.ADD_DISTRIBUTED:
                self.system.beams[lastAction.related[2] - 1][0].distributedList.pop()

                for force in lastAction.related[0]:
                    self.drawing_area.delete(force)
                
                self.drawing_area.delete(lastAction.related[1])

                if lastAction.related[3]:
                    self.drawing_area.delete(lastAction.related[4])

            elif lastAction.type == ActionType.ADD_MOMENT:
                self.system.beams[lastAction.related[2] - 1][0].moment = None
                self.drawing_area.delete(lastAction.related[0])
                self.drawing_area.delete(lastAction.related[1])

            elif lastAction.type == ActionType.ADD_SUPPORT:
                if lastAction.related[3] == 0:
                    self.system.beams[lastAction.related[2] - 1][0].start = (None, self.system.beams[lastAction.related[2] - 1][0].start[1])
                else:
                    self.system.beams[lastAction.related[2] - 1][0].end = (None, self.system.beams[lastAction.related[2] - 1][0].end[1])

                self.drawing_area.delete(lastAction.related[0])

class SupportWidget:

    def __init__(self, master, master_window, name: str, x: int, y: int, mode: InsertionMode, force: Optional[Point], beamAngle: Optional[float], beamID: Optional[int], beamEnd = None):
        self.master = master
        self.master.geometry(f"450x350+{x}+{y}")
        self.master.title(name)
        
        self.frame = Frame(self.master)
        self.frame.pack()

        self.master_window = master_window
        
        self.mode = mode
        self.beamAngle = beamAngle
        self.beamID = beamID
        self.master_force = force
        self.beamEnd = beamEnd

        if mode == InsertionMode.FORCE:
            self.angleContent = StringVar()
            self.angleContent.trace("w", lambda a, b, c: self.updateForce())
            
            self.lengthContent = StringVar()
            self.lengthContent.trace("w", lambda a, b, c: self.updateForce())
            
            self.positionContent = StringVar()
            self.positionContent.trace("w", lambda a, b, c: self.updateForce())

            self.angleContent.set("90")
            self.lengthContent.set("1")
            self.positionContent.set("0")

            introLabel = Label(self.frame, font = "Helvetica", text = "Parâmetros de Força Concentrada")
            introLabel.grid(row = 0, column = 1, padx = 0, pady = (5, 0))

            angleLabel = Label(self.frame, font = "Helvetica", text = "Ângulo: ")
            angleLabel.grid(row = 1, column = 0, padx = 3, pady = 20)

            angleEntry = Entry(self.frame, textvariable = self.angleContent)
            angleEntry.grid(row = 1, column = 1)

            degreesLabel = Label(self.frame, font = "Helvetica", text = "º")
            degreesLabel.grid(row = 1, column = 2, padx = 2)

            lengthLabel = Label(self.frame, font = "Helvetica", text = "Módulo: ")
            lengthLabel.grid(row = 2, column = 0)

            lengthEntry = Entry(self.frame, textvariable = self.lengthContent)
            lengthEntry.grid(row = 2, column = 1)

            newtonLabel = Label(self.frame, font = "Helvetica", text = "kN")
            newtonLabel.grid(row = 2, column = 2, padx = 2)

            positionLabel = Label(self.frame, font = "Helvetica", text = "Posição: ")
            positionLabel.grid(row = 3, column = 0)

            positionEntry = Entry(self.frame, textvariable = self.positionContent)
            positionEntry.grid(row = 3, column = 1, pady = 20)

            metersLabel = Label(self.frame, font = "Helvetica", text = "m")
            metersLabel.grid(row = 3, column = 2)

            insertButton = Button(self.frame, text = "Inserir Força", font = "Helvetica", command = lambda: self.insertForce())
            insertButton.grid(row = 4, column = 1)
        
        elif mode == InsertionMode.DISTRIBUTED:
            self.angleContent = StringVar()
            self.angleContent.trace("w", lambda a, b, c: self.updateDistributed())

            self.radioContent = IntVar()
            self.lastRadio = None

            self.startPosContent = StringVar()
            self.startPosContent.trace("w", lambda a, b, c: self.updateDistributed())

            self.endPosContent = StringVar()
            self.endPosContent.trace("w", lambda a, b, c: self.updateDistributed())

            introLabel = Label(self.frame, font = "Helvetica", text = "Parâmetros de Carga Distribuída")
            introLabel.grid(row = 0, column = 1, padx = 0, pady = (5, 0))
            
            angleLabel = Label(self.frame, font = "Helvetica", text = "Ângulo: ")
            angleLabel.grid(row = 1, column = 0, padx = 3, pady = 20)

            angleEntry = Entry(self.frame, textvariable = self.angleContent)
            angleEntry.grid(row = 1, column = 1)

            degreesLabel = Label(self.frame, font = "Helvetica", text = "º")
            degreesLabel.grid(row = 1, column = 2, padx = 0)

            typeLabel = Label(self.frame, font = "Helvetica", text = "Tipo de Carga")
            typeLabel.grid(row = 2, column = 1)

            uniform = Radiobutton(self.frame, text = "Uniforme", variable = self.radioContent, value = 0, command = lambda: self.updateDistributed())
            uniform.grid(row = 3, column = 0)

            linear = Radiobutton(self.frame, text = "Linear", variable = self.radioContent, value = 1, command = lambda: self.updateDistributed())
            linear.grid(row = 3, column = 1)

            posLabel = Label(self.frame, font = "Helvetica", text = "Posição da Carga")
            posLabel.grid(row = 5, column = 1, pady = (20, 0))

            startPosEntry = Entry(self.frame, textvariable = self.startPosContent, width = 4)
            startPosEntry.grid(row = 6, column = 1)

            endPosEntry = Entry(self.frame, textvariable = self.endPosContent, width = 4)
            endPosEntry.grid(row = 6, column = 3)

            startLabel = Label(self.frame, font = "Helvetica", text = "De")
            startLabel.grid(row = 6, column = 0, pady = 20)

            endLabel = Label(self.frame, font = "Helvetica", text = "Até")
            endLabel.grid(row = 6, column = 2, padx = 0)

            insertButton = Button(self.frame, text = "Inserir Carga", font = "Helvetica", command = lambda: self.insertDistributed())
            insertButton.grid(row = 7, column = 1)

            self.distributedParameters = list()
            self.distributedEntries = list()
            self.distributedLabels = list()

            self.radioContent.set(0)
            self.angleContent.set("90")
            self.startPosContent.set("0")
            self.endPosContent.set("5")

        elif mode == InsertionMode.MOMENT:
            self.positionContent = StringVar()
            self.positionContent.trace("w", lambda a, b, c: self.updateMoment())

            self.magnitudeContent = StringVar()
            self.magnitudeContent.trace("w", lambda a, b, c: self.updateMoment())

            introLabel = Label(self.frame, font = "Helvetica", text = "Parâmetros de Momento")
            introLabel.grid(row = 0, column = 1, padx = 0, pady = (5, 0))

            guideLabel = Label(self.frame, font = "Helvetica", text = "Positivo = Anti-Horário")
            guideLabel.grid(row = 2, column = 1, padx = 0, pady = (5, 0))

            magnitudeLabel = Label(self.frame, font = "Helvetica", text = "Módulo: ")
            magnitudeLabel.grid(row = 1, column = 0, padx = 3, pady = 20)

            magnitudeEntry = Entry(self.frame, textvariable = self.magnitudeContent)
            magnitudeEntry.grid(row = 1, column = 1)

            kNmLabel = Label(self.frame, font = "Helvetica", text = "kNm")
            kNmLabel.grid(row = 1, column = 2, padx = 0)

            insertButton = Button(self.frame, text = "Inserir Momento", font = "Helvetica", command = lambda: self.insertMoment())
            insertButton.grid(row = 3, column = 1)
            
            self.positionContent.set("0")
            self.magnitudeContent.set("1")
    
        elif mode == InsertionMode.SUPPORT:
            self.typeContent = IntVar()
            self.lastType = None

            self.positionContent = IntVar()
            self.lastPosition = None

            self.angleContent = StringVar()
            self.angleContent.trace("w", lambda a, b, c: self.updateSupport())

            introLabel = Label(self.frame, font = "Helvetica", text = "Parâmetros de Reforço")
            introLabel.grid(row = 0, column = 1, padx = 0, pady = (5, 0))

            posLabel = Label(self.frame, font = "Helvetica", text = "Posição do Reforço")
            posLabel.grid(row = 1, column = 1, pady = (20, 0))

            start = Radiobutton(self.frame, text = "Início", variable = self.positionContent, value = 0, command = lambda: self.updateSupport())
            start.grid(row = 2, column = 0)

            end = Radiobutton(self.frame, text = "Final", variable = self.positionContent, value = 1, command = lambda: self.updateSupport())
            end.grid(row = 2, column = 1)

            typeLabel = Label(self.frame, font = "Helvetica", text = "Tipo de Reforço")
            typeLabel.grid(row = 3, column = 1, pady = (20, 0))

            simple = Radiobutton(self.frame, text = "Simples", variable = self.typeContent, value = 0, command = lambda: self.updateSupport())
            simple.grid(row = 4, column = 0)

            pinned = Radiobutton(self.frame, text = "Duplo", variable = self.typeContent, value = 1, command = lambda: self.updateSupport())
            pinned.grid(row = 4, column = 1)

            fixed = Radiobutton(self.frame, text = "Engastamento", variable = self.typeContent, value = 2, command = lambda: self.updateSupport())
            fixed.grid(row = 4, column = 2)

            self.angleLabel = Label(self.frame, font = "Helvetica", text = "Ângulo: ")
            self.angleLabel.grid(row = 5, column = 0, padx = 3, pady = 20)

            self.angleEntry = Entry(self.frame, textvariable = self.angleContent)
            self.angleEntry.grid(row = 5, column = 1)

            self.degreesLabel = Label(self.frame, font = "Helvetica", text = "º")
            self.degreesLabel.grid(row = 5, column = 2, padx = 0)

            insertButton = Button(self.frame, text = "Inserir Reforço", font = "Helvetica", command = lambda: self.insertSupport())
            insertButton.grid(row = 6, column = 1, pady = 20)
            
            self.typeContent.set(0)
            self.positionContent.set(0)
            self.angleContent.set("90")

    def updateForce(self):
        force_angle = float(self.angleContent.get()) - self.beamAngle if len(self.angleContent.get()) != 0 else 0
        length = float(self.lengthContent.get()) if len(self.lengthContent.get()) != 0 else 1
        pos = float(self.positionContent.get()) if len(self.positionContent.get()) != 0 else 0

        scale = 1 if 0 <= length < 10 else 0.1 if 10 <= length < 100 else 0.01 if 100 <= length < 1000 else 0.001

        tipX : float = self.master_force.x + (pos * pcos(self.beamAngle) * 10)
        tipY : float = self.master_force.y - (pos * psin(self.beamAngle) * 10)

        self.master_window.drawing_area.delete(self.master_window.forcePreview)
        self.master_window.forcePreview = self.master_window.drawing_area.create_line(tipX - 20 * length * scale * pcos(force_angle), tipY - 20 * length * scale * psin(force_angle), tipX, tipY, arrow = LAST, width = 4.0, activefill = "blue", smooth = True)
        self.master_window.drawing_area.delete(self.master_window.labelPreview)
        self.master_window.labelPreview = self.master_window.drawing_area.create_text(tipX + 10 - 40 * pcos(force_angle) if force_angle <= 180 else tipX, tipY - 20 - 40 * psin(force_angle) if force_angle < 180 else tipY - 20, font = "Helvetica", text = f"{length} kN", anchor = W)
        
    def insertForce(self):
        force_angle = float(self.angleContent.get()) - self.beamAngle if len(self.angleContent.get()) != 0 else 0
        length = float(self.lengthContent.get()) if len(self.lengthContent.get()) != 0 else 1
        pos = float(self.positionContent.get()) if len(self.positionContent.get()) != 0 else 0

        scale = 1 if 0 <= length < 10 else 0.1 if 10 <= length < 100 else 0.01 if 100 <= length < 1000 else 0.001

        tipX : float = self.master_force.x + (pos * pcos(self.beamAngle) * 10)
        tipY : float = self.master_force.y - (pos * psin(self.beamAngle) * 10)

        self.master_window.system.beams[self.beamID - 1][0].concentratedList.append((Concentrated(length), pos, force_angle + self.beamAngle))
        self.master_window.drawing_area.delete(self.master_window.forcePreview)
        self.master_window.drawing_area.delete(self.master_window.labelPreview)

        force = self.master_window.drawing_area.create_line(tipX - 20 * length * scale * pcos(force_angle), tipY - 20 * length * scale * psin(force_angle), tipX, tipY, arrow = LAST, width = 4.0, activefill = "blue", smooth = True)
        label = self.master_window.drawing_area.create_text(tipX + 10 - 40 * pcos(force_angle) if force_angle <= 180 else tipX, tipY - 20 - 40 * psin(force_angle) if force_angle < 180 else tipY - 20, font = "Helvetica", text = f"{length} kN", anchor = W)
        
        self.master_window.actions.append(Action(related = (force, label, self.beamID), type = ActionType.ADD_CONCENTRATED))

        self.master_window.inserting = False
        self.master.destroy()

    def updateDistributed(self):
        force_angle = float(self.angleContent.get()) - self.beamAngle if len(self.angleContent.get()) != 0 else 0
        radioOption = self.radioContent.get()
        start_pos = float(self.startPosContent.get()) if len(self.startPosContent.get()) != 0 else 0
        end_pos = float(self.endPosContent.get()) if len(self.endPosContent.get()) != 0 else 5

        if self.lastRadio != radioOption:
            self.distributedParameters.clear()

            for entry in self.distributedEntries:
                entry.grid_remove()
            
            for label in self.distributedLabels:
                label.grid_remove()

            self.distributedEntries.clear()
            self.distributedLabels.clear()

            if radioOption == 0:
                uniformLoad = StringVar()
                uniformLoad.set("1")
                uniformLoad.trace("w", lambda a, b, c: self.updateDistributed())

                self.distributedParameters.append(uniformLoad)

                loadEntry = Entry(self.frame, textvariable = uniformLoad, width = 4)
                loadEntry.grid(row = 4, column = 0)

                entryLabel = Label(self.frame, font = "Helvetica", text = "kN/m")
                entryLabel.grid(row = 4, column = 1)

                self.distributedEntries.append(loadEntry)
                self.distributedLabels.append(entryLabel)

            elif radioOption == 1:
                startLoad = StringVar()
                startLoad.set("0")
                startLoad.trace("w", lambda a, b, c: self.updateDistributed())

                endLoad = StringVar()
                endLoad.set("1")
                endLoad.trace("w", lambda a, b, c: self.updateDistributed())

                self.distributedParameters.append(startLoad)
                self.distributedParameters.append(endLoad)

                startLabel = Label(self.frame, font = "Helvetica", text = "De")
                startLabel.grid(row = 4, column = 0)

                startEntry = Entry(self.frame, textvariable = startLoad, width = 4)
                startEntry.grid(row = 4, column = 1)

                endLabel = Label(self.frame, font = "Helvetica", text = "até")
                endLabel.grid(row = 4, column = 2)

                endEntry = Entry(self.frame, textvariable = endLoad, width = 4)
                endEntry.grid(row = 4, column = 3, padx = 0)

                self.distributedEntries.append(startEntry)
                self.distributedEntries.append(endEntry)

                self.distributedLabels.append(startLabel)
                self.distributedLabels.append(endLabel)

        if radioOption == 0:
            uniformLoad = int(self.distributedParameters[0].get()) if len(self.distributedParameters[0].get()) != 0 else 1

            scale = 1 if 0 <= uniformLoad <= 10 else 0.1 if 10 < uniformLoad < 100 else 0.01 if 100 <= uniformLoad < 1000 else 0.001

            if len(self.master_window.forcePreview) != 0:
                for force in self.master_window.forcePreview:
                    self.master_window.drawing_area.delete(force)
                self.master_window.forcePreview.clear()
                self.master_window.drawing_area.delete(self.master_window.labelPreview)

            tipX : float = self.master_force.x + (start_pos * pcos(self.beamAngle) * 10)
            tipY : float = self.master_force.y - (start_pos * psin(self.beamAngle) * 10)

            tipX0 : float = tipX
            tipY0 : float = tipY

            for i in range(11):    
                self.master_window.forcePreview.append(self.master_window.drawing_area.create_line(tipX - 20 * uniformLoad * scale * pcos(force_angle), tipY - 20 * uniformLoad * scale * psin(force_angle), tipX, tipY, arrow = LAST, width = 4.0, activefill = "blue", smooth = True))
                tipX = tipX + (end_pos - start_pos) * pcos(self.beamAngle)
                tipY = tipY - (end_pos - start_pos) * psin(self.beamAngle)
            
            self.master_window.labelPreview = self.master_window.drawing_area.create_text((tipX + tipX0) / 2 - 40 * pcos(force_angle) if force_angle <= 180 else (tipX + tipX0) / 2, (tipY + tipY0) // 2 - 30 * (uniformLoad), font = "Helvetica", text = f"{uniformLoad} kN/m")

            self.lastRadio = 0

        if radioOption == 1:
            startLoad = int(self.distributedParameters[0].get()) if len(self.distributedParameters[0].get()) != 0 else 0
            endLoad = int(self.distributedParameters[1].get()) if len(self.distributedParameters[1].get()) != 0 else 1

            scale = 1

            if self.master_window.startLabelPreview != None and self.master_window.startLabelPreview != 0:
                self.master_window.drawing_area.delete(self.master_window.startLabelPreview)

            if len(self.master_window.forcePreview) != 0:
                for force in self.master_window.forcePreview:
                    self.master_window.drawing_area.delete(force)
                self.master_window.forcePreview.clear()
                self.master_window.drawing_area.delete(self.master_window.labelPreview)

            tipX : float = self.master_force.x + (start_pos * pcos(self.beamAngle) * 10)
            tipY : float = self.master_force.y - (start_pos * psin(self.beamAngle) * 10)
            load : int = startLoad

            tipX0 : float = tipX
            tipY0 : float = tipY

            for i in range(11):
                self.master_window.forcePreview.append(self.master_window.drawing_area.create_line(tipX - 20 * load * scale * pcos(force_angle), tipY - 20 * load * scale * psin(force_angle), tipX, tipY, arrow = LAST, width = 2.0, activefill = "blue", smooth = True))
                tipX = tipX + (end_pos - start_pos) * pcos(self.beamAngle)
                tipY = tipY - (end_pos - start_pos) * psin(self.beamAngle)
                load = load + (endLoad - startLoad) / 10
            
            if startLoad != 0:
                self.master_window.startLabelPreview = self.master_window.drawing_area.create_text(tipX0, tipY0 - 5 - 25 * startLoad, font = "Helvetica", text = f"{startLoad} kN/m")

            self.master_window.labelPreview = self.master_window.drawing_area.create_text(tipX, tipY - 5 - 25 * endLoad, font = "Helvetica", text = f"{endLoad} kN/m")

            self.lastRadio = 1

    def insertDistributed(self):
        force_angle = float(self.angleContent.get()) - self.beamAngle if len(self.angleContent.get()) != 0 else 0
        radioOption = self.radioContent.get()
        start_pos = float(self.startPosContent.get()) if len(self.startPosContent.get()) != 0 else 0
        end_pos = float(self.endPosContent.get()) if len(self.endPosContent.get()) != 0 else 5

        if radioOption == 0:
            uniformLoad = int(self.distributedParameters[0].get()) if len(self.distributedParameters[0].get()) != 0 else 1

            scale = 1 if 0 <= uniformLoad <= 10 else 0.1 if 10 < uniformLoad < 100 else 0.01 if 100 <= uniformLoad < 1000 else 0.001

            if len(self.master_window.forcePreview) != 0:
                for force in self.master_window.forcePreview:
                    self.master_window.drawing_area.delete(force)
                self.master_window.forcePreview.clear()
                self.master_window.drawing_area.delete(self.master_window.labelPreview)

            tipX : float = self.master_force.x + (start_pos * pcos(self.beamAngle) * 10)
            tipY : float = self.master_force.y - (start_pos * psin(self.beamAngle) * 10)

            tipX0 : float = tipX
            tipY0 : float = tipY
            
            forces = list()

            for i in range(11):    
                forces.append(self.master_window.drawing_area.create_line(tipX - 20 * uniformLoad * scale * pcos(force_angle), tipY - 20 * uniformLoad * scale * psin(force_angle), tipX, tipY, arrow = LAST, width = 4.0, activefill = "blue", smooth = True))
                tipX = tipX + (end_pos - start_pos) * pcos(self.beamAngle)
                tipY = tipY - (end_pos - start_pos) * psin(self.beamAngle)
            
            label = self.master_window.drawing_area.create_text((tipX + tipX0) / 2 - 40 * pcos(force_angle) if force_angle <= 180 else (tipX + tipX0) / 2, (tipY + tipY0) // 2 - 30 * (uniformLoad), font = "Helvetica", text = f"{uniformLoad} kN/m")

            self.master_window.system.beams[self.beamID - 1][0].distributedList.append((Distributed(end_pos - start_pos, Polynomial([uniformLoad])), start_pos, force_angle + self.beamAngle))
            self.master_window.actions.append(Action(related = (forces, label, self.beamID, False, 0), type = ActionType.ADD_DISTRIBUTED))

        if radioOption == 1:
            startLoad = int(self.distributedParameters[0].get()) if len(self.distributedParameters[0].get()) != 0 else 0
            endLoad = int(self.distributedParameters[1].get()) if len(self.distributedParameters[1].get()) != 0 else 1

            scale = 1

            if len(self.master_window.forcePreview) != 0:
                for force in self.master_window.forcePreview:
                    self.master_window.drawing_area.delete(force)
                self.master_window.forcePreview.clear()
                self.master_window.drawing_area.delete(self.master_window.labelPreview)

            if self.master_window.startLabelPreview != None and self.master_window.startLabelPreview != 0:
                self.master_window.drawing_area.delete(self.master_window.startLabelPreview)

            tipX : float = self.master_force.x + (start_pos * pcos(self.beamAngle) * 10)
            tipY : float = self.master_force.y - (start_pos * psin(self.beamAngle) * 10)
            load : int = startLoad

            tipX0 : float = tipX
            tipY0 : float = tipY

            forces = list()

            for i in range(11):
                forces.append(self.master_window.drawing_area.create_line(tipX - 20 * load * scale * pcos(force_angle), tipY - 20 * load * scale * psin(force_angle), tipX, tipY, arrow = LAST, width = 2.0, activefill = "blue", smooth = True))
                tipX = tipX + (end_pos - start_pos) * pcos(self.beamAngle)
                tipY = tipY - (end_pos - start_pos) * psin(self.beamAngle)
                load = load + (endLoad - startLoad) / 10
            
            startLabel = 0

            if startLoad != 0:
                startLabel = self.master_window.drawing_area.create_text(tipX0, tipY0 - 5 - 25 * startLoad, font = "Helvetica", text = f"{startLoad} kN/m")

            label = self.master_window.drawing_area.create_text(tipX, tipY - 5 - 25 * endLoad, font = "Helvetica", text = f"{endLoad} kN/m")

            self.master_window.system.beams[self.beamID - 1][0].distributedList.append((Distributed(end_pos - start_pos, Polynomial([startLoad, (endLoad - startLoad) / (end_pos - start_pos)])), start_pos, force_angle + self.beamAngle))
            self.master_window.actions.append(Action(related = (forces, label, self.beamID, startLoad != 0, startLabel), type = ActionType.ADD_DISTRIBUTED))

        for force in self.master_window.forcePreview:
            self.master_window.drawing_area.delete(force)

        self.master_window.forcePreview.clear()
        self.master_window.drawing_area.delete(self.master_window.labelPreview)

        self.master_window.inserting = False
        self.master.destroy()

    def updateMoment(self):
        magnitude = float(self.magnitudeContent.get()) if len(self.magnitudeContent.get()) != 0 else 1

        tipX : float = ((self.master_force.x + self.beamEnd.x) // 2) - 40 * pcos(self.beamAngle)
        tipY : float = ((self.master_force.y + self.beamEnd.y) // 2) 

        textAngle = self.beamAngle if 0 <= self.beamAngle < 90 else self.beamAngle - 180 if self.beamAngle > 90 else 360 + self.beamAngle if - 90 < self.beamAngle < 0 else self.beamAngle + 180
        self.master_window.drawing_area.delete(self.master_window.forcePreview)
        self.momentAsset = ImageTk.PhotoImage(Image.open("assets/arrow1.png").rotate(self.beamAngle)) if magnitude > 0 else ImageTk.PhotoImage(Image.open("assets/arrow2.png").rotate(self.beamAngle))
        self.master_window.forcePreview = self.master_window.drawing_area.create_image(tipX, tipY, image = self.momentAsset)
        self.master_window.drawing_area.delete(self.master_window.labelPreview)
        self.master_window.labelPreview = self.master_window.drawing_area.create_text(tipX + 40, tipY - 40, font = "Helvetica", text = f"{magnitude} kNm", angle = textAngle)

    def insertMoment(self):
        magnitude = float(self.magnitudeContent.get()) if len(self.magnitudeContent.get()) != 0 else 1

        tipX : float = ((self.master_force.x + self.beamEnd.x) // 2) - 40 * pcos(self.beamAngle)
        tipY : float = ((self.master_force.y + self.beamEnd.y) // 2)

        self.master_window.system.beams[self.beamID - 1][0].moment = Moment(magnitude)
        self.master_window.drawing_area.delete(self.master_window.forcePreview)
        self.master_window.drawing_area.delete(self.master_window.labelPreview)

        textAngle = self.beamAngle if 0 <= self.beamAngle < 90 else self.beamAngle - 180 if self.beamAngle > 90 else 360 + self.beamAngle if - 90 < self.beamAngle < 0 else self.beamAngle + 180
        momentAsset = ImageTk.PhotoImage(Image.open("assets/arrow1.png").rotate(self.beamAngle)) if magnitude > 0 else ImageTk.PhotoImage(Image.open("assets/arrow2.png").rotate(self.beamAngle))
        moment = self.master_window.drawing_area.create_image(tipX, tipY, image = momentAsset)
        label = self.master_window.drawing_area.create_text(tipX + 40, tipY - 40, font = "Helvetica", text = f"{magnitude} kNm", angle = textAngle)

        self.master_window.actions.append(Action(related = (moment, label, self.beamID, momentAsset), type = ActionType.ADD_MOMENT))
        self.master_window.inserting = False
        self.master.destroy()

    def updateSupport(self):
        position = self.positionContent.get()
        selectedType = self.typeContent.get()

        if self.lastType != selectedType:
            if selectedType == 0:
                self.angleLabel.grid(row = 5, column = 0, padx = 3, pady = 20)
                self.angleEntry.grid(row = 5, column = 1)
                self.degreesLabel.grid(row = 5, column = 2, padx = 0)
            else:
                self.angleLabel.grid_remove()
                self.angleEntry.grid_remove()
                self.degreesLabel.grid_remove()

        if selectedType == 0:
            angle = float(self.angleContent.get()) - self.beamAngle if len(self.angleContent.get()) != 0 else 0

            tipX : float = self.master_force.x if position == 0 else self.beamEnd.x
            tipY : float = self.master_force.y if position == 0 else self.beamEnd.y

            self.master_window.drawing_area.delete(self.master_window.forcePreview)
            self.supportAsset = ImageTk.PhotoImage(Image.open("assets/simple.png").rotate(angle))
            self.master_window.forcePreview = self.master_window.drawing_area.create_image(tipX, tipY, image = self.supportAsset)
        
        elif selectedType == 1:
            tipX : float = self.master_force.x if position == 0 else self.beamEnd.x
            tipY : float = self.master_force.y if position == 0 else self.beamEnd.y

            self.master_window.drawing_area.delete(self.master_window.forcePreview)
            self.supportAsset = PhotoImage(file = "assets/pinned.png")
            self.master_window.forcePreview = self.master_window.drawing_area.create_image(tipX, tipY, image = self.supportAsset)
        
        elif selectedType == 2:
            tipX : float = self.master_force.x if position == 0 else self.beamEnd.x
            tipY : float = self.master_force.y if position == 0 else self.beamEnd.y

            self.master_window.drawing_area.delete(self.master_window.forcePreview)
            self.supportAsset = PhotoImage(file = "assets/fixed.png")
            self.master_window.forcePreview = self.master_window.drawing_area.create_image(tipX, tipY, image = self.supportAsset)
        
    def insertSupport(self):
        position = self.positionContent.get()
        selectedType = self.typeContent.get()

        supportAsset = None
        supportInstance = None

        tipX : float = self.master_force.x if position == 0 else self.beamEnd.x
        tipY : float = self.master_force.y if position == 0 else self.beamEnd.y

        if selectedType == 0:
            angle = float(self.angleContent.get()) - self.beamAngle if len(self.angleContent.get()) != 0 else 0
            supportInstance = Support("SIMPLE", angle)
            supportAsset = ImageTk.PhotoImage(Image.open("assets/simple.png").rotate(angle))
        
        elif selectedType == 1:
            supportInstance = Support("PINNED")
            supportAsset = PhotoImage(file = "assets/pinned.png")
        
        elif selectedType == 2:
            supportInstance = Support("FIXED")
            supportAsset = supportAsset = PhotoImage(file = "assets/fixed.png")

        if position == 0:
            self.master_window.system.beams[self.beamID - 1][0].start = (supportInstance, self.master_window.system.beams[self.beamID - 1][0].start[1])
        else:
            self.master_window.system.beams[self.beamID - 1][0].end = (supportInstance, self.master_window.system.beams[self.beamID - 1][0].end[1])

        self.master_window.drawing_area.delete(self.master_window.forcePreview)
        support = self.master_window.drawing_area.create_image(tipX, tipY, image = supportAsset)

        self.master_window.actions.append(Action(related = (support, supportAsset, self.beamID, position), type = ActionType.ADD_SUPPORT))
        self.master_window.inserting = False
        self.master.destroy()

class ResultWidget:

    def __init__(self, master, name: str, beams, polynomials, polyID):
        self.master = master
        self.master.geometry(f"1360x768")
        self.master.title(name)
        
        self.canvas = Canvas(self.master, width = 1360, height = 768)
        self.canvas.pack(fill = BOTH, expand = True, side = TOP)

        for (i, beam) in enumerate(beams):
            start = Point(beam[1].x, beam[1].y)
            end = Point(beam[3].x, beam[3].y)

            self.canvas.create_line((start, end), smooth = True, width = 5, fill="#404040")

            stressFunctions = polynomials[i][0]
            endFirst = polynomials[i][1]

            length = beam[0].length
            angle = beam[2]

            tipX = start.x if not endFirst else end.x
            tipY = start.y if not endFirst else end.y

            scale = -1 

            startFactor = 1 if not endFirst else -1

            for j in range(0, 100):
                fun = stressFunctions(polyID, j * length / 100)
                print(fun)

                self.canvas.create_line(tipX, tipY, tipX, tipY + 20 * fun * scale)
                tipX += 1 / 10 * length * pcos(angle) * startFactor
                tipY += 1 / 10 * length * psin(angle) * startFactor

if __name__ == "__main__":
    root = tk.ThemedTk()
    root.set_theme("breeze")
    root.title("PEF3208 - Análise de Estruturas 2D")
    root.geometry("1360x768")
    root.iconphoto(True, PhotoImage(file = "assets/pikachu.png"))

    mainWidget : MainWidget = MainWidget(root)
    root.mainloop()
