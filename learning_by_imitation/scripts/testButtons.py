#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String
import Const

def processCommand(data):
    msg = String()
    if data.data == "INIT_LEARNING":
        msg.data = str(Const.COMMAND_INIT_LEARNING)
    elif data.data == "END_LEARNING":
        msg.data = str(Const.COMMAND_END_LEARNING)
    elif data.data == "PLAY":
        msg.data = str(Const.COMMAND_PLAY)
    elif data.data == "STOP":
        msg.data = str(Const.COMMAND_STOP)
    elif data.data == "BAD":
        msg.data = str(Const.COMMAND_BAD)
    command.publish(msg)
    print data.data

if __name__ == '__main__':
    print "Prueba commandos"
    rospy.init_node('testButtons', anonymous=True)
    
    #Me suscribo a datos de los commandos
    rospy.Subscriber("/vrep/command", String, processCommand)
    command = rospy.Publisher('topic_command', String, queue_size=10)
    rospy.spin()
    


