#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64MultiArray, Float64
from random import randint
import Const

ACTION_FORWARD = 1
ACTION_TURN_LEFT = 2
ACTION_TURN_RIGHT = 3
ACTION_BACK = 4

identify = -1
speed = 8
action = ACTION_BACK
dataSensorColor = [Const.SENSOR_COLOR_DETECT_WHITE, Const.SENSOR_COLOR_DETECT_WHITE, Const.SENSOR_COLOR_DETECT_WHITE]

def getAction(color):
    global action
    if dataSensorColor[0] == color and dataSensorColor[1] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[2] == Const.SENSOR_COLOR_DETECT_WHITE:
        action = ACTION_TURN_LEFT
        print "IZQUIERDA"
    elif dataSensorColor[0] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[1] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[2] == color:
       action = ACTION_TURN_RIGHT
       print "DERECHA"
    elif dataSensorColor[0] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[1] == color and dataSensorColor[2] == Const.SENSOR_COLOR_DETECT_WHITE:
       action = ACTION_FORWARD
       print "ADELANTE"
    elif dataSensorColor[0] == color and dataSensorColor[1] == color and dataSensorColor[2] == Const.SENSOR_COLOR_DETECT_WHITE:
       action = ACTION_TURN_LEFT
       print "IZQUIERDA"
    elif dataSensorColor[0] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[1] == color and dataSensorColor[2] == color:
       action = ACTION_TURN_RIGHT
       print "DERECHA"
    elif dataSensorColor[0] == color and dataSensorColor[1] == color and dataSensorColor[2] == color:
       action = ACTION_TURN_RIGHT
       print "DERECHA"
       
        
    
    
    

def publish(speedRight, speedLeft):
    global identify
    global motores
    msg = Float64MultiArray()
    msg.data = [identify, speedRight, speedLeft]
    motores.publish(msg)

def wander(color):
    global speed
    global action
    delay = 0
    changeTime = rospy.Time.now() + rospy.Duration(delay)
    rate = rospy.Rate(100)

    while not rospy.is_shutdown():
        getAction(color)        
        
        if action == ACTION_BACK:
            # voy hacia atras
            publish(-speed, -speed)
        elif action == ACTION_FORWARD:
            # sigo hacia adelante
            publish(speed, speed)
        elif action == ACTION_TURN_LEFT:
            # girar a la izquierda
            publish(speed/8, speed/2)
        else:
            # girar a la derecha
            publish(speed/2, speed/8)
        
        if changeTime < rospy.Time.now():
            if dataSensorColor[0] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[1] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[2] == Const.SENSOR_COLOR_DETECT_WHITE:
                if action == ACTION_FORWARD or action == ACTION_BACK:
                    if randint(0, 1) == 0:
                        action = ACTION_TURN_LEFT
                        print "IZQUIERDA"
                    else:
                        action = ACTION_TURN_RIGHT
                        print "DERECHA"
                else:
                     action = ACTION_FORWARD
                     print "ADELANTE"
            delay = randint(2, 9)
            changeTime = rospy.Time.now() + rospy.Duration(delay)
        rate.sleep()

def processSensorLineDetectedColorData(data):
    global dataSensorColor
    dataSensorColor = [data.data[1], data.data[2], data.data[3]]


def processProximitySensorData(data):
    global action
    if data.data < 0.25:
        action = ACTION_BACK
        print "ATRAS"
    #print data.data
    
if __name__ == '__main__':
    print "iniciando test de sensor de colores"  

    rospy.init_node('wander', anonymous=True)
    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=1)

    rospy.Subscriber("sensorLineDetectedColorData", Float64MultiArray, processSensorLineDetectedColorData)
    rospy.Subscriber("proximitySensorData", Float64, processProximitySensorData)
    
    wander(Const.SENSOR_COLOR_DETECT_BLACK)   
    rospy.spin()

