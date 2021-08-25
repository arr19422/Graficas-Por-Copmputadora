import gl as gl


render = gl.Renderer(1000, 1000)
render.load('./models/baymax.obj', [50, 1, 0], [10, 10, 3])
render.glFinish('./x.bmp')
render.glFinishZ('./x2.bmp')