#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Atributo import Atributo

# -- esta lista tendria que ser dinamica --
from Angulo import Angulo
from Color import Color
from Distancia import Distancia


def get(sensor_id, value):
    gen = (subclass for subclass in Atributo.__subclasses__() if subclass.ATT_ID == sensor_id)
    subclass = next(gen, None)
    if subclass is None:
        raise ValueError("No matching attribute")
    new_obj = subclass(value)
    return new_obj
