#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    
  
