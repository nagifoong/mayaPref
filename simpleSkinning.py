def getSkinCluster( dag):
    """A convenience function for finding the skinCluster deforming a mesh.

    params:
      dag (MDagPath): A MDagPath for the mesh we want to investigate. 
    """

    # useful one-liner for finding a skinCluster on a mesh
    skin_cluster = cmds.ls(cmds.listHistory(dag.fullPathName()), type="skinCluster")

    if len(skin_cluster) > 0:
      # get the MObject for that skinCluster node if there is one
      sel = OpenMaya.MSelectionList()
      sel.add(skin_cluster[0])
      skin_cluster_obj = OpenMaya.MObject()
      sel.getDependNode(0, skin_cluster_obj)

      return skin_cluster[0], skin_cluster_obj

    else:
      raise RuntimeError("Selected mesh has no skinCluster")
      
def defSkinWeight(sel):
    import maya.OpenMaya as OpenMaya
    import maya.OpenMayaAnim as OpenMayaAnim
    import maya.cmds as cmds
    import maya.mel as mel
    
    # poly mesh and skinCluster name
    shapeName = sel#'pCube1'
    smoothing = 0 ### percentage
    #clusterName = 'skinCluster1'
    ##find skin cluster from selected mesh
    selection = OpenMaya.MSelectionList()
    selection.add(shapeName)
    iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)
    
    # get dagPath
    dagPath = OpenMaya.MDagPath()
    iterSel.getDagPath( dagPath )
    
    ## get skin cluster and depend node of it
    ##cmds.ls(cmds.listHistory(dagPath.fullPathName()), type="skinCluster")
    clusterName,clusterNode = getSkinCluster( dagPath)
    
    # get the MFnSkinCluster for clusterName
    
    skinFn = OpenMayaAnim.MFnSkinCluster(clusterNode)
    
    # get the MDagPath for all influence
    infDags = OpenMaya.MDagPathArray()
    skinFn.influenceObjects(infDags)
    
    # create a dictionary whose key is the MPlug indice id and 
    # whose value is the influence list id
    # infs = all joints in current skin cluster
    infIds = {}
    infs = []
    for x in xrange(infDags.length()):
    	infPath = infDags[x].fullPathName()
    	infId = int(skinFn.indexForInfluenceObject(infDags[x]))
    	infIds[infId] = x
    	infs.append(infPath)
    
    # get the MPlug for the weightList and weights attributes
    wlPlug = skinFn.findPlug('weightList')
    wPlug = skinFn.findPlug('weights')
    wlAttr = wlPlug.attribute()
    wAttr = wPlug.attribute()
    wInfIds = OpenMaya.MIntArray()
    
    # the weights are stored in dictionary, the key is the vertId, 
    # the value is another dictionary whose key is the influence id and 
    # value is the weight for that influence
    weights = {}
    for vId in xrange(wlPlug.numElements()):
    	vWeights = {}
    	# tell the weights attribute which vertex id it represents
    	wPlug.selectAncestorLogicalIndex(vId, wlAttr)
    	
    	# get the indice of all non-zero weights for this vert
    	wPlug.getExistingArrayAttributeIndices(wInfIds)
    
    	# create a copy of the current wPlug
    	infPlug = OpenMaya.MPlug(wPlug)
    	for infId in wInfIds:
    		# tell the infPlug it represents the current influence id
    		infPlug.selectAncestorLogicalIndex(infId, wAttr)
    		
    		# add this influence and its weight to this verts weights
    		try:
    			vWeights[infIds[infId]] = infPlug.asDouble()
    		except KeyError:
    			# assumes a removed influence
    			pass
    	weights[vId] = vWeights
    
    ####CLEAN UP SKIN CLUSTER	
    # unlock influences used by skincluster
    for inf in infs:
    	cmds.setAttr('%s.liw' % inf)
    
    # normalize needs turned off for the prune to work
    skinNorm = cmds.getAttr('%s.normalizeWeights' % clusterName)
    if skinNorm != 0:
    	cmds.setAttr('%s.normalizeWeights' % clusterName, 0)
    cmds.skinPercent(clusterName, shapeName, nrm=False, prw=100)
    
    # restore normalize setting
    if skinNorm != 0:
    	cmds.setAttr('%s.normalizeWeights' % clusterName, skinNorm)
    	
    for vertId, weightData in weights.items():
    	wlAttr = '%s.weightList[%s]' % (clusterName, vertId)
    	for infId, infValue in weightData.items():
    		wAttr = '.weights[%s]' % infId
    		cmds.setAttr(wlAttr + wAttr, infValue)
    
    
    ###FINDING VERTICES WORLD POSITION
    # create empty point array
    inMeshMPointArray = OpenMaya.MPointArray()
    
    # create function set and get points in world space
    currentInMeshMFnMesh = OpenMaya.MFnMesh(dagPath)
    currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kWorld)
    		
    for ind,jnt in enumerate(infs):
        #ind = 0
        if ind+1 == len(infs):
            break
            
        skinList = []
        newInfVal = [0 for nullInf in infs]
        cmds.select(cl=1)
        
        jntA = cmds.xform(jnt ,q= 1 ,ws = 1,t =1 )
        jntB = cmds.xform(infs[ind+1] ,q= 1 ,ws = 1,t =1 )
        startV = OpenMaya.MVector(jntA[0] ,jntA[1],jntA[2])
        endV = OpenMaya.MVector(jntB[0] ,jntB[1],jntB[2])
        startEnd = endV - startV
        startEndN = startEnd.normal()
        kStart = startV * startEndN#cmds.xform("locator3",t=( startEndN[0],startEndN[1],startEndN[2]))
        kEnd = endV * startEndN
        totalDistance = float('%f' %(kEnd-kStart))
        
        for i in range(len(weights)):
            #create a list to temporaly
            newInfVal = [0 for nullInf in infs]
            vertLoc = OpenMaya.MVector(inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2])
    
            disStart = kStart-(vertLoc*startEndN)
            disEnd = float('%f' %(kEnd-(vertLoc*startEndN)))
            
            if disStart> 0 or disEnd<0:
                continue
            if disStart<=0 and disEnd>=0:
                ## finding skin weights value for each joint based on distance between joints and vertex
                newInfVal[ind+1] = cmds.gradientControlNoAttr('skinGrad',q=1,vap=disEnd/totalDistance)
                newInfVal[ind] = 1-newInfVal[ind+1]
                ## while smoothing value is not 0, makes all vertex with skin weight 1 share the skin weight to its neighbours
                if smoothing != 0:
                    if newInfVal[ind] ==1 :
                        if ind-1 >= 0:                
                            newInfVal[ind-1] = smoothing
                            newInfVal[ind] -=smoothing
                        if ind+1 < len(infs):                
                            newInfVal[ind+1] = smoothing
                            newInfVal[ind] -=smoothing
                    elif newInfVal[ind+1] ==1:
                        if ind >= 0:                
                            newInfVal[ind] =smoothing
                            newInfVal[ind+1] -=smoothing
                        if ind+2 < len(infs):                
                            newInfVal[ind+2] =smoothing
                            newInfVal[ind+1] -=smoothing
                #print "vertex %s weight %s" %(i,newInfVal)
                ##apply skin weights to each vertex        
                for inf , newVal in enumerate(newInfVal):                
                    wAttr = '%s.weightList[%s].weights[%s]' % (clusterName, i,inf)
                    cmds.setAttr(wAttr,newVal)
    cmds.select(sel)



def gardCC(*n):
    '''
    Changes on gradient control apply to float slider
    '''
    cmds.optionMenu("skinInterMenu",e=1,sl=cmds.gradientControlNoAttr('skinGrad',q=1,civ=1))
    
    currentKey = cmds.gradientControlNoAttr('skinGrad',q=1,ck=1)
    currentYVal = cmds.gradientControlNoAttr('skinGrad',q=1,cvv=1)
    currentXVal = cmds.gradientControlNoAttr('skinGrad',q=1,vap=currentYVal)
    cmds.floatSliderGrp("skinXlocGrp",e=1,v=currentXVal)
    cmds.floatSliderGrp("skinYlocGrp",e=1,v=currentYVal)
    
def floatCC(*n):
    '''
    Changes on float slider apply to gradient control
    '''
    string = cmds.gradientControlNoAttr('skinGrad',q=1,asString=1)
    stringSplit = string.split(",")
    currentKey = cmds.gradientControlNoAttr('skinGrad',q=1,ck=1)
    stringSplit[currentKey*3+1] = str(cmds.floatSliderGrp("skinXlocGrp",q=1,v=1))
    stringSplit[currentKey*3] = str(cmds.floatSliderGrp("skinYlocGrp",q=1,v=1))
    
    cmds.gradientControlNoAttr('skinGrad',e=1,asString=",".join(stringSplit))

import maya.cmds as cmds

if cmds.window('betterSkinWind',q=1,ex=1):
    cmds.deleteUI('betterSkinWind')
    
cmds.window('betterSkinWind',wh=[800,800],s=1,vis=1,t = "Better Skinning Window")
cmds.formLayout("mainCol",nd=100,p='betterSkinWind')
cmds.text("baseTxt",l = "Parent Joint" , p='mainCol')
cmds.text("childTxt",al="right",l = "Child Joint" , p='mainCol')

if not cmds.optionVar(ex='skinningFalloffOptionVar'):
    cmds.optionVar(stringValueAppend=['skinningFalloffOptionVar', '0,1,2'])
    cmds.optionVar(stringValueAppend=['skinningFalloffOptionVar', '1,0,2'])

cmds.gradientControlNoAttr('skinGrad',h=100,p='mainCol',optionVar = 'skinningFalloffOptionVar', cc = gardCC)


cmds.columnLayout("interpCol",p ='mainCol' )
cmds.optionMenu("skinInterMenu", p = 'interpCol',label = "Interpolation",cc="cmds.gradientControlNoAttr('skinGrad',e=1,civ=cmds.optionMenu('skinInterMenu',q=1,sl=1))")
cmds.menuItem(label = "Linear" , p = 'skinInterMenu')
cmds.menuItem(label = "Spline" , p = 'skinInterMenu')
cmds.menuItem(label = "Smooth" , p = 'skinInterMenu')
cmds.menuItem(label = "Stepped" , p = 'skinInterMenu')

cmds.floatSliderGrp("skinXlocGrp",p = 'interpCol',l = "X:",step = .01,cw3=[10,50,100],ad3=3,min=0,max=1,fmn=0,fmx=1, f=1,cc=floatCC ,v= cmds.gradientControlNoAttr('skinGrad',q=1,cvv=1) )

cmds.floatSliderGrp("skinYlocGrp",p = 'interpCol',l = "Y:",step = .01,cw3=[10,50,100],ad3=3,min=0,max=1,fmn=0,fmx=1, f=1,cc=floatCC ,v= cmds.gradientControlNoAttr('skinGrad',q=1,vap=cmds.gradientControlNoAttr('skinGrad',q=1,cvv=1)) )


cmds.button("applyBt",l = "Apply",p='mainCol', c='defSkinWeight(cmds.ls(sl=1)[0])')
cmds.formLayout("mainCol",e=1,af = [('baseTxt','top',5),('baseTxt','left',5),('childTxt','top',5),('childTxt','right',5),('skinGrad','top',30),('skinGrad','left',5),('skinGrad','right',5),('interpCol','left',5),('interpCol','bottom',5),('applyBt','right',5),('applyBt','bottom',5)],
                                ac = [('baseTxt','bottom',5,'skinGrad'),('skinGrad','bottom',5,'interpCol')])


gardCC()

#cmds.optionVar(q='skinningFalloffOptionVar')