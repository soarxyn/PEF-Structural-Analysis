from auxiliary.algebra import *
from Barra import Barra
from Force import *
from reforcos import Reforco

barras : List[[Barra, Vector3]] = []

forcas : List[[Concentrated, Vector3]] = []
cargas : List[[Distributed, Vector3]] = []
momentos : List[[Momentum, Vector3]] = []
reforcos : List[[Reforco, Vector3]] = []

def solveSystem():
  coefs : Matrix3x3 = Matrix3x3()
  b : Vector3 = Vector3(0, 0, 0)
  res : Vector3 = Vector3()
  h : List[Vector3] = []
  v : List[Vector3] = []
  m : List[Vector3] = []
  r : List[float] = []


  for reforco in reforcos:
    v.append(reforco[0].reacao)
    if reforco[0].reacao.x != None:
      h.append(reforco[0].reacao)
    if reforco[0].reacao.z != None:
      m.append(reforco[0].reacao)

  for forca in forcas:
    b.x += forca[0].forceVector.x
    b.y += forca[0].forceVector.y
    b.z += forca[0].forceVector.x*forca[1].y + forca[0].forceVector.y*forca[1].x

  for carga in cargas:
    b.x += carga[0].equivalent.forceVector.x
    b.y += carga[0].equivalent.forceVector.y
    b.z += carga[0].equivalent.forceVector.x*carga[1].y + carga[0].equivalent.forceVector.y*carga[1].x

  for momento in momentos:
    b.z += momento.magnitude


  for i in range(len(h)):
    coefs[0][i] = 1
    coefs[2][i] = h[i].y

  for i in range(len(v)):
    coefs[1][len(h) + i] = 1
    coefs[2][len(h) + i] = v[i].x

  for i in range(len(m)):
    coefs[2][len(h) + len(v) + i] = 1


  res = solve(coefs, b)
  r = [res.x, res.y, res.z]


  for i in range(len(h)):
    h[i] = r[i]

  for i in range(len(v)):
    v[len(h) + i] = r[len(h) + 1]

  for i in range(len(m)):
    m[len(h) + len(v) + i] = r[len(h) + len(v) + i]
