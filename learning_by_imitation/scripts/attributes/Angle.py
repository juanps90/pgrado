#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Angle
# @brief Clase Angle usada comparar dos angulos.
# @details Clase que posee una única función destinada a comparar valores que representan angulos.
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

class Angle(Attribute):

    ATT_ID = Const.ATR_ANGLE # deberia ser ATRIBUTO_ID
    
    ##
    # Compara el valor pasado por parametro con la propiedad valor heredada. Si la diferencia es menor a un umbral entonces 
    # retorna True. En caso contrario retorna False.
    # @param at2 Valor a ser comparado con la propiedad valor heredada.
    # @return Retorna True si la diferencia es menor a un umbral y False en caso contrario.
    #    
    def similar(self,at2):
	 return abs(self.valor - at2.valor ) < 0.2
