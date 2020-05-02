class Vec3d:
  def __init__(self, x, y, z):
    self.x : float = x
    self.y : float = y
    self.z : float = z


class Barra(object):
    forcas : Vec3d = []
    def __init__(self, comprimento, angulo, nome):
        if(comprimento > 0):
            self.comprimento : float = comprimento
        self.angulo : float = angulo
        self.nome : str = nome
        while (len(self.forcas) < comprimento + 1):
           self.forcas.append(None)
                   
    def MedeDistancia(self, ponto1, ponto2):
        if (ponto2 > ponto1):
            return ponto2 - ponto1
        else:
            return ponto1 - ponto2
                
    def CriaCorte1(self, ponto):
        comprimento1 = self.MedeDistancia(0, ponto)
        Ba =  Barra(comprimento1, self.angulo, self.nome + 'a')
        i = 0
        while (i < ponto):
            Ba.forcas[i] = self.forcas[i]
            i = i + 1
        return Ba
    def CriaCorte2(self, ponto):
        comprimento2 = self.MedeDistancia(ponto, self.comprimento)
        Bb =  Barra(comprimento2, self.angulo, self.nome + 'b')
        i = 0
        while (ponto < self.comprimento):
            Bb.forcas[i] = self.forcas[ponto]
            i = i + 1
            ponto += ponto
        return Bb
