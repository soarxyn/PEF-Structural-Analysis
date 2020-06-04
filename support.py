from typing import Tuple
from enum import Enum
from auxiliary.algebra import Vector3, psin, pcos

class SupportType(Enum):
  SIMPLE: Tuple = (1, 0)   # tuple values are the number
  PINNED: Tuple = (2, 0)   # of forces and the number
  FIXED: Tuple = (2, 1)    # of moments, in that order

class Support:
  reaction: Vector3 = Vector3(0, 0, 0)

  def __init__(self, name: str, angle: float):
    if SupportType[name].value[0] > 1:
      self.reaction.x = 1
      self.reaction.y = 1
    else:
      self.reaction.x = -psin(angle)
      self.reaction.y = pcos(angle)

    if SupportType[name].value[1] == 1:
      self.reaction.z = 1
