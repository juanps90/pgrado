#!/usr/bin/env python
# -*- coding: utf-8 -*-

from atributos import AttributeFactory
from Sensor import Sensor

import Const

class HeadSensor(Sensor):
    
    SENSOR_ID = Const.SENSOR_VISION_HEAD_ID
    
    """Compara"""
    def similar(self,at2):
        return AttributeFactory.get(Const.ATR_ANGLE, self.valor[0]).similar(AttributeFactory.get(Const.ATR_ANGLE, at2[0])) \
           and AttributeFactory.get(Const.ATR_COLOR, self.valor[1]).similar(AttributeFactory.get(Const.ATR_COLOR, at2[1] ))
	 
