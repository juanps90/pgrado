#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from atributos import Atributos
from Sensor import Sensor

import Const

class UltrasonicSensor(Sensor):
    
    SENSOR_ID = Const.SENSOR_NOSE_ULTRASONIC_ID
    
    """Compara"""
    def similar(self,at2):
        return Atributos.get(Const.ATR_DIST, self.valor[0]).similar(Atributos.get(Const.ATR_DIST, at2[0]))
	 
