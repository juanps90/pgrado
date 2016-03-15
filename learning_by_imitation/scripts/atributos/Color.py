from abc import ABCMeta, abstractmethod

from Atributo import Atributo
import Const

class Color(Atributo):
    
    SENSOR_ID = Const.SENSOR_COLOR_DETECT_LINE_ID
    
    """Compara"""
    def similar(self, at2):
        return self.valor == at2.valor # tolerancia 0
	 
