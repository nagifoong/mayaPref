'''
create attribute on object has fk ik switch.
ikFkSnap to let script understand which object need to use this function
ikMain = IK Controller
ikPoleVector = ik Pole Vector Controller
fkChain = fk Controller Chain
skinJoints = skin/ result joints which influence by fk and ik chain
ikSpace = if ik and fk controller have different rotation
'''
from maya import cmds, OpenMaya

#sel = cmds.ls(sl=1)[0]
status = cmds.getAttr("%s.ikFk"%sel)
if "ikFkSnap" in cmds.listAttr(sel):
    ikCtrls = [cmds.getAttr("%s.ikMain"%sel),cmds.getAttr("%s.ikPoleVector"%sel)]
    fkCtrls = cmds.getAttr("%s.fkChain"%sel).split(",")
    skinJnts = cmds.getAttr("%s.skinJoints"%sel).split(",")
    if status == 0:
        for ind , fk in enumerate(fkCtrls):
            cmds.xform(fk,ws=1,ro=cmds.xform(skinJnts[ind],q=1,ws=1,ro=1))
        cmds.setAttr("%s.ikFk"%sel,1)
    else:
        if "ikSpace" in cmds.listAttr(sel):
            ikLoc = cmds.getAttr("%s.ikSpace"%sel)
            cmds.xform(ikCtrls[0],ws=1,ro=cmds.xform(ikLoc,q=1,ws=1,ro=1))
            cmds.xform(ikCtrls[0],ws=1,t=cmds.xform(ikLoc,q=1,ws=1,t=1))
        else:
            cmds.xform(ikCtrls[0],ws=1,t=cmds.xform(skinJnts[-1],q=1,ws=1,t=1))
            ikOrigRot = cmds.xform(ikCtrls[0],q=1,ws=1,ro=1)
            fkOrigRot = cmds.xform(fkCtrls[-1],q=1,ws=1,ro=1)
            finalRot = [fkOrigRot[i]-q for i,q in enumerate(ikOrigRot)]
            cmds.xform(ikCtrls[0],ro=ikLoc)
            ##find pole vector
            
        newStartV = [cmds.xform(fkCtrls[1] ,q= 1 ,ws = 1,t =1 )[i]-cmds.xform(fkCtrls[0] ,q= 1 ,ws = 1,t =1 )[i] for i in range(3)]
        newEndV = [cmds.xform(fkCtrls[1] ,q= 1 ,ws = 1,t =1 )[i]-cmds.xform(fkCtrls[2] ,q= 1 ,ws = 1,t =1 )[i] for i in range(3)]
        resultV = [cmds.xform(fkCtrls[1] ,q= 1 ,ws = 1,t =1 )[i]+ newStartV[i]*.75+ newEndV[i] *.75 for i in range(3)]
        
        start = cmds.xform(fkCtrls[0] ,q= 1 ,ws = 1,t =1 )
        mid = cmds.xform(fkCtrls[1] ,q= 1 ,ws = 1,t =1 )
        end = cmds.xform(fkCtrls[2] ,q= 1 ,ws = 1,t =1 )
        startV = OpenMaya.MVector(start[0] ,start[1],start[2])
        midV = OpenMaya.MVector(mid[0] ,mid[1],mid[2])
        endV = OpenMaya.MVector(end[0] ,end[1],end[2])
        startEnd = endV - startV
        startMid = midV - startV
        dotP = startMid * startEnd
        proj = float(dotP) / float(startEnd.length())
        startEndN = startEnd.normal()
        projV = startEndN * proj
        arrowV = startMid - projV        
        finalV = (arrowV*(startEnd.length()/20)) + midV
       ##Pole Vector Controller Creation and Reposition ##
        cmds.xform(ikCtrls[1] , ws =1 , t= (finalV.x  , finalV.y  , finalV.z))
                    
        #cmds.xform(ikCtrls[1] , ws =1 , t= (resultV[0]  , resultV[1]  , resultV[2]))
        cmds.setAttr("%s.ikFk"%sel,0)
