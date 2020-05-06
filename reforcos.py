import enum
from auxiliary.algebra import Vector3

class TipoReforco(enum.Enum):
  APOIO : tuple = (1, 0)
  ARTICULACAO : tuple = (2, 0)
  ENGASTE : tuple = (2, 1)

class Reforco:
  def __init__(self, nome, x, y):
    self.tipo : enum = TipoReforco[nome]
    self.nome : str = self.tipo.name
    self.posicao : Vector3 = Vector3(x, y, None)
    self.forcas : int = 2 if self.tipo.value[0] > 1 else 1
    self.momentos : int = 1 if self.tipo.value[1] == 1 else 0
    self.reacao : Vector3 = Vector3(0 if self.forcas == 2 else None, 0, 0 if self.momentos == 1 else None)
