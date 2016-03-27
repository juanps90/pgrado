# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 21:29:39 2016

@author: viki
"""
#
# Codificacion de colores para los sensores
SENSOR_COLOR_DETECT_NONE = -1
SENSOR_COLOR_DETECT_BLACK = 0
SENSOR_COLOR_DETECT_WHITE = 1
SENSOR_COLOR_DETECT_GREEN = 2
SENSOR_COLOR_DETECT_RED = 3
SENSOR_COLOR_DETECT_YELLOW = 4
SENSOR_COLOR_DETECT_BLUE = 5
SENSOR_COLOR_DETECT_ORANGE = 6
#
# id de los sensores
SENSOR_COLOR_DETECT_LINE_ID = 0
SENSOR_NOSE_ULTRASONIC_ID = 1
SENSOR_VISION_HEAD_ID = 2
#
# id de los comandos
COMMAND_INIT_LEARNING = 1
COMMAND_END_LEARNING = 2
COMMAND_PLAY = 3
COMMAND_STOP = 4
COMMAND_BAD = 5
RED_CALIBRATE = 7
GREEN_CALIBRATE=8
BLUE_CALIBRATE=9
ORANGE_CALIBRATE=10
YELLOW_CALIBRATE=11
END_CALIBRATE=12
COMMAND_COME = 13
COMMAND_GO = 14
COMMAND_EXIT = 15


#
# Constantes para los tipos de links
LINK_ORD=0
LINK_ENA=1
LINK_PRM=2
#
# id de las secciones del XML
SECCION_NODOS = 'nodos'
SECCION_PARAMETROS = 'parametros'
SECCION_TOPOLOGIA = 'topologia'
SECCION_NETWORK = 'network'
SECCION_COLORES = 'colores'

# Tipos de atributos

ATR_COLOR = 1
ATR_DIST  = 2
ATR_ANGLE = 3
