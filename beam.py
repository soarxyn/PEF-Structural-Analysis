from __future__ import annotations
from typing import List, Tuple, Callable
from collections import namedtuple
from auxiliary.algebra import Vector3, Polynomial, psin, pcos, integrate
from force import Concentrated, Distributed, Moment
from support import Support

StressFunctions = namedtuple("StressFunctions", ("normal", "shear", "bending"))

class Beam:
	def __init__(self, length: float):
		self.length: float = length
		self.start: Tuple[Support, List[Beam]] = (None, list())	# beam can be attached to other
		self.end: Tuple[Support, List[Beam]] = (None, list())		# beams or to a support

		self.concentratedList: List[Tuple[Concentrated, float, float]] = list()	# tuple floats are the relative
		self.distributedList: List[Tuple[Distributed, float, float]] = list()		# position and angle, in that order
		self.moment: Moment = None

	def pointPos(self, startPos: Vector3, point: float, angle: float) -> Vector3:
		if point > self.length or point < 0:
			raise Exception('Point is outside the beam!')

		return startPos + Vector3(point*pcos(angle), point*psin(angle), 0)

	def solve(self, reaction: Vector3, endFirst: bool) -> StressFunctions:
		forces : List = sorted(self.concentratedList + self.distributedList, key = lambda v: v[1], reverse = endFirst)

		resulting: Vector3 = -reaction if endFirst else reaction
		pos: float = 0

		stress: List[Tuple[Tuple[Polynomial, Polynomial, Polynomial], float]] = list()

		for force in forces:
			prev: float = pos
			pos = self.length - force[1] if endFirst else force[1]
			stress.append(((Polynomial([-resulting.x]), Polynomial([resulting.y]), Polynomial([-resulting.z, resulting.y])), pos))

			resulting.z -= resulting.y*abs(pos - prev)
			v: Vector3
			if isinstance(force[0], Distributed):
				pos -= force[0].length if endFirst else -force[0].length
				a: Tuple[Distributed, Distributed] = force[0].angledComponents(force[2])
				a[0].distribution.coefficients[0] -= resulting.x
				a[1].distribution.coefficients[0] += resulting.y
				b: Tuple[Polynomial, Polynomial] = (-a[0].distribution, -a[1].distribution) if endFirst else (a[0].distribution, a[1].distribution)

				stress.append(((-b[0], b[1], Polynomial([-resulting.z])), pos))

				equivalent: Tuple[Concentrated, float] = force[0].equivalent(0, force[0].length)
				v = equivalent[0].forceVector(force[2])

				resulting.z += v.y*abs(pos - prev - equivalent[1])

			else:
				v = force[0].forceVector(force[2])

			if endFirst:
				resulting -= v
			else:
				resulting += v

		def normal(x: float) -> float:
			d: int = 0
			for i in range(len(stress)):
				if x < stress[i][1]:
					p: float = stress[i - 1][1] if i > 0 else 0
					d = i + d
					if d < len(forces):
						if isinstance(forces[d][0], Distributed):
							return integrate(stress[i][0][0], abs(x - p), forces[d][0].length) if endFirst else integrate(stress[i][0][0], 0, abs(x - p))

					else:
						return stress[i][0][0](abs(x - p))

				if isinstance(forces[i + d][0], Distributed):
					d += 1

			return -resulting.x

		def shear(x:float) -> float:
			d: int = 0
			for i in range(len(stress)):
				if x < stress[i][1]:
					p: float = stress[i - 1][1] if i > 0 else 0
					d = i + d
					if d < len(forces):
						if isinstance(forces[d][0], Distributed):
							return integrate(stress[i][0][1], abs(x - p), forces[d][0].length) if endFirst else integrate(stress[i][0][1], 0, abs(x - p))

					else:
						return stress[i][0][1](abs(x - p))

				if isinstance(forces[i + d][0], Distributed):
					d += 1

			return resulting.y

		def bending(x: float) -> float:
			d: int = 0
			for i in range(len(stress)):
				if x < stress[i][1]:
					p: float = stress[i - 1][1] if i > 0 else 0
					d = i + d
					if d < len(forces):
						if isinstance(forces[d][0], Distributed):
							e: Tuple[Concentrated, float] = forces[d][0].equivalent(abs(x - p), forces[d][0].length) if endFirst else forces[d][0].equivalent(0, abs(x - p))
							return stress[i][0][2](abs(x - p)) + e[0].y*e[1] if endFirst else stress[i][0][2][0] + e[0].y*abs(x - p - e[1])

					else:
						return stress[i][0][2](abs(x - p))

				if isinstance(forces[i + d][0], Distributed):
					d += 1

			return resulting.y*(abs(x - pos)) - resulting.z

		return (normal, shear, bending)