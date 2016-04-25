#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Attribute import Attribute

import Const

class Distance(Attribute):
    
    ATT_ID = Const.ATR_DIST
    
    """Compara"""
    def similar(self,at2):
        #return abs(self.valor - at2.valor ) < 0.1
        return abs(self.valor - at2.valor ) < 0.08
