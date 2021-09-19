from obj import Texture
import gl as gl

r = gl.Renderer(800, 600)
t = Texture('./earth_map.bmp')
r.load('./models/earth.obj', [800, 600, 0], (0.5, 0.5, 1), texture=t)
r.display('out.bmp')