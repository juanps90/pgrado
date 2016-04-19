#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from atributos import Atributos
from Sensor import Sensor

import Const

class LineDetect(Sensor):
    
    SENSOR_ID = Const.SENSOR_COLOR_DETECT_LINE_ID
    
    """Compara"""
    def similar(self,at2):
        return Atributos.get(Const.ATR_COLOR, self.valor[1]).similar(Atributos.get(Const.ATR_COLOR, at2[1])) 
