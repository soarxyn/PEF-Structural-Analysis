from typing import Tuple
from enum import Enum
from auxiliary.algebra import Vector3, psin, pcos

# this is an auxiliary class used for initializing the Support class's members' values
class SupportType(Enum):
	SIMPLE: Tuple = (1, 0)  # tuple values are the number
	PINNED: Tuple = (2, 0)  # of forces and the number
	FIXED: Tuple = (2, 1)   # of moments, in that order

# this is a class that defines one of three support types: simple, pinned or fixed
class Support:
	def __init__(self, name: str, angle: float = 0):
		# this member is the reaction vector from the support
		# its values are used for solving the system
		self.reaction: Vector3 = Vector3(0, 0, 0)

		if SupportType[name].value[0] > 1:
			self.reaction.x = 1
			self.reaction.y = 1
		else:
			self.reaction.x = pcos(angle)
			self.reaction.y = psin(angle)

		if SupportType[name].value[1] == 1:
			self.reaction.z = 1
