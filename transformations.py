from numpy import *
from gl import *

r = Renderer(1000, 1000)

def line(A, B, color=WHITE):
  x0, y0, x1, y1 = A.x, A.y, B.x, B.y
  dy = y1 - y0
  dx = x1 - x0

  desc = (dy*dx) < 0

  dy = abs(dy)
  dx = abs(dx)

  steep = dy > dx

  if steep:
      x0, y0 = y0, x0
      x1, y1 = y1, x1

      dy = abs(y1 - y0)
      dx = abs(x1 - x0)

  if desc and (y0 < y1):
      y0, y1 = y1, y0
  elif (not desc) and (y1 < y0):
      y0, y1 = y1, y0

  if (x1 < x0):
      x1, x0 = x0, x1

  offset = 0
  threshold = dx
  y = y0

  # y = mx + b
  points = []
  for x in range(int(x0), int(x1+1)):
      if steep:
          points.append((y, x))
      else:
          points.append((x, y))

      try:
          div = dy/dx
      except:
          div = 0
      offset += div * 2 * dx

      if offset >= threshold:
          y += 1 if y0 < y1 else -1
          threshold += 1 * 2 * dx

  for point in points:
    x = point[1]
    y = point[0]
    r.point(x, y, color)

points = [
  [200.0, 200.0],
  [400.0, 200.0],
  [400.0, 400.0],
  [200.0, 400.0]
]

center = V3(300, 300)

a = 3.14 / 4


move_to_origin = matrix([
  [1, 0, -center.x],
  [0, 1, -center.y],
  [0, 0, 1]
])


rotation_matrix = matrix([
  [cos(a), -sin(a), 0],
  [sin(a), cos(a), 0],
  [0, 0, 1]
])

identity_matrix = matrix([
  [1, 0, 0],
  [0, 1, 0],
  [0, 0, 1]
])


move_back = matrix([
  [1, 0, center.x],
  [0, 1, center.y],
  [0, 0, 1]
])

transform_matrix = move_back @ identity_matrix @ move_to_origin

transformed_points = []

for point in points:
  point = V3(*point)
  tpoint = transform_matrix @ [ point.x, point.y, 1]
  tpoint = tpoint.tolist()[0]

  tpoint2D = V3(
    int(tpoint[0]/tpoint[2]),
    int(tpoint[1]/tpoint[2])
  )

  transformed_points.append(tpoint2D)



point = transformed_points[-1]
prev_point = V3(point[0], point[1])
for point in transformed_points:
  print(point)
  line(prev_point, point)
  prev_point = point

point = points[-1]
prev_point = V3(int(point[0]), int(point[1]))
for point in points:
  point = V3(int(point[0]), int(point[1]))
  line(prev_point, point, color(255, 0, 255))
  prev_point = point


r.write('t.bmp')