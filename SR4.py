import gl as gl


render = gl.Renderer(1000, 1000)
render.load('./models/cube2.obj', [6 , 5, 0], [100, 100, 120])
render.glFinish('./x.bmp')
render.glFinishZ('./x2.bmp')