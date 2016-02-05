#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64, String, Float32
import Const

def processSensorLineDetectColorData(data): 
    msg = String()   
    ingreso=data.data
    #negro
    if ingreso > 0.2 and ingreso < 0.3:
        msg.data = Const.SENSOR_COLOR_DETECT_BLACK
        print "negro = ", data.data
        sensorLineDetectColorData.publish(msg)
    #blanco
    elif ingreso > 0.6 and ingreso < 0.8:
        msg.data = Const.SENSOR_COLOR_DETECT_WHITE
        print "blanco = ", data.data
        sensorLineDetectColorData.publish(msg)
    #verde
    elif ingreso > 0.4 and ingreso < 0.5:
        msg.data = Const.SENSOR_COLOR_DETECT_GREEN
        print "verde = ", data.data
        sensorLineDetectColorData.publish(msg)
    else:
        print "no Color = ", data.data

def processProximitySensorData(data):
    msg = Float64()
    msg.data = float(data.data)
    proximitySensorData.publish(msg)
    print "Distancia = ", data.data
   

if __name__ == '__main__':
    print "sensado"
    rospy.init_node('inputs', anonymous=True)
    
    #Me suscribo a datos de los sensores de vision que detectan colores en el suelo
    sensorLineDetectColorData = rospy.Publisher('sensorLineDetectedColorData', String, queue_size=50)
    rospy.Subscriber("/vrep/sensorLineDetectColorData", Float32, processSensorLineDetectColorData)
    
    #Me suscribo a datos de los sensores de distancia
    proximitySensorData = rospy.Publisher('proximitySensorData', Float64, queue_size=50)
    rospy.Subscriber("/vrep/proximitySensorData", String, processProximitySensorData)
    
    rospy.spin()

