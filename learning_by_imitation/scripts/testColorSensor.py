#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64MultiArray, Float64, String
from random import randint
import Const

identify = 1
speed = 8
crash = False

def publish(speedRight, speedLeft):
    global identify
    global motores
    msg = Float64MultiArray()
    msg.data = [identify, speedRight, speedLeft]
    motores.publish(msg)

def wander():
    global speed
    global crash
    spin = 0
    delay = 0
    hasFollow = False
    changeTime = rospy.Time.now() + rospy.Duration(delay)
    rate = rospy.Rate(100)

    while not rospy.is_shutdown():
        if crash:
            # voy hacia atras
            publish(-speed, -speed)
        elif hasFollow:
            # sigo hacia adelante
            publish(speed, speed)
        elif spin == 0:
            # girar a la izquierda
            publish(speed/8, speed/2)
        else:
            # girar a la derecha
            publish(speed/2, speed/8)
        
        if changeTime < rospy.Time.now():
            hasFollow = not hasFollow
            spin = randint(0, 1)
            delay = randint(2, 9)
            changeTime = rospy.Time.now() + rospy.Duration(delay)
            crash = False
            
        rate.sleep()

def processSensorLineDetectedColorData(data):
    global speed
    if data.data == Const.SENSOR_COLOR_DETECT_BLACK:
        speed = 12
    elif data.data == Const.SENSOR_COLOR_DETECT_GREEN:
        speed = 5
    print data.data

def processProximitySensorData(data):
    global crash
    crash = data.data < 0.25

    print data.data
    
if __name__ == '__main__':
    print "iniciando test de sensor de colores"  

    rospy.init_node('wander', anonymous=True)
    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=1)

    rospy.Subscriber("sensorLineDetectedColorData", String, processSensorLineDetectedColorData)
    rospy.Subscriber("proximitySensorData", Float64, processProximitySensorData)
    
    wander()   
    rospy.spin()

