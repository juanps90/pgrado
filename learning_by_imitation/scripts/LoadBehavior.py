#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package LoadBehavior
# @brief Modulo usado para listar todos los comportamientos abstractos existentes en el sistema.
# @details Para que el sistema sepa que comportamientos abstractos tiene disponibles se debe chequear las siguientes condiciones:
#   - El archivo debe estar en la carpeta behavior.
#   - Debe ser un archivo con extension py (archivo python)
#   - Debe contener una clase con nombre igual al del archivo y modulo.
#   - La clase mencionada en el punto anterior debe heredar de AbstractBehavior, por tanto deberá implementar
#       los metodos actuar, veriPosSenEjecutar, getParAprendidos y veriPosSenAprender.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

import sys 
from os import listdir, getenv
from os.path import isfile, join, splitext

from AbstractBehavior import AbstractBehavior
import importlib

##
# Retorna una instancia de la clase.
# @param full_class_string Nombre de la clase a instanciar.
# @param behaviorPath Path de la clase a instanciar.
# @return Retorna una instancia de la clase.
#  
def load_class(full_class_string, behaviorPath):
    sys.path.append(behaviorPath)
    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]
    module = importlib.import_module(module_path)

    return getattr(module, class_str)

##
# Retorna una lista con los nombres de todos los comoprtamientos abstractos disponibles, según las
# condiciones mencionadas anteriormente. Por defecto el path en donde estan los comportamientos abstractos se encuentran en
# \$HOME/catkin_ws/src/learning_by_imitation/scripts/behavior. Para indicar lo contrario debemos configurar la variable de
# entorno llamada LEARNING_BY_IMITATION_PATH.
# @return Retorna un lista con todos los comportamientos abstractos disponibles.
#  
def load_abstract_behavior():
    path = getenv('LEARNING_BY_IMITATION_PATH', getenv('HOME') + '/catkin_ws/src/learning_by_imitation/scripts') + "/behavior"
    ret = []
    only_file_py = [ 
        f for f in listdir(path)
        if (isfile(join(path, f)) and (splitext(f)[1] == ".py"))]
    for f in only_file_py:
        name = str(splitext(f)[0])
        try:
            clazz = load_class(name + '.' + name, path)
            if issubclass(clazz, AbstractBehavior):        
                ret.append(splitext(f)[0])
        except:
            continue                    
    
    return ret

   
