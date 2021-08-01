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
