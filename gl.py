import struct
import numpy as np


def char(c):
    return struct.pack("=c", c.encode("ascii"))


def word(w):
    return struct.pack("=h", w)


def dword(l):
    return struct.pack("=l", l)


def color(r, g, b):
    return bytes([r, g, b])


WHITE = color(255, 255, 255)
BLACK = color(0, 0, 0)


class Renderer(object):
    def __init__(self, width, height):
        self.glInit()
        self.glCreateWindow(width, height)
        self.glViewPort(800, 600)
        self.glClear()
        self.glClearColor(0, 0, 0)
        self.glColor(1, 1, 1)

    def glInit(self):
        self.curret_color = WHITE

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height

    def glClear(self):
        self.framebuffer = [
            [self.curret_color for x in range(self.width)] for y in range(self.height)
        ]

    def glClearColor(self, r, g, b):
        self.curret_color = color(int(r * 255), int(g * 255), int(b * 255))
        self.glClear()

    def glViewPort(self, x, y):
        self.vpx = x
        self.vpy = y

    def glColor(self, r, g, b):
        self.curret_color = color(int(r * 255), int(g * 255), int(b * 255))

    def write(self, filename):
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

    def glFinish(self):
        self.write("x.bmp")

    def point(self, x, y, color):
        try:
            self.framebuffer[int(y)][int(x)] = color
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

    def load(self, filename, translate, scale):
        from obj import Obj
        model = Obj(filename)

        for face in model.faces:
            vcount = len(face)

            for j in range(vcount):
                f1 = face[j][0]
                f2 = face[(j + 1) % vcount][0]

                v1 = model.vertices[f1 - 1]
                v2 = model.vertices[f2 - 1]

                x1 = round((v1[0] + translate[0]) * scale[0])
                y1 = round((v1[1] + translate[1]) * scale[1])
                x2 = round((v2[0] + translate[0]) * scale[0])
                y2 = round((v2[1] + translate[1]) * scale[1])

                self.line2(x1, y1, x2, y2, self.curret_color)

    def fill(self, polygon, color):
        polygon = [list(pol) for pol in polygon]
        xmax = max(map(lambda x: x[0], polygon))
        xmin = min(map(lambda x: x[0], polygon))
        ymax = max(map(lambda x: x[1], polygon))
        ymin = min(map(lambda x: x[1], polygon))
        dy = round((ymax + ymin) / 2)
        dx = round((xmax + xmin) / 2)
        countx = xmax
        county = ymax
        while dx < countx and dy < county:
            for i in range(0, len(polygon)):
                if i == (len(polygon)-1):
                    self.line2(polygon[i][0], polygon[i][1], polygon[0][0], polygon[0][1], color)

                else:
                    self.line2(polygon[i][0], polygon[i][1], polygon[i+1][0], polygon[i+1][1], color)

                if polygon[i][0] > dx:
                    polygon[i][0] -= 1
                elif polygon[i][0] < dx:
                    polygon[i][0] += 1


                if polygon[i][1] > dy:
                    polygon[i][1] -= 1
                elif polygon[i][1] < dy:
                    polygon[i][1] += 1


            if countx > dx:
                countx -= 1
            if county > dy:
                county -= 1
        pass