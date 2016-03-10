#!/usr/bin/env python

import sys 
from os import listdir, getenv
from os.path import isfile, join, splitext

from comportamiento import comportamiento
import importlib


def load_class(full_class_string, behaviorPath):

    sys.path.append(behaviorPath)
    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]
    module = importlib.import_module(module_path)

    return getattr(module, class_str)

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
            if issubclass(clazz, comportamiento):        
                ret.append(splitext(f)[0])
        except:
            continue                    
    
    return ret

   
