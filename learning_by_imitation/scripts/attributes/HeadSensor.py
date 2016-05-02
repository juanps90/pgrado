#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package HeadSensor
# @brief Clase HeadSensor usada para evaluar similitudes entre valores de sensores que miden angulo y color en imagen.
# @details Clase que posee una única función destinada a evaluar similitudes en los datos otorgados por el HeadSensor.
# La clase hereda de Sensor y compara Angle y Color.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

from attributes import AttributeFactory
from Sensor import Sensor

import Const

class HeadSensor(Sensor):
    
    SENSOR_ID = Const.SENSOR_VISION_HEAD_ID
    
    ##
    # Compara el angulo y color  que se tiene en la propiedad valor con la que nos da los valores del array pasado por parametro. Retorna True si tanto 
    # Angle como Color son similares. En caso contrario retorna False.
    # @param at2 Array a ser comparado con la propiedad valor heredada.
    # @return Retorna True si tanto Angle como Color son similares y False en caso contrario.
    #
    def similar(self,at2):
        return AttributeFactory.get(Const.ATR_ANGLE, self.valor[0]).similar(AttributeFactory.get(Const.ATR_ANGLE, at2[0])) \
           and AttributeFactory.get(Const.ATR_COLOR, self.valor[1]).similar(AttributeFactory.get(Const.ATR_COLOR, at2[1] ))
	 
