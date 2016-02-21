from node import Node
class Aux:
    
    def sampleGraph1(self):
        # ABDFG
        
        nA = Node()
        nA.letra = 'A'
        
        nB = Node()
        nB.letra = 'B'
        
        nC = Node()
        nC.letra = 'C'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
        
       
        nINIT = Node()
        
        nINIT.parentNodes = [nE]
        nE.parentNodes = [nD]
        nD.parentNodes = [nB, nC]
        nC.parentNodes = [nA]
        nB.parentNodes = [nA]
        
        
        # Enlaces reversos
        nE.childNodes = [nINIT]
        nD.childNodes = [nE]
        nC.childNodes = [nD]
        nB.childNodes = [nD]
        nA.childNodes = [nB, nC]
        
        
        
        return nINIT
        
    def sampleGraph2(self):
        
        nA = Node()
        nA.letra = 'A'
        
      
        nK = Node()
        nK.letra = 'K'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
       
        nINIT = Node()
        

        nINIT.parentNodes = [nE]
        nE.parentNodes = [nD]
        nD.parentNodes = [nK]
        nK.parentNodes = [nA]
        
        nINIT.parentTypes = [Node.LINK_ORD]
        nE.parentTypes = [Node.LINK_ORD]
        nD.parentTypes = [Node.LINK_ORD]
        nK.parentTypes = [Node.LINK_ORD]
        
        return nINIT
        
    def sampleGraph3(self):
        
        nA = Node()
        nA.letra = 'X'
        
      
        nK = Node()
        nK.letra = 'K'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
       
        nINIT = Node()
        

        nINIT.parentNodes = [nE]
        nE.parentNodes = [nD]
        nD.parentNodes = [nK]
        nK.parentNodes = [nA]
        
        nINIT.parentTypes = [Node.LINK_ORD]
        nE.parentTypes = [Node.LINK_ORD]
        nD.parentTypes = [Node.LINK_ORD]
        nK.parentTypes = [Node.LINK_ORD]
        
        return nINIT
