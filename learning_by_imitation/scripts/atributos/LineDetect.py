#!/usr/bin/env python
# -*- coding: utf-8 -*-

from atributos import AttributeFactory
from Sensor import Sensor

import Const

class LineDetect(Sensor):
    
    SENSOR_ID = Const.SENSOR_COLOR_DETECT_LINE_ID
    
    """Compara"""
    def similar(self,at2):
        return AttributeFactory.get(Const.ATR_COLOR, self.valor[1]).similar(AttributeFactory.get(Const.ATR_COLOR, at2[1])) 
