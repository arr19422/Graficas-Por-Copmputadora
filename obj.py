import struct
import gl as gl

class Obj(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.lines = f.read().splitlines()

        self.vertices = []
        self.faces = []
        self.read()

    def read(self):
        for line in self.lines:
            if line:
                if len(line) < 2:
                    pass
                else:
                    prefix, value = line.split(' ', 1)
                    prefix = prefix.strip()
                    value = value.strip()
                    if prefix == "v":
                        self.vertices.append(list(map(float, value.split(" "))))
                    elif prefix == "f":
                        try:
                            self.faces.append(
                                [list(map(int, face.split("/"))) for face in value.split(" ")]
                            )
                        except:
                            self.faces.append(
                                [list(map(int, face.split("//"))) for face in value.split(" ")]
                            )


class Texture(object):
    def __init__(self, path ):
        self.path = path
        self.pixels = []
        self.read()

    def read(self):
        image = open(self.path, "br")

        val = image.read(4)
        header_size = struct.unpack('=1', image)[0]

        image.seek(18)
        self.width = struct.unpack('=1', image.read(4))[0]
        self.height = struct.unpack('=1', image.read(4))[0]

        image.seek(header_size)

        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(image.read(1))
                g = ord(image.read(1))
                r = ord(image.read(1))
                self.pixels[y].append(gl.color(r, g, b))

# t = Texture('/.tex.bmp')
# t.read()

render = gl.Renderer(1000, 1000)
render.load('./models/cube2.obj', [6 , 5, 0], [100, 100, 120])
render.glFinish('./x.bmp')
render.glFinishZ('./x2.bmp')

