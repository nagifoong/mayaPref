## joint follow mesh silhouette with controllers (joint on skull to simulate muscle)
## select controllers and run script
## redefine mesh!!!!
ctrls = cmds.ls(sl=1)
mesh = "skull_geoShape"
jntMainGrp = cmds.group(name = "jnt_%s"%mesh.replace("Shape","_grp"),em=1)
utilMainGrp = cmds.group(name = "%s_util"%mesh.replace("Shape","_grp"),em=1)
for ctrl in ctrls:
    ##create groups, joints and locators
    prefix = ctrl.replace("CTRL_","")
    locGrp = cmds.group(em=1,name = "%s_loc_grp"%prefix)
    jntGrp = cmds.group(em=1,name = "jnt_%s_loc_grp"%prefix)
    loc  = cmds.spaceLocator(name = "%s_loc"%prefix)[0]
    jnt = cmds.joint(name = "jnt_%s"%prefix)
    node = cmds.shadingNode("closestPointOnMesh",au=1,name = "%s_pntOnMEsh"%prefix)
    
    locShp = cmds.listRelatives(loc,type="locator")[0]
    
    ##clean up
    cmds.parent(jntGrp,jntMainGrp)
    cmds.parent(locGrp,utilMainGrp)
    cmds.parent(loc,locGrp)
    cmds.parent(jnt,jntGrp)
    
    ##relocate locator group to controller
    cmds.delete(cmds.parentConstraint(ctrl,locGrp,mo=0))
    
    #connect attribute
    cmds.connectAttr("%s.outMesh"%mesh,"%s.inMesh"%node)
    cmds.connectAttr("%s.t"%ctrl,"%s.t"%loc)
    cmds.connectAttr("%s.worldPosition"%locShp,"%s.inPosition"%node)
    cmds.connectAttr("%s.position"%node,"%s.t"%jntGrp)
