### Select follicles wanted to be projected and object(nurbsSurface) to be project 
def createFollicle(obj , name = '' ,uPos = 0.0, vPos = 0.0):
    if cmds.objectType(obj,isType = "transform"):
        cmds.warning( "Please insert only \"Mesh\" or \"nurbsSurface\".")
        return
    #name = "test"
    
    ####Create follicle shape
    fol = cmds.createNode("follicle",name = name+"_shape")
    folTrans = cmds.listRelatives(fol,p=1,type= "transform")[0]
    folTrans = cmds.rename(folTrans,name)
    
    try:
        cmds.connectAttr("%s.local"%obj,"%s.inputSurface"%fol,f=1)
    except:
        cmds.connectAttr("%s.outMesh"%obj,"%s.inputMesh"%fol,f=1)
    cmds.connectAttr("%s.worldMatrix[0]"%obj,"%s.inputWorldMatrix"%fol,f=1)
    
    cmds.connectAttr("%s.outRotate"%fol,"%s.rotate"%folTrans,f=1)
    cmds.connectAttr("%s.outTranslate"%fol,"%s.translate"%folTrans,f=1)    
    
    ####Adding attribute on transform node for futher adjustments
    cmds.addAttr(name,ln='uValue',at='double',k=1)
    cmds.addAttr(name,ln='vValue',at='double',k=1)
    
    uUc= cmds.shadingNode('unitConversion',au=1,n=name+'_uValue')	
    vUc= cmds.shadingNode('unitConversion',au=1,n=name+'_vValue')
    
    cmds.setAttr('%s.conversionFactor'%uUc,.01)
    cmds.setAttr('%s.conversionFactor'%vUc,.01)
    
    cmds.connectAttr(name+".uValue",'%s.input'%uUc,f=1)
    cmds.connectAttr(name+".vValue",'%s.input'%vUc,f=1)
    
    cmds.setAttr(name+'.uValue',uPos*100)
    cmds.setAttr(name+'.vValue',vPos*100)
    
    cmds.connectAttr(name+'_uValue.output', fol+'.parameterU' , f=1)
    cmds.connectAttr(name+'_vValue.output', fol+'.parameterV' , f=1)
    
    ##Clean up: lock transform's translate and rotate
    cmds.setAttr(name+".t",lock=1)
    cmds.setAttr(name+".r",lock=1)
    
    #ctrlSys = createIkFeather(folTrans,name=name.replace("follicle",""))
    
    return folTrans,fol
    
selList = cmds.ls(sl=1)
geo = selList[-1]
geoShape = cmds.listRelatives(geo,type = "nurbsSurface")[0]
fols = selList[:-1]

tempFol = createFollicle(geoShape , name = 'tempFol')
tempLoc = cmds.spaceLocator(name = "tempLoc")[0]
tempG = cmds.group(name = "tempGrp",em=1)
tempNode = cmds.createNode('closestPointOnSurface',name = "tempCPOM")
tempMult = cmds.createNode('multiplyDivide',name = "tempMD")
resultG = cmds.group(name = "projectedFollicleGrp",em=1)

cmds.setAttr("%s.tz"%tempLoc,1000)
cmds.setAttr("%s.input2"%tempMult,.5,.125,0,type = "double3")
cmds.parentConstraint(tempG,tempLoc,mo=1)
cmds.connectAttr("%s.worldSpace[0]"%geoShape , "%s.inputSurface"%tempNode)
cmds.connectAttr("%s.t"%tempLoc , "%s.inPosition"%tempNode)
cmds.connectAttr("%s.parameterU"%tempNode,'%s.input1X'%tempMult)
cmds.connectAttr("%s.parameterV"%tempNode,'%s.input1Y'%tempMult)
cmds.connectAttr('%s.outputX'%tempMult,"%s.parameterU"%tempFol[1],f=1)
cmds.connectAttr('%s.outputY'%tempMult,"%s.parameterV"%tempFol[1],f=1)

for fol in fols:
    const = cmds.parentConstraint(fol,tempG,mo=0)    
    newFol = createFollicle(geoShape , name = '%s_aim'%fol,uPos = cmds.getAttr("%s.parameterU"%tempFol[1]),vPos =cmds.getAttr("%s.parameterV"%tempFol[1]) )
    cmds.delete(const)
    cmds.parent(newFol[0],resultG)
cmds.delete(tempFol,tempLoc,tempG,tempNode,tempMult)
    
