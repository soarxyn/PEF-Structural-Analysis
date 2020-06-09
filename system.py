from typing import List, Tuple, Callable, Union
from auxiliary.algebra import Vector3, Polynomial, Matrix3x3, solve, rotate
from beam import Beam
from force import Concentrated, Distributed, Moment
from support import Support

class System:
  def __init__(self):
    self.beams: List[Tuple[Beam, Vector3, float, Vector3]] = list() # the tuple vectors are the beam's start and end position, respectively, with respect to the
                                                                    # center of the coordinate system, while the float is its angle with respect to the x axis

  def solveSystem(self) -> List[Tuple[Callable[[int, float], float], bool]]:
    coefs: Matrix3x3 = Matrix3x3([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    b: Vector3 = Vector3(0, 0, 0)

    supports: List[Tuple[Vector3, Vector3]] = list() # the first vector is the reaction force from the support and the second one is its position with respect to the center of the coordinate system

    result: Vector3
    r: List[float] = list()

    DFSRoot: Beam = None

    def scaleBeam(b):
      return (b[0], Vector3(b[1].x, -b[1].y, b[1].z)*0.1, b[2], Vector3(b[3].x, -b[3].y, b[3].z)*0.1)

    scaledBeams = list(map(lambda b: scaleBeam(b), self.beams.copy()))
    for beam in scaledBeams:
      if beam[0].start[0] != None:
        supports.append((beam[0].start[0].reaction, beam[1]))
        DFSRoot = beam[0]

      if beam[0].end[0] != None:
        supports.append((beam[0].end[0].reaction, beam[3]))
        DFSRoot = beam[0]


      for concentrated in beam[0].concentratedList:
        force: Vector3 = concentrated[0].forceVector(concentrated[2] - beam[2])
        pos: Vector3 = beam[0].pointPos(beam[1], concentrated[1], beam[2])
        b.x -= force.x
        b.y -= force.y
        b.z -= force.y*pos.x - force.x*pos.y

      for distributed in beam[0].distributedList:
        equivalent: Tuple[Concentrated, float] = distributed[0].equivalent(0, distributed[0].length)
        force: Vector3 = equivalent[0].forceVector(distributed[2] - beam[2])
        pos: Vector3 = beam[0].pointPos(beam[1], distributed[1] + equivalent[1], beam[2])
        b.x -= force.x
        b.y -= force.y
        b.z -= force.y*pos.x - force.x*pos.y

      if beam[0].moment != None:
        b.z -= beam[0].moment.magnitude

    i: int = 0
    for s in supports:
      coefs[0][i] = s[0].x
      coefs[2][i] = -s[0].x*s[1].y
      if s[0].x == 1 and s[0].y == 1:
        i += 1

      coefs[1][i] = s[0].y
      coefs[2][i] += s[0].y*s[1].x
      i += 1

      if s[0].z != 0:
        coefs[2][i] = s[0].z
        i += 1


    if i == 3:
      result = solve(coefs, b)
      r = [result.x, result.y, result.z]

      i = 0
      for s in supports:
        if s[0].x == 1 and s[0].y == 1:
          s[0].x *= r[i]
          i += 1
        else:
          s[0].x *= r[i]

        s[0].y *= r[i]
        i += 1

        if s[0].z != 0:
          s[0].z *= r[i]
          i += 1

    else:
      raise Exception('System is not isostatic!')
    
    solution: List[Tuple[Callable[[int, float], float], bool]] = [None]*len(self.beams)

    def solveBeamsDFS(b: Beam, p: Union[Tuple[Beam, Vector3, float], None]):
      v: Vector3 = None
      endFirst: bool = False
      i: int = 0

      for i in range(len(self.beams)):
        if b == self.beams[i][0]:
          break
        
      if b.solved:
        return

      if b.start[0] != None:
        v = rotate(b.start[0].reaction, -self.beams[i][2])
        endFirst = False
      elif b.end[0] != None:
        v = rotate(b.end[0].reaction, -self.beams[i][2])
        endFirst = True
      elif p != None:
        v = rotate(p[1], p[2] - self.beams[i][2])
        endFirst = p[0] in b.end[1]
      else:
        raise Exception('Cannot find reaction!')
      
      v = b.solve(v, endFirst)
      solution[i] = (b.stressFunction, endFirst)
      b.solved = True

      if endFirst:
        for beam in b.start[1]:
          solveBeamsDFS(beam, (b, v, self.beams[i][2]))
      else:
        for beam in b.end[1]:
          solveBeamsDFS(beam, (b, v, self.beams[i][2]))

    solveBeamsDFS(DFSRoot, None)

    return solution
