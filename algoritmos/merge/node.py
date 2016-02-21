class LinkPoint:
    def __init__(self, node):
        self.thisNode =  node # Referencias al nodo padre
        self.score = 0
		
        self.lpoint = None
        
        self.length = 0 # largo del camino
        
		# ------ Datos para calculos de valores --------
        self.values = None
        self.samePrefix = None
		
		# Indica el nodo al que apunta cuando se esta haciendo el algoritmo de similitud
		# O sea el mas parecido
        self.mov = None
        
        node.n.append(self)

#class LinkNodo:
#	def __init__(self, ltype, lnode):
#		self.ltype =  ltype
#        self.lnode = lnode



class Node:
    """Representa un nodo"""
    LINK_ORD=1
    LINK_ENA=2
    LINK_PRM=3
    
    def __init__(self):
        # ------ Datos de la estructura ------------
        self.letra = None        
        self.childNodes = [] # recorre el grafo al reves
        self.parentNodes = []
        self.parentTypes = []
        
        
        # Valores del calculo
        self.n = []
        # extraLinks
	
    def run(self, conds):
        print "RUN iracolor"
        
