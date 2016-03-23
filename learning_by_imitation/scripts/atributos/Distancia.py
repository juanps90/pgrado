from abc import ABCMeta, abstractmethod
from Atributo import Atributo

import Const

class Distancia(Atributo):
    
    ATT_ID = Const.ATR_DIST
    
    """Compara"""
    def similar(self,at2):
        #return abs(self.valor - at2.valor ) < 0.1
        return abs(self.valor - at2.valor ) < 0.08
