from __future__ import annotations
from typing import List, Tuple, Union
from auxiliary.algebra import Vector3, Polynomial, psin, pcos, integrate
from force import Concentrated, Distributed, Moment
from support import Support

class Beam:
	def __init__(self, length: float):
		self.length: float = length
		self.start: Tuple[Support, List[Beam]] = (None, list())	# beam can be attached to other
		self.end: Tuple[Support, List[Beam]] = (None, list())		# beams or to a support

		self.concentratedList: List[Tuple[Concentrated, float, float]] = list()	# tuple floats are the relative
		self.distributedList: List[Tuple[Distributed, float, float]] = list()		# position and angle, in that order
		self.moment: Moment = None

		self.stress: Tuple[List[Tuple[Tuple[Polynomial, Polynomial, Polynomial], float]], bool] = None

	def pointPos(self, startPos: Vector3, point: float, angle: float) -> Vector3:
		if point > self.length or point < 0:
			raise Exception('Point is outside the beam!')

		return startPos + Vector3(point*pcos(angle), point*psin(angle), 0)

	def solve(self, reaction: Vector3, endFirst: bool):
		self.stress = (list(), endFirst)
		forces: List[Tuple[Union[Concentrated, Distributed], float, float]] = sorted(self.concentratedList + self.distributedList, key = lambda v: v[1], reverse = endFirst)

		resulting: Vector3 = -reaction if endFirst else reaction
		pos: float = 0

		for force in forces:
			prev: float = pos
			pos = self.length - force[1] if endFirst else force[1]
			self.stress[0].append(((Polynomial([-resulting.x]), Polynomial([resulting.y]), Polynomial([-resulting.z, resulting.y])), pos))

			resulting.z -= resulting.y*abs(pos - prev)
			v: Vector3
			if isinstance(force[0], Distributed):
				prev = pos
				pos += force[0].length

				t: Tuple[Distributed, Distributed] = force[0].angledComponents(force[2])
				n: Polynomial
				s: Polynomial
				if endFirst:
					n = -t[0].distribution
					s = t[1].distribution
				else:
					n = t[0].distribution
					s = -t[1].distribution

				b: Polynomial = Polynomial(s.coefficients.copy())
				b.coefficients.insert(0, 0)
				b.degree = s.degree + 1

				n.coefficients.append(-resulting.x)
				s.coefficients.append(resulting.y)
				b.coefficients.append(-resulting.z)

				self.stress[0].append(((n, s, b), pos))

				equivalent: Tuple[Concentrated, float] = force[0].equivalent(0, force[0].length)
				v = equivalent[0].forceVector(force[2])

				resulting.z -= v.y*abs(pos - prev - equivalent[1])

			else:
				v = force[0].forceVector(force[2])

			if endFirst:
				resulting -= v
			else:
				resulting += v

		self.stress[0].append(((Polynomial([-resulting.x]), Polynomial([resulting.y]), Polynomial([-resulting.z, resulting.y])), self.length))

	def stressFunction(self, polyID: int, x: float) -> float:
		if self.stress == None:
			raise Exception('Beam yet to be solved!')

		for i in range(len(self.stress[0])):
			if x <= self.stress[0][i][1]:
				p: float = self.stress[0][i - 1][1] if i > 0 else 0
				f: Tuple[Polynomial, Polynomial, Polynomial] = self.stress[0][i][0]
				if f[0].degree > 0:
					return f[polyID].coefficients[f[polyID].degree + 1] + integrate(f[polyID], abs(x - p), abs(self.stress[0][i][1] - p)) if self.stress[1] else f[polyID].coefficients[f[polyID].degree + 1] + integrate(f[polyID], 0, abs(x - p))
				else:
					return f[polyID](abs(x - p))

		raise Exception('x out of range!')
