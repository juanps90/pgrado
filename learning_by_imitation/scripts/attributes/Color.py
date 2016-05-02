#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Color
# @brief Clase Color usada comparar dos colores.
# @details Clase que posee una única función destinada a comparar valores que representan colores.
# La clase hereda de Attribute la cual posee un valor que será comparado con otro para determinar su similitud.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

from abc import ABCMeta, abstractmethod
from Attribute import Attribute
import Const

class Color(Attribute):

    ATT_ID = Const.ATR_COLOR
    
    ##
    # Compara el valor pasado por parametro con la propiedad valor heredada. Si son iguales entonces 
    # retorna True. En caso contrario retorna False.
    # @param at2 Valor a ser comparado con la propiedad valor heredada.
    # @return Retorna True si los valores son iguales y False en caso contrario.
    #    
    def similar(self, at2):
        return self.valor == at2.valor # tolerancia 0
	 
