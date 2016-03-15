from Atributo import Atributo

# -- esta lista tendria que ser dinamica --
from Angulo import Angulo
from Color import Color


def get(sensor_id, value):
    gen = (subclass for subclass in Atributo.__subclasses__() if subclass.SENSOR_ID == sensor_id)
    subclass = next(gen, None)
    if subclass is None:
        raise ValueError("No matching attribute")
    new_obj = subclass(value)
    return new_obj
