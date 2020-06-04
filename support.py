from typing import Tuple
from enum import Enum
from auxiliary.algebra import Vector3

class SupportType(Enum):
  SIMPLE: Tuple = tuple(1, 0)   # tuple values are the number
  PINNED: Tuple = tuple(2, 0)   # of forces and the number
  FIXED: Tuple = tuple(2, 1)    # of moments, in that order

class Support:
  reaction: Vector3 = Vector3(None, None, None)

  def __init__(self, name: str):
    if SupportType[name].value[0] > 1:
      self.reaction.x = 0

    if SupportType[name].value[0] > 0:
      self.reaction.y = 0

    if SupportType[name].value[1] == 1:
      self.reaction.z = 0
