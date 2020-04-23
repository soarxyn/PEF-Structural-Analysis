import enum

class Vec3d:
  def __init__(self, x, y, z):
    self.x : float = x
    self.y : float = y
    self.z : float = z

class Reforco:
  _tipos : enum.Enum = enum.Enum('tipo', 'apoio articulacao engaste')
  def __init__(self, tipo):
    self.tipo : str = tipo
    self.reacao : Vec3d = Vec3d(0 if self._tipos[tipo].value > 1 else None, 0, 0 if self._tipos[tipo].value == 3 else None)

if __name__ == "__main__":
  apoio = Reforco('engaste')
  print(apoio.tipo)
  print(apoio.reacao.x)
  print(apoio.reacao.y)
  print(apoio.reacao.z)