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

    supports: List[Tuple[Vector3, Vector3]] = list() # the first vector is the reaction force from the support and the second one is its position with respect to the center of the coordinate system

    result: Vector3 = None
    r: List[float] = list()

    for beam in self.beams:
      if isinstance(beam[0].start, Support):
        supports.append((beam[0].start.reaction, beam[1]))

      if isinstance(beam[0].end, Support):
        supports.append((beam[0].end.reaction, beam[3]))


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


      i: float = 0
      for s in supports:
        if s[0].x != 0:
          coefs[0][i] = s[0].x
          coefs[2][i] = -s[1].y
          i += 1

        if s[0].y != 0:
          coefs[1][i] = s[0].y
          coefs[2][i] = s[1].x
          i += 1

        if s[0].z != 0:
          coefs[2][i] = s[0].z


      if i == 3:
        result = solve(coefs, b)
        r = [result.x, result.y, result.z]

        i = 0
        for s in supports:
          if s[0].x != 0:
            s[0].x = r[i]
            i += 1

          if s[0].y != 0:
            s[0].y = r[i]
            i += 1

          if s[0].z != 0:
            s[0].z = r[i]


      else:
        raise Exception('System is not isostatic!')
      