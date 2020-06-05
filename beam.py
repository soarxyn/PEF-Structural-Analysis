from __future__ import annotations
from functools import partial
from typing import List, Tuple, Callable
from auxiliary.algebra import Vector3, Polynomial, psin, pcos, integrate
from force import Concentrated, Distributed, Moment
from support import Support

class Beam:
	length: float = None
	start: Tuple[Support, List[Beam]] = (None, list())	# beam can be attached to other
	end: Tuple[Support, List[Beam]] = (None, list())		# beams or to a support

	concentratedList: List[Tuple[Concentrated, float, float]] = list()	# tuple floats are the relative
	distributedList: List[Tuple[Distributed, float, float]] = list()		# position and angle, in that order
	moment: Moment = None

	stress: List[Tuple[Tuple[Polynomial, Polynomial, Polynomial], float]] = list()

	def __init__(self, length: float):
		self.length = length

	def pointPos(self, startPos: Vector3, point: float, angle: float) -> Vector3:
		if point > self.length or point < 0:
			raise Exception('Point is outside the beam!')

		return startPos + Vector3(point*pcos(angle), point*psin(angle), 0)

	def solve(self, reaction: Vector3, endFirst: bool) -> List[Tuple[Tuple[Callable[[float], float], Callable[[float], float], Callable[[float], float]], float]]:
		forces: List = (self.concentratedList + self.distributedList).sort(key = lambda v: v[1], reverse = endFirst)
		resulting: Vector3 = -reaction if endFirst else reaction
		pos: float = None

		for force in forces:
			pos = self.length - force[1] if endFirst else force[1]
			self.stress.append(((Polynomial([-resulting.x]), Polynomial([resulting.y]), Polynomial([-resulting.z, resulting.y])), pos))

			v: Vector3 = None
			if isinstance(force[0], Distributed):
				pos -= force[0].length if endFirst else -force[0].length
				a: Tuple[Polynomial, Polynomial] = force[0].angledComponents(force[2])
				a[0][0] -= resulting.x
				a[1][0] += resulting.y
				if endFirst:
					a = (-a[0], -a[1])

				self.stress.append(((-a[0], a[1], Polynomial(-resulting.z)), pos))

				equivalent: Tuple[Concentrated, float] = force[0].equivalent(0, force[0].length)
				v = equivalent[0].forceVector(force[2])

				resulting += v.y*equivalent[1]

			else:
				v = force[0].forceVector(force[2])

			if endFirst:
				resulting -= v
			else:
				resulting += v


		def normal(p: float, x: float) -> float:
			d: float = 0
			for i in range(self.stress):
				if isinstance(forces[i + d][0], Distributed):
					d += 1
				if abs(x - p) < self.stress[i][1]:
					if isinstance(forces[i + d - 1][0], Distributed):
						d = i + d - 1
						return integrate(self.stress[i][0][0], abs(x - p), forces[d][0].length) if endFirst else integrate(self.stress[i][0][0], 0, abs(x - p))

					else:
						return self.stress[i][0][0][0]

			return -resulting.x

		def shear(p: float, x:float) -> float:
			d: float = 0
			for i in range(self.stress):
				if isinstance(forces[i + d][0], Distributed):
					d += 1
				if abs(x - p) < self.stress[i][1]:
					if isinstance(forces[i + d - 1][0], Distributed):
						d = i + d - 1
						return integrate(self.stress[i][0][1], abs(x - p), forces[d][0].length) if endFirst else integrate(self.stress[i][0][1], 0, abs(x - p))

					else:
						return self.stress[i][0][1][0]

			return resulting.y

		def bending(p: float, x: float) -> float:
			d: float = 0
			for i in range(self.stress):
				if isinstance(forces[i + d][0], Distributed):
					d += 1
				if abs(x - p) < self.stress[i][1]:
					if isinstance(forces[i + d - 1][0], Distributed):
						d = i + d - 1
						e: Tuple[Concentrated, float] = forces[d][0].equivalent(abs(x - p), forces[d][0].length) if endFirst else forces[d][0].equivalent(0, abs(x - p))
						return self.stress[i][0][2][0] + e[0].y*abs(x - p - e[1])

					else:
						return self.stress[i][0][2][0]

			return resulting.y*abs(x - p) - resulting.z


		r: List[Tuple[Callable[[float], float], Callable[[float], float], Callable[[float], float]], float] = list()

		pNormal: Callable[[float], float] = partial(normal, 0)
		pShear: Callable[[float], float] = partial(shear, 0)
		pBending: Callable[[float], float] = partial(bending, 0)

		for i in range(self.stress):
			r.append(((pNormal, pShear, pBending), self.stress[i][1]))
			pNormal = partial(normal, self.stress[i][1])
			pShear = partial(shear, self.stress[i][1])
			pBending = partial(bending, self.stress[i][1])

		
		r.append(((pNormal, pShear, pBending), self.stress[len(self.stress) - 1][1]))

		return r