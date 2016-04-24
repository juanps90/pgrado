#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from Attribute import Attribute

import Const

class Angle(Attribute):

    ATT_ID = Const.ATR_ANGLE # deberia ser ATRIBUTO_ID
    
    """Compara"""
    def similar(self,at2):
        #return abs(self.valor - at2.valor ) < 0.5
	 return abs(self.valor - at2.valor ) < 0.2
