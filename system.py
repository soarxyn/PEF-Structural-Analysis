from typing import List, Tuple
from auxiliary.algebra import Vector3, Polynomial, Matrix3x3, solve
from beam import Beam
from force import Concentrated, Distributed, Moment
from support import Support

class System:
  beams: List[Tuple[Beam, Vector3, float, Vector3]] = list()  # the tuple vectors are the beam's start and end position, respectively, with respect to the
                                                              # center of the coordinate system, while the float is its angle with respect to the x axis

  def solveSystem(self):
    coefs: Matrix3x3 = Matrix3x3([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    b: Vector3 = Vector3(0, 0, 0)

    h: List[Tuple[Vector3, Vector3]] = list() # the first vector is the reaction force from the support and the second
    v: List[Tuple[Vector3, Vector3]] = list() # one is its position with respect to the center of the coordinate system
    m: List[Vector3] = list() # the vector is the reaction force from the support

    result: Vector3 = None
    r: List[float] = list()

    for beam in self.beams:
      if isinstance(beam[0].start, Support):
        reaction: Vector3 = beam[0].start.reaction
        pos: Vector3 = beam[1]
        v.append(tuple(reaction, pos))
        if reaction.x != None:
          h.append(tuple(reaction, pos))
        if reaction.z != None:
          m.append(tuple(reaction, pos))

      if isinstance(beam[0].end, Support):
        reaction: Vector3 = beam[0].end.reaction
        pos: Vector3 = beam[0].pointPos(beam[1], beam[0].length, beam[2])
        v.append(tuple(reaction, pos))
        if reaction.x != None:
          h.append(tuple(reaction, pos))
        if reaction.z != None:
          m.append(tuple(reaction, pos))


      for concentrated in beam[0].concentratedList:
        force: Vector3 = concentrated[0].forceVector(beam[2] + concentrated[2])
        pos: Vector3 = beam[0].pointPos(beam[1], concentrated[1], beam[2])
        b.x -= force.x
        b.y -= force.y
        b.z -= force.y*pos.x - force.x*pos.y

      for distributed in beam[0].distributedList:
        equivalent: Tuple[Concentrated, float] = distributed[0].equivalent()
        force: Vector3 = equivalent[0].forceVector(beam[2] + distributed[2])
        pos: Vector3 = beam[0].pointPos(beam[1], distributed[1] + equivalent[1], beam[2])
        b.x -= force.x
        b.y -= force.y
        b.z -= force.y*pos.x - force.x*pos.y

      b.z -= beam[0].moment.magnitude


      if len(h) + len(v) + len(m) == 3:
        for i in range(len(h)):
          coefs[0][i] = 1
          coefs[2][i] = -h[i][1].y

        for i in range(len(v)):
          coefs[1][len(h) + i] = 1
          coefs[2][len(h) + i] = v[i][1].x

        for i in range(len(m)):
          coefs[2][len(h) + len(v) + i] = 1


        result = solve(coefs, b)
        r = [result.x, result.y, result.z]


        for i in range(len(h)):
          h[i][0].x = r[i]

        for i in range(len(v)):
          v[i][0].y = r[len(h) + i]

        for i in range(len(m)):
          m[i][0].z = r[len(h) + len(v) + i]

      else:
        raise Exception('System is not isostatic!')
