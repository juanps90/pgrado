#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from AttributeFactory import AttributeFactory
from Sensor import Sensor

import Const

class UltrasonicSensor(Sensor):
    
    SENSOR_ID = Const.SENSOR_NOSE_ULTRASONIC_ID
    
    """Compara"""
    def similar(self,at2):
        return AttributeFactory.get(Const.ATR_DIST, self.valor[0]).similar(AttributeFactory.get(Const.ATR_DIST, at2[0]))
	 
