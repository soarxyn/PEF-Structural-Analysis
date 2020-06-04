from __future__ import annotations
from typing import List, Tuple
from auxiliary.algebra import Vector3, psin, pcos
from force import Concentrated, Distributed, Moment
from support import Support

class Beam:
	length: float = None
	start: Tuple[Support, List[Beam]] = tuple(None, list())	# beam can be attached to other
	end: Tuple[Support, List[Beam]] = tuple(None, list())		# beams or to a support

	concentratedList: List[Tuple[Concentrated, float, float]] = list()	# tuple floats are the relative
	distributedList: List[Tuple[Distributed, float, float]] = list()		# position and angle, in that order
	moment: Moment = None

	def __init__(self, length: float):
		self.length = length

	def pointPos(self, startPos: Vector3, point: float, angle: float) -> Vector3:
		if point > self.length or point < 0:
			raise Exception('Point is outside the beam')

		return startPos + Vector3(point*pcos(angle), point*psin(angle), 0)
