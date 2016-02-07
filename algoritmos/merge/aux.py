from node import Node, LinkPoint
class Aux:
    
    def sampleGraph1(self):
        # ABDFG
        
        nA = Node()
        nA.letra = 'A'
        
        nB = Node()
        nB.letra = 'B'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
        
       
        nINIT = Node()
        
        lA = LinkPoint(nA)
        lB = LinkPoint(nB)
        lD = LinkPoint(nD)
        lE = LinkPoint(nE)
        lInit = LinkPoint(nINIT)
        
        lInit.lpoint = lE
        lE.lpoint = lD
        lD.lpoint = lB
        lB.lpoint = lA
        
        lInit.length = 4
        
        return nINIT
        
    def sampleGraph2(self):
        
        nA = Node()
        nA.letra = 'A'
        
        nC = Node()
        nC.letra = 'C'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
        
       
        nINIT = Node()
        
        lA = LinkPoint(nA)
        lC = LinkPoint(nC)
        lD = LinkPoint(nD)
        lE = LinkPoint(nE)
        lInit = LinkPoint(nINIT)
        
        lInit.lpoint = lE
        lE.lpoint = lD
        lD.lpoint = lC
        lC.lpoint = lA
        
        lInit.length = 4
        lE.length = 3
        lD.length = 2
        lC.length = 1
        lA.length = 0
        
        return nINIT
