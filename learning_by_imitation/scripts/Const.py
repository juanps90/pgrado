#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#------------------------------------------------------------------------------
# --------------------------- General use constants --------------------------
#------------------------------------------------------------------------------
# 
# Environment variables, important folder and file names
PGRADO_HOME = '/home/viki/pgrado'
PERSIT_FOLDER_NAME = 'persist'
CONFIG_FOLDER_NAME = 'config'
CONFIG_XML_NAME = 'parametros'
#
# Color codification used by sensors
SENSOR_COLOR_DETECT_NONE = -1
SENSOR_COLOR_DETECT_BLACK = 0
SENSOR_COLOR_DETECT_WHITE = 1
SENSOR_COLOR_DETECT_ORANGE = 2
SENSOR_COLOR_DETECT_YELLOW = 3
SENSOR_COLOR_DETECT_GREEN = 4
SENSOR_COLOR_DETECT_RED = 5
SENSOR_COLOR_DETECT_BLUE = 6
#
# sensors' id
SENSOR_COLOR_DETECT_LINE_ID = 0
SENSOR_NOSE_ULTRASONIC_ID = 1
SENSOR_VISION_HEAD_ID = 2
#
# commands' id
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
COMMAND_HERE = 16
#
# link types 
LINK_ORD = 0 
LINK_ENA = 1 
LINK_PRM = 2
#
#------------------------------------------------------------------------------
#-------------------------- Script specific constats --------------------------
#------------------------------------------------------------------------------
#
# >> Constants used on master.py script <<
#
debugMaestro = 1 # for debugging set this variable to 1 (0 turns-off debugging)
if debugMaestro == 1:
    EPSILON = 5000 # Used for link creation with debugging
else:
    EPSILON = 500 # Used for link creation without debugging
#
#------------------------------------------------------------------------------
#
# >> Constants used on inputs.py script <<
#
debugInputs = 1 # for debugging set this variable to 1 (0 turns-off debugging)
#
#------------------------------------------------------------------------------
#
# >> Constants used on motores.py script <<
#
debugMotores = 1 # for debugging set this variable to 1 (0 turns-off debugging)
#
#------------------------------------------------------------------------------
#
# >> Constants used on cargarXML.py and salvarXML scripts <<
#
# XML sections' tags
SECCION_NODOS = 'nodos'
SECCION_PARAMETROS = 'parametros'
SECCION_TOPOLOGIA = 'topologia'
SECCION_NETWORK = 'network'
SECCION_COLORES = 'colores'
#
# Attribute types
ATR_COLOR = 1
ATR_DIST  = 2
ATR_ANGLE = 3
