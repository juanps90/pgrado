from abc import ABCMeta, abstractmethod
from Atributo import Atributo

import Const

class Angulo(Atributo):

    ATT_ID = Const.ATR_ANGLE # deberia ser ATRIBUTO_ID
    
    """Compara"""
    def similar(self,at2):
        #return abs(self.valor - at2.valor ) < 0.5
	 return abs(self.valor - at2.valor ) < 0.2
