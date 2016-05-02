#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package UltrasonicSensor
# @brief Clase UltrasonicSensor usada para evaluar similitudes entre valores de sensores de ultrasonido.
# @details Clase que posee una única función destinada a evaluar similitudes en los datos de sensores ultrasonicos.
# La clase hereda de Sensor compara Distances.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

from attributes import AttributeFactory
from Sensor import Sensor

import Const

class UltrasonicSensor(Sensor):
    
    SENSOR_ID = Const.SENSOR_NOSE_ULTRASONIC_ID
    
    ##
    # Compara la distancia que se tiene en la propiedad valor con el valor del array pasado por parametro. Retorna True si 
    # distania es similar. En caso contrario retorna False.
    # @param at2 Array a ser comparado con la propiedad valor heredada.
    # @return Retorna True Distance es similares y False en caso contrario.
    #
    def similar(self,at2):
        return AttributeFactory.get(Const.ATR_DIST, self.valor[0]).similar(AttributeFactory.get(Const.ATR_DIST, at2[0]))
	 
