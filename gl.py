import struct
import random
from collections import namedtuple
import numpy as np

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])


def char(c):
    return struct.pack("=c", c.encode("ascii"))


def word(w):
    return struct.pack("=h", w)


def dword(l):
    return struct.pack("=l", l)


def color(r, g, b):
    return bytes([r, g, b])


def bbox(A, B, C):
    xs = [A.x, B.x, C.x]
    xs.sort()
    ys = [A.y, B.y, C.y]
    ys.sort()
    return xs[0], xs[-1], ys[0], ys[-1]


def cross(v0, v1):
    cx = v0.y * v1.z - v0.z * v1.y
    cy = v0.z * v1.x - v0.x * v1.z
    cz = v0.x * v1.y - v0.y * v1.x

    return V3(cx, cy, cz)


def barycentric(A, B, C, P):
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x), 
        V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )

    if cz == 0:
        return -1, -1, -1

    v = cy / cz
    u = cx / cz
    w = 1 - (cx + cy)/cz
    return w, u, v

def sub(v0,v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def length(v0):
    return (v0.x ** 2 + v0.y ** 2 + v0.z ** 2) ** 0.5

def norm(v0):
    l = length(v0)
    if l == 0:
        return V3(0,0,0)
    return V3(v0.x/l, v0.y/l, v0.z/l)

def dot(v0,v1):
    return(v0.x*v1.x + v0.y*v1.y + v0.z*v1.z)

WHITE = color(255, 255, 255)
BLACK = color(0, 0, 0)


class Renderer(object):
    def __init__(self, width, height):
        self.glInit()
        self.glCreateWindow(width, height)
        self.glClear()
        self.glClearColor(0.219,0,0)
        self.glColor(0.95,0.12,0.135)

    def glInit(self):
        self.curret_color = color(0, 0, 139)

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height

    def glClear(self):
        self.framebuffer = [
            [self.curret_color for x in range(self.width)] for y in range(self.height)
        ]
        self.zbuffer = [
            [-float('inf') for x in range(self.width)] for y in range(self.height)
        ]

    def glClearColor(self, r, g, b):
        if(r<=1 and g<=1 and b<=1):
            self.curret_color = color(int(r * 255), int(g * 255), int(b * 255))
        else:
            self.curret_color = color(r,g,b)

        self.glClear()

    def glViewPort(self, x, y):
        self.vpx = x
        self.vpy = y

    def glColor(self, r, g, b):
        if(r <= 1 and g <= 1 and b <= 1):
            self.curret_color = color(int(r * 255), int(g * 255), int(b * 255))
        else:
            self.curret_color = color(r,g,b)

    def point(self, x, y, color = None):
        try:
            self.framebuffer[int(y)][int(x)] = color or self.curret_color
        except:
            pass

    def line(self, x0, y0, x1, y1):
        x0 = int((x0 + 1) * (self.vpx / 2) + self.vpx)
        x1 = int((x1 + 1) * (self.vpx / 2) + self.vpx)
        y0 = int((y0 + 1) * (self.vpy / 2) + self.vpy)
        y1 = int((y1 + 1) * (self.vpy / 2) + self.vpy)

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

            dy = abs(y1 - y0)
            dx = abs(x1 - x0)

        offset = 0 * 2 * dx
        threshold = 0.5 * 2 * dx
        y = y0
        for x in np.arange(x0, x1, 0.1):
            if steep:

                self.point(y, x)
            else:

                self.point(x, y)

            offset += (dy / dx) * 2 * dx
            if offset >= threshold:
                y += 0.1 if y0 < y1 else -0.1
                threshold += 0.1 * 2 * dx

    def line2(self, x0, y0, x1, y1, color):
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        threshold = dx
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                self.point(y, x, color)
            else:
                self.point(x, y, color)

            offset += dy * 2
            if offset >= threshold:
                y += 1 if y0 < y1 else -1
                threshold += dx * 2

    def display(self, filename='out.bmp'):
        """
        Displays the image, a external library (wand) is used, but only for convenience during development
        """
        self.glFinish(filename)

        try:
            from wand.image import Image
            from wand.display import display

            with Image(filename=filename) as image:
                display(image)
        except ImportError:
            pass  # do nothing if no wand is installed

    def load(self, filename, movement, scale, texture=None):
        from obj import Obj
        
        model = Obj(filename)
        light = norm(V3(0,0,1))

        for face in (model.faces):
            vcount  = len(face)

            if vcount == 3:
                f1 = face[0][0]-1
                f2 = face[1][0]-1
                f3 = face[2][0]-1

                A = self.transform(model.vertices[f1],movement,scale)
                B = self.transform(model.vertices[f2], movement, scale)
                C = self.transform(model.vertices[f3], movement, scale)

                normal = norm(cross(sub(B,A),sub(C,A)))
                intensity = dot(normal, light)
                
                if not texture:
                    grey = round(255 * intensity)
                    if grey < 0:
                        continue
                    self.triangle(A, B, C, col=color(grey, grey, grey))
                else:
                    t1 = face[0][1] - 1
                    t2 = face[1][1] - 1
                    t3 = face[2][1] - 1
                    tA = V3(*model.tvertices[t1])
                    tB = V3(*model.tvertices[t2])
                    tC = V3(*model.tvertices[t3])

                    self.triangle(A, B, C, texture=texture, texture_coords=(tA, tB, tC), intensity=intensity)


            elif vcount == 4:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1   

                vertices = [
                    self.transform(model.vertices[f1], movement, scale),
                    self.transform(model.vertices[f2], movement, scale),
                    self.transform(model.vertices[f3], movement, scale),
                    self.transform(model.vertices[f4], movement, scale)
                ]

                normal = norm(cross(sub(vertices[0], vertices[1]), sub(vertices[1], vertices[2])))  # no necesitamos dos normales!!
                intensity = dot(normal, light)
                grey = round(255 * intensity)

                A, B, C, D = vertices 

                if not texture:
                    grey = round(255 * intensity)
                    if grey < 0:
                        continue
                    self.triangle(A, B, C, color(grey, grey, grey))
                    self.triangle(A, C, D, color(grey, grey, grey))            
                else:
                    t1 = face[0][1] - 1
                    t2 = face[1][1] - 1
                    t3 = face[2][1] - 1
                    t4 = face[3][1] - 1
                    tA = V3(*model.tvertices[t1])
                    tB = V3(*model.tvertices[t2])
                    tC = V3(*model.tvertices[t3])
                    tD = V3(*model.tvertices[t4])
                    
                    self.triangle(A, B, C, texture=texture, texture_coords=(tA, tB, tC), intensity=intensity)
                    self.triangle(A, C, D, texture=texture, texture_coords=(tA, tC, tD), intensity=intensity)

    def transform(self, v, translate, scale):
        return V3(
            round(((v[0] + translate[0]) * scale[0])),
            round(((v[1] + translate[1]) * scale[1])),
            round(((v[2] + translate[2]) * scale[2]))
        )

    def triangle(self, A, B, C, col = None, texture=None, texture_coords=(), intensity=1):
        xmin, xmax, ymin, ymax = bbox(A, B, C)

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    continue

                if texture:
                    tA, tB, tC = texture_coords
                    tx = tA.x * w + tB.x * v + tC.x * u
                    ty = tA.y * w + tB.y * v + tC.y * u
                    
                    ttcolor = texture.get_color(tx, ty)
                    b, g, r = [int(c * intensity) if intensity > 0 else 0 for c in ttcolor]
                    col = color(r, g, b)


                z = A.z * w + B.z * v + C.z * u

                if x < 0 or y < 0:
                    continue

                if x < len(self.zbuffer) and y < len(self.zbuffer[x]) and z > self.zbuffer[x][y]:
                    self.point(x, y, col)
                    self.zbuffer[x][y] = z

    def glFinish(self, filename):
        f = open(filename, "bw")
        # file header - 14
        f.write(char("B"))
        f.write(char("M"))
        f.write(dword(14 + 40 + 3 * (self.width * self.height)))
        f.write(dword(0))
        f.write(dword(14 + 40))

        # info header - 40
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(3 * (self.width * self.height)))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # bitmap
        for y in range(self.height):
            for x in range(self.width):
                f.write(self.framebuffer[y][x])

        f.close()

    def glFinishZ(self, filename):
        #bw means binary write
        f = open(filename, 'bw')
        #file header
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14+40+ 3*(self.width*self.height)))
        f.write(dword(0))
        f.write(dword(14+40))

        #info header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(3*(self.width*self.height)))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        z_min = float('inf')
        z_max = -float('inf')

        for x in range(self.height):
            for y in range(self.width):
                if self.zbuffer[x][y] != -float('inf'):
                    if self.zbuffer[x][y] > z_max:
                        z_max = self.zbuffer[x][y]

                    if self.zbuffer[x][y] < z_min:
                        z_min = self.zbuffer[x][y]

        for x in range(self.height):
            for y in range(self.width):
                z_value = self.zbuffer[x][y]

                if z_value == -float('inf'):
                    z_value = z_min

                z_value = round(((z_value - z_min) / (z_max - z_min)) * 255)

                z_color = color(z_value, z_value, z_value)
                f.write(z_color)

        f.close()