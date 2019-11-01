"""
formula by nickyliu
/ -----------------------------------------------------------
//     $d : current distance betw ends
//     $D : initial distance betw ends
//     $S : IK softness
//
//     softJ_start & softJ_end
//         a 2-joint chain with it's IK parented under e.g. foot ctrl
//         the main IK is point constrainted to softJ_end
// -----------------------------------------------------------

float $S = ctrl.soft;
float $D_soft = $D - $S;
float $new_d = $d;

if ( $d > $D_soft ) {
    float $x = $d - $D_soft;
    $new_d = $D_soft + $S *( 1-exp(-$x) );
}

softJ_end.ty = $new_d;
"""
[ctrl,ikMain] = [cmds.ls(sl=1)[0],cmds.ls(sl=1,type = "ikHandle")[0]]
jntList = cmds.ikHandle(ikMain, q=1,jl=1)
jntList.append(cmds.listRelatives(jntList[-1],type = "joint"))
ikJnts = [jntList[0],jntList[-1]]

pref = ikMain.split("ikHandle")[0]
pref = pref[:-1] if pref[-1] == "_" else pref
total = cmds.xform(jntList[1],q=1,t=1)[0]+cmds.xform(jntList[2],q=1,t=1)[0]

## create node
locA = cmds.spaceLocator(name = "%s_locA"%pref)
locB = cmds.spaceLocator(name = "%s_locB"%pref)
dimNode = cmds.shadingNode("distanceDimShape",au=1,name = "%s_distanceNodeShape"%pref)

locShp = []
for ind , loc in enumerate([locA,locB]):
    cmds.xform(loc,t=cmds.xform(ikJnts[ind],q=1,ws=1,t=1))
    locShp.append(cmds.listRelatives(loc, type = "locator")[0])
    

distanceSub = cmds.shadingNode("plusMinusAverage",name = "%s_softIk_distance_SUB",au=1)
diffSub = cmds.shadingNode("plusMinusAverage",name = "%s_softIk_diff_SUB",au=1)
negUc = cmds.shadingNode("unitConversion",name = "%s_softIk_diff_NEG",au=1)
expNode = cmds.shadingNode("multiplyDivide",name = "%s_exp_diff_POW",au=1)
revSub = cmds.shadingNode("plusMinusAverage",name = "%s_rev_exp_SUB",au=1)
expMult = cmds.shadingNode("multiplyDivide",name = "%s_softIk_exp_MULT",au=1)
finalAdd = cmds.shadingNode("plusMinusAverage",name = "%s_softIk_ADD",au=1)
condNode = cmds.shadingNode("condition",name = "%s_softIk_COND",au=1)

##set attribute##
cmds.setAttr("%s.input1D[0]"%distanceSub,total)
cmds.setAttr("%s.operation"%distanceSub,2)
cmds.setAttr("%s.operation"%diffSub,2)
cmds.setAttr("%s.conversionFactor"%negUc,-1)
cmds.setAttr("%s.operation"%expNode,3)
cmds.setAttr("%s.input1X"%expNode,2.718)
cmds.setAttr("%s.operation"%revSub,2)
cmds.setAttr("%s.input1D[0]"%distanceSub,1)
cmds.setAttr("%s.operation"%expMult,1)
cmds.setAttr("%s.operation"%finalAdd,1)
cmds.setAttr("%s.operation"%condNode,2)

##connect attribute##
##distance node
cmds.connectAttr("%s.worldPosition"%locShp[0],"%s.startPoint"%dimNode)
cmds.connectAttr("%s.worldPosition"%locShp[1],"%s.endPoint"%dimNode)
