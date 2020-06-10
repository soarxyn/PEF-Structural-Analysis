from typing import List, Tuple, Callable, Union
from auxiliary.algebra import Vector3, Polynomial, Matrix3x3, solve, rotate
from beam import Beam
from force import Concentrated, Distributed, Moment
from support import Support

class System:
	def __init__(self):
		self.beams: List[Tuple[Beam, Vector3, float, Vector3]] = list()	# the tuple vectors are the beam's start and end position, respectively, with respect to the
																																		# center of the coordinate system, while the float is its angle with respect to the x axis

	def solveSystem(self) -> List[Callable[[int, float], float]]:
		coefs: Matrix3x3 = Matrix3x3([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
		b: Vector3 = Vector3(0, 0, 0)

		supports: List[Tuple[Vector3, Vector3]] = list()	# the first vector is the reaction force from the support and the second one is its position with respect to the center of the coordinate system

		def scaleBeam(b):
			return (b[0], Vector3(b[1].x, -b[1].y, b[1].z)*0.1, b[2], Vector3(b[3].x, -b[3].y, b[3].z)*0.1)

		scaledBeams = list(map(lambda b: scaleBeam(b), self.beams.copy()))
		for beam in scaledBeams:
			if beam[0].start[0] != None:
				supports.append((beam[0].start[0].reaction, beam[1]))

			if beam[0].end[0] != None:
				supports.append((beam[0].end[0].reaction, beam[3]))

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
			result: Vector3 = solve(coefs, b)
			r: List[float, float, float] = [result.x, result.y, result.z]

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

		solution: List[Callable[[int, float], float]] = [None]*len(self.beams)

		def findReaction(b: Beam, p: Union[Beam, None]) -> Tuple[Vector3, float]:	# tuple float is the beam's angle
			v: Vector3 = Vector3(0, 0, 0)
			endFirst: bool
			for i in range(len(self.beams)):
				if b == self.beams[i][0]:
					break

			if len(b.start[1]) == 0:
				endFirst = False
				if b.start[0] != None:
					v = rotate(b.start[0].reaction, -self.beams[i][2])
			elif len(b.end[1]) == 0:
				endFirst = True
				if b.end[0] != None:
					v = rotate(b.end[0].reaction, -self.beams[i][2])
			elif p != None:
				if p in b.start[1]:
					endFirst = True
					for c in b.end[1]:
						r: Tuple[Vector3, float] = findReaction(c, b)
						v += rotate(r[0], r[1] - self.beams[i][2])
				elif p in b.end[1]:
					endFirst = False
					for c in b.start[1]:
						r: Tuple[Vector3, float] = findReaction(c, b)
						v += rotate(r[0], r[1] - self.beams[i][2])
				else:
					raise Exception('Cannot find parent!')
			else:
				raise Exception('Parent not given!')

			v = b.solve(v, self.beams[i][2], endFirst)
			solution[i] = b.stressFunction
			return (v, self.beams[i][2])

		for b in self.beams:
			if len(b[0].start[1]) == 0 or len(b[0].end[1]) == 0:
				findReaction(b[0], None)
				for beam in b[0].start[1]:
					findReaction(beam, b[0])
				for beam in b[0].end[1]:
					findReaction(beam, b[0])
				break

		return solution
