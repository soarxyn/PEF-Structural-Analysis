from __future__ import annotations
from typing import List, Tuple, Union
from auxiliary.algebra import Vector3, Polynomial, psin, pcos, primitive, rotate
from force import Concentrated, Distributed, Moment
from support import Support

class Beam:
  def __init__(self, length: float):
    self.length: float = length
    self.start: Tuple[Union[Support, None], List[Beam]] = (None, list())	# beam can be attached to other
    self.end: Tuple[Union[Support, None], List[Beam]] = (None, list())		# beams or to a support
    self.solved: bool = False

    self.concentratedList: List[Tuple[Concentrated, float, float]] = list()	# tuple floats are the relative
    self.distributedList: List[Tuple[Distributed, float, float]] = list()		# position and angle, in that order
    self.moment: Union[Moment, None] = None

    self.stress: Union[List[Tuple[Tuple[Polynomial, Polynomial, Polynomial], float]], None] = None

  def pointPos(self, startPos: Vector3, point: float, angle: float) -> Vector3:
    if point > self.length or point < 0:
      raise Exception('Point is outside the beam!')

    return startPos + Vector3(point*pcos(angle), point*psin(angle), 0)

  def solve(self, reaction: Vector3, angle: float, endFirst: bool) -> Vector3:
    self.stress = list()
    forces: List[Tuple[Union[Concentrated, Distributed], float, float]] = sorted(self.concentratedList + self.distributedList, key = lambda v: v[1], reverse = endFirst)

    resulting: Vector3 = -reaction if endFirst else reaction
    pos: float = self.length if endFirst else 0

    for force in forces:
      prev: float = pos
      pos = force[1]
      if isinstance(force[0], Distributed) and endFirst:
        pos += force[0].length
      self.stress.append(((Polynomial([-resulting.x]), Polynomial([resulting.y]), Polynomial([-resulting.z, resulting.y])), prev if endFirst else pos))

      resulting.z -= resulting.y*(pos - prev)
      v: Vector3
      if isinstance(force[0], Distributed):
        prev = pos
        pos -= force[0].length if endFirst else -force[0].length

        equivalent: Tuple[Concentrated, float] = force[0].equivalent(0, force[0].length)
        v = equivalent[0].forceVector(force[2])
        if endFirst:
          resulting.z += resulting.y*(prev - pos) - v.y*equivalent[1]
          resulting -= v

        t: Tuple[Distributed, Distributed] = force[0].angledComponents(force[2])

        n: Polynomial= primitive(t[0].distribution)
        n.coefficients[0] -= resulting.x
        s: Polynomial = primitive(-t[1].distribution)
        s.coefficients[0] += resulting.y
        b = primitive(Polynomial(s.coefficients.copy()))
        b.coefficients[0] -= resulting.z

        self.stress.append(((n, s, b), prev if endFirst else pos))

        if not endFirst:
          resulting.z -= resulting.y*(pos - prev) + v.y*(pos - prev - equivalent[1])
          resulting += v

      else:
        v = force[0].forceVector(force[2])
        if endFirst:
          resulting -= v
        else:
          resulting += v

    if endFirst:
      resulting.z += resulting.y*pos
      if self.start[0] != None:
        resulting -= rotate(self.start[0].reaction, -angle)

    self.stress.append(((Polynomial([-resulting.x]), Polynomial([resulting.y]), Polynomial([-resulting.z, resulting.y])), pos if endFirst else self.length))
    if endFirst:
      self.stress.reverse()

    if not endFirst:
      resulting.z -= resulting.y*(self.length - pos)
      if self.end[0] != None:
        resulting -= rotate(self.end[0].reaction, -angle)

    return -resulting if endFirst else resulting

  def stressFunction(self, polyID: int, x: float) -> float:
    p: float = 0
    for i in range(len(self.stress)):
      if x < self.stress[i][1]:
        p = self.stress[i - 1][1] if i > 0 else 0
        return self.stress[i][0][polyID](x - p)

    if len(self.stress) > 0:
      return self.stress[-1][0][polyID](x - p)
    else:
      raise Exception('Beam has not been solved yet!')
