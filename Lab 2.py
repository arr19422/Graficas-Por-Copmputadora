import gl as gl


render = gl.Renderer(800, 800)
render.load('./models/earth.obj', [400, 400, 0], [1, 1, 1])
# render.glFinish('./earth.bmp')
render.glFinishZ('./earth2.bmp')