from __future__ import annotations
from typing import List, Tuple, Union
import math
from auxiliary.algebra import Vector3
from force import Concentrated, Distributed, Moment
from support import Support

class Beam:
	length: float = None
	start: Union[Beam, Support] = None	# beam can be attached to other
	end: Union[Beam, Support] = None		# beams or to a support

	concentratedList: List[Tuple[Concentrated, float, float]] = []	# tuple floats are the relative
	distributedList: List[Tuple[Distributed, float, float]] = []		# position and angle, in that order
	momentList: List[Moment] = []

	def __init__(self, length: float):
		self.length = length

	def pointPos(self, startPos: Vector3, point: float, angle: float) -> Vector3:
		return startPos + Vector3(point*math.cos(angle), point*math.sin(angle), 0)

	def leftCut(self, point: float):
		left: Beam = Beam(point)

		for concentrated in self.concentratedList:
			if concentrated[1] < point:
				left.concentratedList.append(concentrated)

		for distributed in self.distributedList:
			if distributed[1] < point:
				left.distributedList.append(distributed)

		for moment in self.momentList:
			if moment[1] < point:
				left.momentList.append(moment)

		return left

	def rightCut(self, point: float):
		right: Beam = Beam(point)

		for concentrated in self.concentratedList:
			if concentrated[1] >= point:
				right.concentratedList.append(concentrated)

		for distributed in self.distributedList:
			if distributed[1] >= point:
				right.distributedList.append(distributed)

		for moment in self.momentList:
			if moment[1] >= point:
				right.momentList.append(moment)

		return right
