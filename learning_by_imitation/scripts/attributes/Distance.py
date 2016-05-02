#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Distance
# @brief Clase Distance usada comparar dos distancias.
# @details Clase que posee una única función destinada a comparar valores que representan distancias.
# La clase hereda de Attribute la cual posee un valor que será comparado con otro para determinar su similitud.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

from Attribute import Attribute

import Const

class Distance(Attribute):
    
    ATT_ID = Const.ATR_DIST
    
    ##
    # Compara el valor pasado por parametro con la propiedad valor heredada. Si la diferencia es menor a un umbral entonces 
    # retorna True. En caso contrario retorna False.
    # @param at2 Valor a ser comparado con la propiedad valor heredada.
    # @return Retorna True si la diferencia es menor a un umbral y False en caso contrario.
    #
    def similar(self,at2):
        return abs(self.valor - at2.valor ) < 0.08
