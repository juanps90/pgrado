#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package AttributeFactory
# @brief ----
# @details ----
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

from Attribute import Attribute

# -- esta lista tendria que ser dinamica --
from Angle import Angle
from Color import Color
from Distance import Distance


def get(sensor_id, value):
    gen = (subclass for subclass in Attribute.__subclasses__() if subclass.ATT_ID == sensor_id)
    subclass = next(gen, None)
    if subclass is None:
        raise ValueError("No matching attribute")
    new_obj = subclass(value)
    return new_obj
