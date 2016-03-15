from abc import ABCMeta, abstractmethod

#from atributos import Angulo
#from atributos import Color

class Atributo:
    """Clase base de Comportamiento Abstracto"""
    __metaclass__ = ABCMeta

    """Evalua las postcondiciones del comportamiento abstracto"""
    @abstractmethod
    def similar(preconds):
        pass
	
	"""Parametriza el comportamiento abstracto a partir de las condiciones"""
    def __init__(self, valor):
        self.valor = valor
    
  
