from enum import Enum

class Vec3d:
  def __init__(self, x, y, z):
    self.x : float = x
    self.y : float = y
    self.z : float = z

class TipoReforco(Enum):
  APOIO : tuple = (1, 1, 0)
  ARTICULACAO : tuple = (2, 2, 0)
  ENGASTE : tuple = (3, 2, 1)

class Reforco:
  def __init__(self, nome):
    self.tipo : Enum = TipoReforco[nome]
    self.nome : str = self.tipo.name
    self.forcas : int = 2 if self.tipo.value[1] > 1 else 1
    self.momentos : int = 1 if self.tipo.value[2] == 1 else 0
    self.reacao : Vec3d = Vec3d(0 if self.forcas == 2 else None, 0, 0 if self.momentos == 1 else None)

if __name__ == "__main__":
  nome : str = input('Dê tipo do reforço: ')
  apoio : Reforco = Reforco(nome)
  print(f'tipo: {apoio.tipo}')
  print(f'numero de forcas: {apoio.forcas}')
  print(f'numero de momentos: {apoio.momentos}')
  print(f'modulo da forca em x: {apoio.reacao.x}')
  print(f'modulo da forca em y: {apoio.reacao.y}')
  print(f'modulo do momento em z: {apoio.reacao.z}')