from typing import Tuple
from enum import Enum
from auxiliary.algebra import Vector3

class SupportType(Enum):
  SIMPLE: Tuple = (1, 0)
  PINNED: Tuple = (2, 0)
  FIXED: Tuple = (2, 1)

class Support:
  reaction: Vector3 = Vector3(None, None, None)

  def __init__(self, name: str):
    if SupportType[name].value[0] > 1:
      self.reaction.x = 0

    if SupportType[name].value[0] > 0:
      self.reaction.y = 0

    if SupportType[name].value[1] == 1:
      self.reaction.z = 0
