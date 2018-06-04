import maya.cmds as cmds
###Select nurbsSurface or mesh to run it
### To mirror duplicate the nurbsSurface and set ScaleX to -1

def createIkFeather(obj , name= '',follicleShape = '',pos = [0,0]):
    totalJnt = 5    
    jntList= []
    drvJnt = []
    cmds.select(cl=1)
    ##Create skin joints and driver joints
    for ind in range(totalJnt):
        if ind >0:
            cmds.select(jnt)
        jnt= cmds.joint(name ="jnt_%s_%s_skin"%(name,str(ind+1).zfill(2)),p=[ind,0,0],rad=.05)
        jntList.append(jnt)
    
        if ind +1 == totalJnt or ind == 0 or ind ==totalJnt/2:
            temp = cmds.duplicate(jnt)[0]
            temp = cmds.rename(temp,"jnt_%s_%s_DRV"%(name,str(len(drvJnt)+1).zfill(2)))        
            if len(drvJnt)>0:
                temp = cmds.parent(temp,drvJnt[-1])[0]
            drvJnt.append(temp)
            
    #Create IkHandle        
    hdl = cmds.ikHandle(ns =2,sj=jntList[0],ee=jntList[-1],sol = "ikSplineSolver",name = name+"_ikHandle")
    hdl[-1] = cmds.rename(hdl[-1],name + "_ikCurve")
    
    #Create and adjust skin cluster
    skinClus = eval("cmds.skinCluster(\"%s\",hdl[-1])"%("\",\"".join(drvJnt)))[0] 
       
    crvShape = cmds.listRelatives(hdl[-1],c=1,type = "nurbsCurve")[0]
    crvSpans = cmds.getAttr("%s.spans"%crvShape)+cmds.getAttr("%s.degree"%crvShape)
    
    ite = 0
    for ct in range(crvSpans):
        
        if ct%2 == 0:        
            cmds.skinPercent(skinClus,"%s.cv[%s]"%(hdl[-1],ct),transformValue = (drvJnt[ite],1))
            ite+=1
        else:
            cmds.skinPercent(skinClus,"%s.cv[%s]"%(hdl[-1],ct),transformValue = [(drvJnt[ite-1],.9),(drvJnt[ite],.1)])
            #cmds.skinPercent(skinClus,"%s.cv[%s]"%(hdl[-1],ct),transformValue = (drvJnt[ite-1],1))
    
    #Create Controller ,groups for it and reposition it
    ctrl = cmds.curve(name = "CTRL_"+name,d=1,p=[(1,0,-1),(1,0,1),(3,0,0),(1,0,-1)])
    offG = cmds.group(name = ctrl+"_drv_grp",em=1)
    mainG = cmds.group(name = ctrl+"_main_grp")
    constG = cmds.group(name = ctrl+"_const_grp")
    cmds.parent(ctrl,offG)
    
    cmds.parentConstraint(mainG,drvJnt[0])
    
    #cmds.addAttr(ctrl,ln="length",at="double",k=1)
    cmds.parentConstraint(drvJnt[-1],offG,mo=0,name = "PCCCC1")
    cmds.delete("PCCCC1")
    #cmds.setAttr("%s.length"%ctrl,cmds.getAttr("%s.tx"%offG))
    
    cmds.parentConstraint(ctrl,drvJnt[-1])
    
    #Create connection to readjust the length for the chain
    midUc = cmds.createNode("unitConversion",name = name +"_Mid_uc")
    cmds.setAttr('%s.conversionFactor'%midUc,.5)
    cmds.connectAttr(offG+".tx",'%s.input'%midUc,f=1)    
    cmds.connectAttr('%s.output'%midUc, drvJnt[1]+'.tx' , f=1)
    
    skinUc = cmds.createNode("unitConversion",name = name +"_skin_uc")
    cmds.setAttr('%s.conversionFactor'%skinUc,1.0/(totalJnt-1))
    cmds.connectAttr(offG+".tx",'%s.input'%skinUc,f=1)
    for jnt in  jntList[1:]:   
        cmds.connectAttr('%s.output'%skinUc, jnt+'.tx' , f=1)
    
    #Connect twist attribute and clean up
    cmds.setAttr("%s.dTwistControlEnable"%hdl[0],1)
    cmds.setAttr("%s.dWorldUpType"%hdl[0],3)
    cmds.connectAttr("%s.worldMatrix[0]"%mainG,"%s.dWorldUpMatrix"%hdl[0])
    cmds.connectAttr("%s.rx"%ctrl,"%s.twist"%hdl[0])
    
    cmds.setAttr("%s.tx"%ctrl,l=1,k=0,cb=0)
    cmds.setAttr("%s.ry"%ctrl,l=1,k=0,cb=0)
    cmds.setAttr("%s.rz"%ctrl,l=1,k=0,cb=0)
    cmds.setAttr("%s.s"%ctrl,l=1,k=0,cb=0)
    
    #cmds.setAttr("%s.ty"%offG,l=1)
    #cmds.setAttr("%s.tz"%offG,l=1)
    #cmds.setAttr("%s.r"%offG,l=1)
    #cmds.setAttr("%s.s"%offG,l=1)
    
    #cmds.setAttr("%s.rx"%mainG,90)
    cmds.setAttr("%s.visibility"%drvJnt[0],0)
    utilG = cmds.group(name = "%s_util_grp"%name,em=1)
    jntG = cmds.group(name = "%s_jnt_grp"%name,em=1)
    
    cmds.parent(jntList[0],drvJnt[0],jntG)
    cmds.parent(hdl[0],hdl[-1],utilG)
    
    cmds.parentConstraint(obj,constG,mo=0) 
    
    ###Create nodes for group bending   
    plus = cmds.createNode("plusMinusAverage",n="%s_bend_SUM"%name)
    ucA = cmds.createNode("unitConversion", n ="%s_bend_ucA"%name)
    ucB = cmds.createNode("unitConversion", n ="%s_bend_ucB"%name)
    
    cmds.connectAttr(ucA+".output",plus+".input1D[0]")
    cmds.connectAttr(ucB+".output",plus+".input1D[1]")
    cmds.connectAttr(plus+".output1D",offG+".ty")
    
    ####Adding attribute on transform node for futher adjustments
    cmds.addAttr(offG,ln='uValue',at='double',k=1)
    cmds.addAttr(offG,ln='vValue',at='double',k=1)
     
    uUc= cmds.shadingNode('unitConversion',au=1,n=follicleShape+'_uValue')	
    vUc= cmds.shadingNode('unitConversion',au=1,n=follicleShape+'_vValue')
    
    cmds.setAttr('%s.conversionFactor'%uUc,.01)
    cmds.setAttr('%s.conversionFactor'%vUc,.01)
    
    cmds.connectAttr(offG+".uValue",'%s.input'%uUc,f=1)
    cmds.connectAttr(offG+".vValue",'%s.input'%vUc,f=1)
    
    cmds.setAttr(offG+'.uValue',pos[0]*100)
    cmds.setAttr(offG+'.vValue',pos[1]*100)
    
    cmds.connectAttr('%s.output'%uUc, follicleShape+'.parameterU' , f=1)
    cmds.connectAttr('%s.output'%vUc, follicleShape+'.parameterV' , f=1)

    return [jntG,constG,utilG,ucA,ucB]

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
    

    
    ##Clean up: lock transform's translate and rotate
    cmds.setAttr(name+".t",lock=1)
    cmds.setAttr(name+".r",lock=1)
    
    ctrlSys = createIkFeather(folTrans,name=name.replace("follicle",""),follicleShape = fol,pos =[uPos,vPos])
    
    return folTrans,ctrlSys
    

def mainRun(*n):
    #### mode 0= U ,1=V
    ##Getting value from UI
    mode = cmds.radioButtonGrp("folPlacementRadio",q=1,sl=1)
    pri = cmds.textFieldGrp("priFeatherTxt",q=1,text= 1)   
    secUp=cmds.textFieldGrp("secUpFeatherTxt",q=1,text= 1)  
    secDown = cmds.textFieldGrp("secDownFeatherTxt",q=1,text= 1) 
    
    if not(pri.isdigit() and  secUp.isdigit() and secDown.isdigit()):
        cmds.warning("Please insert digit on the feather counts.")
        return
    
    #Compiling data from UI and selection
    pri,secUp,secDown = int(pri),int(secUp),int(secDown)
    priDiff = 1.0/(pri-1)
    secUpDiff = 1.0/(secUp+1)
    secDownDiff = 1.0/(secDown+1)
    total = pri+secUp+secDown
    sel = cmds.ls(sl=1)[0]
    surf = cmds.listRelatives(sel,type = "nurbsSurface")[0]
    
    #spansU = cmds.getAttr("%s.spansU"%surf)
    #spansV = cmds.getAttr("%s.spansV"%surf)
    
    #degU = cmds.getAttr("%s.degreeU"%surf)
    #degV = cmds.getAttr("%s.degreeV"%surf)
    
    #formU = cmds.getAttr("%s.formU"%surf)
    #formV = cmds.getAttr("%s.formV"%surf)
    
    #cvU = spansU+degU
    #cvV = spansV+degV
    
    #if formU == 2 :
    #    cvU -= degU
    #if formV == 2 :
    #    cvV -= degV
    
    #totalCV = cvU * cvV
    
    #Creating Main groups for util,jnt and ctrl
    folGrp = cmds.group(name =sel+"_follicle_grp",em=1 )
    utilMain = cmds.group(name ="%s_main_util_grp"%sel )
    featherMain = cmds.group(name ="CTRL_%sMain_grp"%sel,em=1 ) 
    ctMain = cmds.group(name ="CTRL_%s_main_grp"%sel)    
    jntMain = cmds.group(name ="jnt_%s_main_grp"%sel,em=1 )
    
    #Creating featherMain controllers and groups
    ctTip = cmds.circle(d=3,name ="CTRL_%s_tip"%sel,nr=[0,1,0],ch=0)[0]
    tipG = cmds.group(name = "CTRL_%s_tip_grp"%sel)
    cmds.addAttr(ctTip,ln="bend",k=1,at="double")
    cmds.addAttr(ctTip,ln="microCtrlVis",k=1,at="bool",dv=1)
    
    
    ctSecStart = cmds.circle(name = "CTRL_%s_SecondaryStart"%sel,d=3,nr=[0,1,0],ch=0)[0]
    secStartG = cmds.group(name = "CTRL_%s_SecondaryStart_grp"%sel)
    cmds.addAttr(ctSecStart,ln="bend",k=1,at="double")
    cmds.addAttr(ctSecStart,ln="microCtrlVis",k=1,at="bool",dv=1)
    
    ctSecMid = cmds.circle(name = "CTRL_%s_SecondaryMid"%sel,d=3,nr=[0,1,0],ch=0)[0]
    secMidG = cmds.group(name = "CTRL_%s_SecondaryMid_grp"%sel)
    cmds.addAttr(ctSecMid,ln="bend",k=1,at="double")
    cmds.addAttr(ctSecMid,ln="microCtrlVis",k=1,at="bool",dv=1)
    
    ctSecEnd = cmds.circle(name = "CTRL_%s_SecondaryEnd"%sel,d=3,nr=[0,1,0],ch=0)[0]
    secEndG = cmds.group(name = "CTRL_%s_SecondaryEnd_grp"%sel)
    cmds.addAttr(ctSecEnd,ln="bend",k=1,at="double")
    
    #to measure object is point +x or -x
    folList = []
    mirror =0
    #to store weight for blending between to controllers
    counterWeight = 0
    
    #Create feather controllers
    for ite in range(total+1):        
        if mode == 1:
            fol,ctSys = createFollicle(surf , name = sel+"_follicle"+str(ite+1).zfill(2) ,uPos = ite/(total-1.0), vPos = 0.5)
        
        elif mode == 2:
            fol,ctSys = createFollicle(surf , name = sel+"_follicle"+str(ite+1).zfill(2) ,uPos = .5 , vPos = ite/(total-1.0))
        
        #organize follicle and groups
        cmds.parent (fol,folGrp)
        cmds.parent(ctSys[0],jntMain)
        cmds.parent(ctSys[1],ctMain)
        cmds.parent(ctSys[2],utilMain)
        
        #finding controller to add constraint
        mainG = cmds.listRelatives(ctSys[1],c=1,type="transform")[0]
        
        #storing first two follicle translateX value
        if ite <=1:
            folList.append(cmds.getAttr("%s.tx"%fol)) 
                
        #Create and move feather blend controllers        
        if ite == 0:
            cmds.pointConstraint(fol,secEndG,mo=0,name = "PCCCC1")
            cmds.delete("PCCCC1")
            
        if ite <= secDown:            
            const = cmds.orientConstraint(ctSecEnd,ctSecMid,mainG)[0]
            weightList = cmds.orientConstraint(const,q=1,wal=1)                        
            cmds.setAttr("%s.%s"%(const,weightList[0]) , max(0,1-counterWeight))
            cmds.setAttr("%s.%s"%(const,weightList[1]) , counterWeight)
            
            cmds.connectAttr("%s.microCtrlVis"%ctSecMid,"%s.visibility"%mainG)
            cmds.connectAttr("%s.bend"%ctSecEnd,"%s.input"%ctSys[3])
            cmds.connectAttr("%s.bend"%ctSecMid,"%s.input"%ctSys[4])
            cmds.setAttr("%s.conversionFactor"%ctSys[3],max(0,1-counterWeight) )
            cmds.setAttr("%s.conversionFactor"%ctSys[4],counterWeight )
                        
            counterWeight +=secDownDiff   
                        
            if ite==secDown:
                counterWeight=0  
                cmds.pointConstraint(fol,secMidG,mo=0,name = "PCCCC1")
                cmds.delete("PCCCC1")              
            
            continue 
            
        if ite <= secDown+secUp:            
            const = cmds.orientConstraint(ctSecMid,ctSecStart,mainG)[0]
            weightList = cmds.orientConstraint(const,q=1,wal=1)            
            cmds.setAttr("%s.%s"%(const,weightList[0]) , max(0,1-counterWeight))
            cmds.setAttr("%s.%s"%(const,weightList[1]) , counterWeight)
            
            cmds.connectAttr("%s.microCtrlVis"%ctSecStart,"%s.visibility"%mainG)
            cmds.connectAttr("%s.bend"%ctSecMid,"%s.input"%ctSys[3])
            cmds.connectAttr("%s.bend"%ctSecStart,"%s.input"%ctSys[4])
            cmds.setAttr("%s.conversionFactor"%ctSys[3],max(0,1-counterWeight) )
            cmds.setAttr("%s.conversionFactor"%ctSys[4],counterWeight )
             
            counterWeight +=secUpDiff
            if ite==secDown+secUp:
                counterWeight=0
                cmds.pointConstraint(fol,secStartG,mo=0,name = "PCCCC1")
                cmds.delete("PCCCC1")
                           
            continue
        if ite <= total:            
            const = cmds.orientConstraint(ctSecStart,ctTip,mainG)[0]
            weightList = cmds.orientConstraint(const,q=1,wal=1)            
            cmds.setAttr("%s.%s"%(const,weightList[0]) , max(0,1-counterWeight))
            cmds.setAttr("%s.%s"%(const,weightList[1]) , counterWeight)
            
            cmds.connectAttr("%s.microCtrlVis"%ctTip,"%s.visibility"%mainG)
            cmds.connectAttr("%s.bend"%ctSecStart,"%s.input"%ctSys[3])
            cmds.connectAttr("%s.bend"%ctTip,"%s.input"%ctSys[4])
            cmds.setAttr("%s.conversionFactor"%ctSys[3],max(0,1-counterWeight) )
            cmds.setAttr("%s.conversionFactor"%ctSys[4],counterWeight )  
            
            counterWeight +=priDiff 
                        
            continue
        
                   
    cmds.pointConstraint(fol,tipG,mo=0,name = "PCCCC1")
    cmds.delete("PCCCC1")
    cmds.parent (sel,utilMain)
    cmds.parent (tipG,secStartG,secMidG,secEndG,featherMain)
    
    ##offset controllers to have better visual for further adjustments
    if folList[1]-folList[0] >= 0:                     
        cmds.setAttr("%s.ry"%tipG,-10)
        cmds.setAttr("%s.ry"%secStartG,30)
        cmds.setAttr("%s.ry"%secMidG,70)
    else:
        cmds.setAttr("%s.ry"%tipG,190)
        cmds.setAttr("%s.ry"%secStartG,150)
        cmds.setAttr("%s.ry"%secMidG,115)
    cmds.setAttr("%s.ry"%secEndG,90)
        
    
    cmds.select(cl=1)

def wingRigWindow():
    ###Creating window
    if "wingRigWind" in cmds.lsUI(wnd=1):
        cmds.deleteUI("wingRigWind",wnd=1)
    #cmds.window("wingRigWind",wh=1,q=1)        
    cmds.window("wingRigWind",wh=[400,115],s=0,vis=1,t="Wing Rig Creator")
    cmds.columnLayout("wingRigMainCol",adj=1,p="wingRigWind")
    cmds.textFieldGrp("priFeatherTxt",cl2=['left','left'],text= 6,cw2=[200,200],l="Number of Primary Feather:",p="wingRigMainCol")
    cmds.textFieldGrp("secUpFeatherTxt",cl2=['left','left'],text= 10,cw2=[200,200],l="Number of Secondary Up Feather:",p="wingRigMainCol") 
    cmds.textFieldGrp("secDownFeatherTxt",cl2=['left','left'],text= 6,cw2=[200,200],l="Number of Secondary Down Feather:",p="wingRigMainCol")
    cmds.radioButtonGrp("folPlacementRadio",cw3= [200,100,100],cl3=['left','left','left'],sl=0,l="Place follicle Along",nrb=2,la2=["U","V"],p="wingRigMainCol")
    cmds.rowLayout("wingRigBtRow",nc=2,p="wingRigMainCol") 
    cmds.button("wingRigBtRun",c=mainRun,label = "Create",w=200,p="wingRigBtRow")
    cmds.button("wingRigBtQuit",c="cmds.deleteUI(\"wingRigWind\",wnd=1) ",label = "Cancel",w=200,p="wingRigBtRow")          


if __name__ == '__main__':
    wingRigWindow()
