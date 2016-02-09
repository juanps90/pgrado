from node import Node, LinkPoint
class Aux:
    
    def sampleGraph1(self):
        # ABDFG
        
        nA = Node()
        nA.letra = 'A'
        
        nA2 = Node()
        nA2.letra = 'a'
        
        
        nB = Node()
        nB.letra = 'B'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
        
       
        nINIT = Node()
        
        lA = LinkPoint(nA)
        lA2 = LinkPoint(nA2)
        lB = LinkPoint(nB)
        lD = LinkPoint(nD)
        lE = LinkPoint(nE)
        lInit = LinkPoint(nINIT)
        
        lInit.lpoint = lE
        lE.lpoint = lD
        lD.lpoint = lB
        lB.lpoint = lA2
        lA2.lpoint = lA
        
        lInit.length = 5
        
        return nINIT
        
    def sampleGraph2(self):
        
        nA = Node()
        nA.letra = 'A'
        
        nA2 = Node()
        nA2.letra = 'a'
        
        nC = Node()
        nC.letra = 'C'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
        
       
        nINIT = Node()
        
        lA = LinkPoint(nA)
        lA2 = LinkPoint(nA2)
        lC = LinkPoint(nC)
        lD = LinkPoint(nD)
        lE = LinkPoint(nE)
        lInit = LinkPoint(nINIT)
        
        lInit.lpoint = lE
        lE.lpoint = lD
        lD.lpoint = lC
        lC.lpoint = lA2
        lA2.lpoint = lA
        
        lInit.length = 5
        lE.length = 4
        lD.length = 3
        lC.length = 2
        lA2.length = 1
        lA.length = 0
        
        return nINIT

    def sampleGraph3(self):
        
        nA = Node()
        nA.letra = 'P'
        
        nA2 = Node()
        nA2.letra = 'a'
        
        nC = Node()
        nC.letra = 'C'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
        
       
        nINIT = Node()
        
        lA = LinkPoint(nA)
        lA2 = LinkPoint(nA2)
        lC = LinkPoint(nC)
        lD = LinkPoint(nD)
        lE = LinkPoint(nE)
        lInit = LinkPoint(nINIT)
        
        lInit.lpoint = lE
        lE.lpoint = lD
        lD.lpoint = lC
        lC.lpoint = lA2
        lA2.lpoint = lA
        
        lInit.length = 5
        lE.length = 4
        lD.length = 3
        lC.length = 2
        lA2.length = 1
        lA.length = 0
        
        return nINIT
