#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Attribute
# @brief ----
# @details ----
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

from abc import ABCMeta, abstractmethod

class Attribute:
    """Clase base de Comportamiento Abstracto"""
    __metaclass__ = ABCMeta

    """Evalua las postcondiciones del comportamiento abstracto"""
    @abstractmethod
    def similar(preconds):
        pass
	
	"""Parametriza el comportamiento abstracto a partir de las condiciones"""
    def __init__(self, valor):
        self.valor = valor
    
  
