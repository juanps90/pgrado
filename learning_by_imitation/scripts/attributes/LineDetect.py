#!/usr/bin/env python
# -*- coding: utf-8 -*-

from attributes import AttributeFactory
from Sensor import Sensor

import Const


##
# @package LineDetect
# @brief Clase LineDetect usada para evaluar similitudes entre valores de sensores de Color.
# @details Clase que posee una única función destinada a evaluar similitudes en los datos otorgados por el sensor de detección de lineas.
# La clase hereda de Sensor y compara Color.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

class LineDetect(Sensor):
    
    SENSOR_ID = Const.SENSOR_COLOR_DETECT_LINE_ID
    
    ##
    # Compara el color que se tiene en la propiedad valor con la que nos da con el valor del array pasado por parametro. Retorna True si 
    # Color es similar. En caso contrario retorna False.
    # @param at2 Array a ser comparado con la propiedad valor heredada.
    # @return Retorna True Color es similares y False en caso contrario.
    #
    def similar(self,at2):
        return AttributeFactory.get(Const.ATR_COLOR, self.valor[1]).similar(AttributeFactory.get(Const.ATR_COLOR, at2[1])) 
