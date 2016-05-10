#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Const
# @brief Contiene un conjunto de constantes.
# @details Contiene un conjunto de constantes. La idea es que estos valores sean fijos y no se modifiquen dinamicamente.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

## Path por defecto en donde se encuentra la aplicación
PGRADO_HOME = '/home/viki/pgrado'
## Carpeta en donde se guardan los archivos XML de aprendizajes
PERSIT_FOLDER_NAME = 'persist'
## Carpeta en donde se guarda el archivo XML de configuración
CONFIG_FOLDER_NAME = 'config'
## Valor del nombre por defecto con el que se guarda el archivo de configuración
CONFIG_XML_NAME = 'parametros'


## Indentificado de un color no detectable.
SENSOR_COLOR_DETECT_NONE = -1
## Identificador del color negro.
SENSOR_COLOR_DETECT_BLACK = 0
## Identificador del color blanco.
SENSOR_COLOR_DETECT_WHITE = 1
## Identificador del color anaranjado.
SENSOR_COLOR_DETECT_ORANGE = 2
## Identificador del color amarillo.
SENSOR_COLOR_DETECT_YELLOW = 3
## Identificador del color verde.
SENSOR_COLOR_DETECT_GREEN = 4
## Identificador del color rojo.
SENSOR_COLOR_DETECT_RED = 5
## Identificador del color azul.
SENSOR_COLOR_DETECT_BLUE = 6

## Identificador de los sensores de detección de color que apuntan al suelo.
SENSOR_COLOR_DETECT_LINE_ID = 0
## Identificador del sensor de ultrasonido usado para detectar distancias.
SENSOR_NOSE_ULTRASONIC_ID = 1
## Identificador de la camara usada como sensor de vision.
SENSOR_VISION_HEAD_ID = 2
## Identificador del comando de inicio del aprendizaje.
COMMAND_INIT_LEARNING = 1
## Identificador del comando de fin del aprendizaje.
COMMAND_END_LEARNING = 2
## Identificador del comando de inicio de reporducción de un aprendizaje.
COMMAND_PLAY = 3
## Identificador del comando de fin de reporducción de un aprendizaje.
COMMAND_STOP = 4
## Identificador del comando BAD para indicar al robot que lo que hace esta mal.
COMMAND_BAD = 5
## Identificador del comando de calibración del color rojo.
RED_CALIBRATE = 7
## Identificador del comando de calibración del color verde.
GREEN_CALIBRATE=8
## Identificador del comando de calibración del color azul.
BLUE_CALIBRATE=9
## Identificador del comando de calibración del color anaranjado.
ORANGE_CALIBRATE=10
## Identificador del comando de calibración del color amarillo.
YELLOW_CALIBRATE=11
## Identificador del comando de fin de calibración.
END_CALIBRATE=12
## Identificador del comando COME.
COMMAND_COME = 13
## Identificador del comando GO.
COMMAND_GO = 14
## Identificador del comando salir.
COMMAND_EXIT = 15
## Identificador del comando HERE.
COMMAND_HERE = 16

## Identificador del tipo de link de orden.
LINK_ORD = 0 
## Identificador del tipo de link de habilitación.
LINK_ENA = 1 
## Identificador del tipo de link de permanencia.
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
# >> Constants used on Inputs.py script <<
#
debugInputs = 1 # for debugging set this variable to 1 (0 turns-off debugging)
#
#------------------------------------------------------------------------------
#
# >> Constants used on Outputs.py script <<
#
debugMotores = 1 # for debugging set this variable to 1 (0 turns-off debugging)
#
#------------------------------------------------------------------------------
#
# >> Constants used on LoadXML.py and SaveXML scripts <<
#
# XML sections' tags
SECCION_NODOS = 'nodos'
SECCION_PARAMETROS = 'parametros'
SECCION_TOPOLOGIA = 'topologia'
SECCION_NETWORK = 'network'
SECCION_COLORES = 'colores'

## Identificador del tipo de atributo color
ATR_COLOR = 1
## Identificador del tipo de atributo distancia
ATR_DIST  = 2
## Identificador del tipo de atributo ángulo
ATR_ANGLE = 3
