#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from Atributo import Atributo
import Const

class Color(Atributo):

    ATT_ID = Const.ATR_COLOR
    
    """Compara"""
    def similar(self, at2):
        return self.valor == at2.valor # tolerancia 0
	 
