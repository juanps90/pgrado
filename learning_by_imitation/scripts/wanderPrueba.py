#!/usr/bin/env python

import os 
import sys 
import sys
import time
import rospy
from std_msgs.msg import String, Int32MultiArray, Float64MultiArray
from random import randint, randrange

identify = 1
speed = 5

def publish(speedRight, speedLeft, begin, end):
    global identify
    global motores
    msg = Float64MultiArray()
    msg.data = [identify, speedRight, speedLeft]
    motores.publish(msg)
    delay = begin
    if begin < end:
        delay = randint(begin, end)
    time.sleep(delay)

def wander():
    global speed
    print speed
    publish(-3, -3, 3, 3)

    while True:
        spin = randint(0, 1)
        if spin == 0:
            # girar a la izquierda
            publish(speed/8, speed/2, 2, 6)
        else:
            # girar a la derecha
            publish(speed/2, speed/8, 2, 6)
        publish(speed, speed, 2, 6)


def processProximitySensorData(data):
    if float(data.data) < 0.4:
        publish(-3, -3, 2, 2)
    print data.data


if __name__ == '__main__':
    print "iniciando localizar"  

    rospy.init_node('wander', anonymous=True)
    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=10)
    rospy.Subscriber("/proximitySensorData", String, processProximitySensorData)

    wander()   
    # rospy.spin()

