import struct
import gl as gl

class Obj(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.lines = f.read().splitlines()

        self.vertices = []
        self.tvertices = []
        self.faces = []
        self.read()

    def read(self):
        for line in self.lines:
            if line:
                try:
                    prefix, value = line.split(' ', 1)
                except:
                    prefix = ''
                if prefix == 'v':
                    self.vertices.append(list(map(float, value.split(' '))))
                if prefix == 'vt':
                    self.tvertices.append(list(map(float, value.split(' '))))                    
                elif prefix == 'f':
                    self.faces.append([list(map(int, face.split('/'))) for face in value.split(' ')])


class Texture(object):
    def __init__(self, path ):
        self.path = path
        self.pixels = []
        self.read()

    def read(self):
        image = open(self.path, "rb")
        image.seek(10)
        val = image.read(4)

        header_size = struct.unpack('=l', val)[0]

        image.seek(18)

        self.width = struct.unpack('=l', image.read(4))[0]
        self.height = struct.unpack('=l', image.read(4))[0]
        self.pixels = []

        image.seek(header_size)

        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(image.read(1))
                g = ord(image.read(1))
                r = ord(image.read(1))
                self.pixels[y].append(gl.color(r,g,b))
        image.close()

    def get_color(self, tx, ty):
        x = int(tx * self.width) - 1 
        y = int(ty * self.height) - 1
        return self.pixels[y][x]