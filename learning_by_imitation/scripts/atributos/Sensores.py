from Sensor import Sensor

# -- esta lista tendria que ser dinamica --
from HeadSensor import HeadSensor
from UltrasonicSensor import UltrasonicSensor
from LineDetect import LineDetect



def get(sensor_id, value):
    gen = (subclass for subclass in Sensor.__subclasses__() if subclass.SENSOR_ID == sensor_id)
    subclass = next(gen, None)
    if subclass is None:
        raise ValueError("No matching sensor")
    new_obj = subclass(value)
    return new_obj
