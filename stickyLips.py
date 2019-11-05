### original from point on palley youtube

##sticky lips curve clean up

##1. create curve by selecting lips edges and convert to nurbsCurve. ** create with Degree 1
##2. run the script with upper lip and lower lip are selected.
list = cmds.ls(sl=1)

crvMainGrp = cmds.group(name = "sticky_lip_main_grp",em=1)
lip_val_list = [] ##cv numbers list
bsList = [] ##blendshape name list
lip_name_list = ['upperLip', 'lowerLip']## prefix
#Left_main_attr = "head_icon.Left_Sticky_Lips"
#Right_main_attr = "head_icon.Right_Sticky_Lips"
#lip_val_list = [34, 30]

#create attribut for sticky lips
cmds.addAttr(crvMainGrp,ln = "leftStickyLips",min = 0 , max = 10,k=1 ,at="double")
cmds.addAttr(crvMainGrp,ln = "rightStickyLips",min = 0 , max = 10,k=1 ,at="double")

#loop for upper and lower lips to create addtional curve
for q in list:
    crvGrp = cmds.group(name = "%s_grp"%q,em=1,p=crvMainGrp)
    
    ##getting number of spans to add 2 additional knots before converting curve to Cubic(degree 3)
    span = cmds.getAttr("%s.spans"%q)-1    
    cmds.insertKnotCurve("%s.u[0.33333333]"%(q),add=1,ch=1,nk=1,rpo=1)
    cmds.insertKnotCurve("%s.u[%s.6666666667]"%(q,span),add=1,ch=1,nk=1,rpo=1)
    
    #duplicate curves for skin, sticky and wire
    newCrv = cmds.rebuildCurve(q,ch=0,rpo=0,rt=0,end=1,kr=0,kcp=0,kep=1,kt=0,s=0,d=3,tol=.01,name = "%s_skin"%q)
    stickyCrv = cmds.duplicate(newCrv[0],name = newCrv[0].replace("skin","sticky"))
    wireCrv = cmds.duplicate(newCrv[0],name = newCrv[0].replace("skin","wire"))
    
    ##clean up by parenting them into one group
    cmds.parent(q,newCrv[0],stickyCrv,wireCrv,crvGrp)
    bsList.append(cmds.blendShape(newCrv,stickyCrv,wireCrv,name = "%s_BS"%q)[0])
    
    lip_val_list.append(cmds.getAttr("%s.spans"%newCrv[0])+cmds.getAttr("%s.degree"%newCrv[0]))


##to loop thru "lip_name_list"
name_counter = 0

##loop cv counts
for each in lip_val_list:
    haLeft_val = (each / 2) + 1
    total_val = each + 1
    div_val = 10.0 / haLeft_val
    counter = 0
    while(counter<haLeft_val):
        lip_sr = cmds.shadingNode( 'setRange', asUtility=True, n='Left_' + lip_name_list[name_counter] + str(counter+1) + '_setRange')
        cmds.setAttr(lip_sr + '.oldMaxX', (div_val * (counter+1)))
        cmds.setAttr(lip_sr + '.oldMinX', (div_val * counter))
        cmds.setAttr(lip_sr + '.maxX', 0)
        cmds.setAttr(lip_sr + '.minX', 1)
        if counter == (haLeft_val - 1):
            cmds.setAttr(lip_sr + '.minX', 0.5)
        cmds.connectAttr("%s.leftStickyLips"%crvMainGrp, lip_sr + '.valueX', f=True)
        
        lip_flip_sr = cmds.shadingNode( 'setRange', asUtility=True, n='Left_' + lip_name_list[name_counter] + '_flip' + str(counter+1) + '_setRange')
        cmds.setAttr(lip_flip_sr + '.oldMaxX', 1)
        if counter == (haLeft_val - 1):
            cmds.setAttr(lip_flip_sr + '.oldMaxX', 0.5)
        cmds.setAttr(lip_flip_sr + '.oldMinX', 0)
        cmds.setAttr(lip_flip_sr + '.maxX', 0)
        cmds.setAttr(lip_flip_sr + '.minX', 1)
        if counter == (haLeft_val - 1):
            cmds.setAttr(lip_flip_sr + '.minX', 0.5)
        cmds.connectAttr(lip_sr + '.outValueX', lip_flip_sr + '.valueX', f=True)
            
        if counter == (haLeft_val - 1):
            mid_pma = cmds.shadingNode( 'plusMinusAverage', asUtility=True, n='ct_' + lip_name_list[name_counter] + str(counter+1) + '_plusMinusAverage')
            cmds.connectAttr(lip_sr + '.outValueX', mid_pma + '.input2D[0].input2Dx', f=True)
            cmds.connectAttr(lip_flip_sr + '.outValueX', mid_pma + '.input2D[0].input2Dy', f=True)
        else:
            cmds.connectAttr(lip_sr + '.outValueX', '%s.inputTarget[0].inputTargetGroup[0].targetWeights['%bsList[name_counter] + str(counter) + ']', f=True)
            cmds.connectAttr(lip_flip_sr + '.outValueX', '%s.inputTarget[0].inputTargetGroup[1].targetWeights['%bsList[name_counter] + str(counter) + ']', f=True)
        
        counter = counter + 1
        
    #div_val = 10.0 / 39
    counter = haLeft_val - 1
    rev_counter = haLeft_val
    while(counter<total_val):
        lip_sr = cmds.shadingNode( 'setRange', asUtility=True, n='Right_' + lip_name_list[name_counter] + str(counter+1) + '_setRange')
        cmds.setAttr(lip_sr + '.oldMaxX', (div_val * rev_counter))
        cmds.setAttr(lip_sr + '.oldMinX', (div_val * (rev_counter-1)))
        cmds.setAttr(lip_sr + '.maxX', 0)
        cmds.setAttr(lip_sr + '.minX', 1)
        if counter == (haLeft_val - 1):
            cmds.setAttr(lip_sr + '.minX', 0.5)
        cmds.connectAttr("%s.rightStickyLips"%crvMainGrp, lip_sr + '.valueX', f=True)
        
        lip_flip_sr = cmds.shadingNode( 'setRange', asUtility=True, n='Right_' + lip_name_list[name_counter] + '_flip' + str(counter+1) + '_setRange')
        cmds.setAttr(lip_flip_sr + '.oldMaxX', 1)
        if counter == (haLeft_val - 1):
            cmds.setAttr(lip_flip_sr + '.oldMaxX', 0.5)
        cmds.setAttr(lip_flip_sr + '.oldMinX', 0)
        cmds.setAttr(lip_flip_sr + '.maxX', 0)
        cmds.setAttr(lip_flip_sr + '.minX', 1)
        if counter == (haLeft_val - 1):
            cmds.setAttr(lip_flip_sr + '.minX', 0.5)
        cmds.connectAttr(lip_sr + '.outValueX', lip_flip_sr + '.valueX', f=True)
        
        if counter == (haLeft_val - 1):
            cmds.connectAttr(lip_sr + '.outValueX', mid_pma + '.input2D[1].input2Dx', f=True)
            cmds.connectAttr(lip_flip_sr + '.outValueX', mid_pma + '.input2D[1].input2Dy', f=True)
            cmds.connectAttr(mid_pma + '.output2Dx', '%s.inputTarget[0].inputTargetGroup[0].targetWeights['%bsList[name_counter] + str(counter) + ']', f=True)
            cmds.connectAttr(mid_pma + '.output2Dy', '%s.inputTarget[0].inputTargetGroup[1].targetWeights['%bsList[name_counter] + str(counter) + ']', f=True)
        else:
            cmds.connectAttr(lip_sr + '.outValueX', '%s.inputTarget[0].inputTargetGroup[0].targetWeights['%bsList[name_counter]+ str(counter) + ']', f=True)
            cmds.connectAttr(lip_flip_sr + '.outValueX', '%s.inputTarget[0].inputTargetGroup[1].targetWeights['%bsList[name_counter] + str(counter) + ']', f=True)
        
        counter = counter + 1
        rev_counter = rev_counter - 1
    name_counter = name_counter + 1
