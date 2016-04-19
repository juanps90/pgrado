#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from atributos import Atributos
from Sensor import Sensor

import Const

class HeadSensor(Sensor):
    
    SENSOR_ID = Const.SENSOR_VISION_HEAD_ID
    
    """Compara"""
    def similar(self,at2):
        return Atributos.get(Const.ATR_ANGLE, self.valor[0]).similar(Atributos.get(Const.ATR_ANGLE, at2[0])) \
           and Atributos.get(Const.ATR_COLOR, self.valor[1]).similar(Atributos.get(Const.ATR_COLOR, at2[1] ))
	 
