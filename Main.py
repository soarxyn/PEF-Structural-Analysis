from tkinter import *
from tkinter import ttk
from ttkthemes import themed_tk as tk
from math import atan2, degrees, tan, radians, sqrt, sin, cos, dist
from collections import deque

root = tk.ThemedTk()
root.set_theme("breeze")

class App:

    x_pos, y_pos = None, None
    x1, y1, x2, y2 = None, None, None, None
    left_button = False
    shift_press = False
    poly, arc, text, preview = None, None, None, None
    drawing_area = None
    snap_points = list()
    snap_areas = list()
    bars = deque()
    labels = deque()

    def draw_bar(self, event = None, preview = False):
        end_point = (round(event.x, 1), round(event.y, 1))
        angle : float = degrees(atan2(-round(event.y, 1) + self.y1, round(event.x, 1) - self.x1))

        if self.shift_press:
            near_snap = False 

            for point in self.snap_points:
                if dist(point, (round(event.x, 1), round(event.y, 1))) <= 40 and point != (self.x1, self.y1):
                    near_snap = True 
                    end_point = point 
                    angle = degrees(atan2(-point[1] + self.y1, point[0] - self.x1))
            
            if not near_snap:
                snap_angle = abs(angle)

                if snap_angle < (45.0 - snap_angle):
                    snap_angle = 0
                elif (snap_angle - 30) < (45 - snap_angle):
                    snap_angle = 30
                elif (snap_angle - 45) < (60 - snap_angle):
                    snap_angle = 45
                elif (snap_angle - 60) < (90 - snap_angle):
                    snap_angle = 60
                elif (snap_angle - 90) < (120 - snap_angle):
                    snap_angle = 90
                elif (snap_angle - 120) < (135 - snap_angle):
                    snap_angle = 120
                elif (snap_angle - 135) < (150 - snap_angle):
                    snap_angle = 135
                elif (snap_angle - 150) < (180 - snap_angle):
                    snap_angle = 150
                else:
                    snap_angle = 180

                angle = snap_angle if angle > 0 else -snap_angle
                end_point = (round(event.x, 1), round(event.y, 1))

        (x, y) = end_point
        pos = None
        bar = None

        if angle != 90 and angle != -90:
            pos = (self.x1, self.y1, x, self.y1 - (x - self.x1) * tan(radians(angle)))
            if preview:
                self.poly = event.widget.create_line(pos, smooth = True, dash = (10, 10))
            else:
                bar = event.widget.create_line(pos, smooth = True, width = 5, fill="#404040")
        else:
            pos = (self.x1, self.y1, self.x1, y)
            if preview:
                self.poly = event.widget.create_line(pos, smooth = True, dash = (10, 10))
            else:
                bar = event.widget.create_line(pos, smooth = True, width = 5, fill="#404040")        
        
        if bar != None:
            self.bars.append(bar)

        (x1, y1, x2, y2) = pos
        size = sqrt((x2 - x1)**2 + (y2 - y1)**2)/10

        if size > 0:
            if preview:
                self.preview = event.widget.create_text((x1 + x2) / 2 - 20 * sin(radians(angle)), (y1 + y2) / 2 - 20 * cos(radians(angle)), font = "Helvetica", text = "{0:.1f} m".format(size), angle = angle if angle > 0 else 360 + angle)
            else:
                self.labels.append(event.widget.create_text((x1 + x2) / 2 - 20 * sin(radians(angle)), (y1 + y2) / 2 - 20 * cos(radians(angle)), font = "Helvetica", text = "{0:.1f} m".format(size), angle = angle if angle > 0 else 360 + angle))

        return (angle, x2, y2)

    def lbd(self, event = None):
        self.left_button = True
        (self.x1, self.y1) = (round(round(event.x, 1), 1), round(round(event.y, 1), 1))
        (self.x_pos, self.y_pos) = (round(event.x, 1), round(event.y, 1))
        
        if len(self.snap_points) == 0:
            self.snap_points.append((round(event.x, 1), round(event.y, 1)))
        else:
            near_snap = False
            for point in self.snap_points:
                (x, y) = point 

                if sqrt((x - self.x1)**2 + (y - self.y1)**2) <= 40 and self.shift_press:
                    (self.x1, self.y1) = (x, y)
                    near_snap = True

            if not near_snap:
                self.snap_points.append((round(event.x, 1), round(event.y, 1)))
        
    def lbr(self, event = None):
        self.left_button = False 
        (self.x2, self.y2) = (round(event.x, 1), round(event.y, 1))
        
        (angle, x2, y2) = self.draw_bar(event)

        if not ((x2, y2) in self.snap_points):
            self.snap_points.append((x2, y2))

        if self.poly != None:
            event.widget.delete(self.poly)

        if self.arc != None:
            event.widget.delete(self.arc)
            
        if self.text != None:
            event.widget.delete(self.text)

        if self.preview != None:
            event.widget.delete(self.preview)

    def motion(self, event = None):
        (self.x_pos, self.y_pos) = (round(event.x, 1), round(event.y, 1))
        
        if self.poly != None:
                event.widget.delete(self.poly)

        if self.arc != None:
            event.widget.delete(self.arc)
            
        if self.text != None:
            event.widget.delete(self.text)

        if self.preview != None:
            event.widget.delete(self.preview)

        if self.left_button:            
            angle = self.draw_bar(event, True)[0]

            self.arc = event.widget.create_arc(self.x1 - 20, self.y1 - 20, self.x1 + 20, self.y1 + 20, start = 0, extent = angle)
            self.text = event.widget.create_text(self.x1 + 40, self.y1 + (20 * abs(angle) / angle) if angle != 0 else self.y1 + 20, font = "Helvetica", text = "{0:.1f}º".format(angle))
            

    def keydown(self, event = None):
        if event.keysym in ("Shift_L", "Shift_R"):
            self.shift_press = True
            
            for point in self.snap_points:
                area = self.drawing_area.create_oval(point[0] - 20, point[1] - 20, point[0] + 20, point[1] + 20, dash = (1, 2))
                self.snap_areas.append(area)
        elif event.char == "z":
            if len(self.bars) > 0:
                self.drawing_area.delete(self.bars.pop())
                self.drawing_area.delete(self.labels.pop())
        


    def keyup(self, event = None):
        if event.keysym in ("Shift_L", "Shift_R"):
            self.shift_press = False
            
            for area in self.snap_areas:
                self.drawing_area.delete(area)
            
            self.snap_areas.clear()
    
    def __init__(self, root):
        self.drawing_area = Canvas(root, width = 1280, height = 720)
        self.drawing_area.pack(fill = BOTH, expand = True)

        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.lbd)
        self.drawing_area.bind("<ButtonRelease-1>", self.lbr)
        root.bind("<KeyPress>", self.keydown)
        root.bind("<KeyRelease>", self.keyup)

root.title("PEF - Análise de Estruturas 2D")
root.geometry("1920x1080")
app = App(root)
root.mainloop()

