#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from Attribute import Attribute
import Const

class Color(Attribute):

    ATT_ID = Const.ATR_COLOR
    
    """Compara"""
    def similar(self, at2):
        return self.valor == at2.valor # tolerancia 0
	 
