from abc import ABCMeta, abstractmethod
from Atributo import Atributo

import Const

class Angulo(Atributo):
    
    SENSOR_ID = -1 # deberia ser ATRIBUTO_ID
    
    """Compara"""
    def similar(self,at2):
        return abs(self.valor - at2.valor ) < 5.0 # tolerancia 5
	 
