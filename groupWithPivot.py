import maya.cmds as cmds
list = cmds.ls(sl=1)
cmds.select(cl=1)
for item in list:
    mainGrp = cmds.group(name = "%s_main_grp"%item,em=1)
    offGrp = cmds.group(name = "%s_offset_grp"%item,em=1,p=mainGrp)
    drvGrp = cmds.group(name = "%s_DRV_grp"%item,em=1,p=offGrp)
    parent = cmds.listRelatives(item,p=1)
    if parent!= None:
        cmds.parent(mainGrp,item)
        
    pc = cmds.parentConstraint(item,mainGrp,name = "tempPCC1",mo=0)
    cmds.delete(pc)
    
    cmds.parent(mainGrp,parent)
    cmds.parent(item,drvGrp)
