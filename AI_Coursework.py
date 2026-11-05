import numpy as np
import random
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plot

SizeOfGrid = 5
#TEST CASE is where the other example can be found, simply uncomment the text case and comment the current one
senses = [
    [(0, 0), "?"], [(0, 1), "?"], [(0, 2), "?"], [(0, 3), "?"], [(0, 4), "?"],# ? for unexplored
    [(1, 0), "?"], [(1, 1), "?"], [(1, 2), "?"], [(1, 3), "?"], [(1, 4), "?"],# B for Breeze
    [(2, 0), "?"], [(2, 1), "?"], [(2, 2), "?"], [(2, 3), "?"], [(2, 4), "?"],# S for Smelly
    [(3, 0), "?"], [(3, 1), "?"], [(3, 2), "?"], [(3, 3), "?"], [(3, 4), "?"],# B/S for Both Breeze and Smelly
    [(4, 0), "?"], [(4, 1), "?"], [(4, 2), "?"], [(4, 3), "?"], [(4, 4), "?"],
]
dangers = [
    [(0, 0), "?"], [(0, 1), "?"], [(0, 2), "?"], [(0, 3), "?"], [(0, 4), "?"],# x for a possible danger
    [(1, 0), "?"], [(1, 1), "?"], [(1, 2), "?"], [(1, 3), "?"], [(1, 4), "?"],# P for Pit
    [(2, 0), "?"], [(2, 1), "?"], [(2, 2), "?"], [(2, 3), "?"], [(2, 4), "?"],# W for Wumpus
    [(3, 0), "?"], [(3, 1), "?"], [(3, 2), "?"], [(3, 3), "?"], [(3, 4), "?"],
    [(4, 0), "?"], [(4, 1), "?"], [(4, 2), "?"], [(4, 3), "?"], [(4, 4), "?"],
]
RiskyNodes = []
SafePath = [(0,0)]# here we are setting up the lists which we will be using to make decisions
Travelled = [(0,0)]# riskynodes are areas which are possibly dangerous hence are risky,
Explored = [(0,0)]#safepath and explored are both areas which are safe and have been visited by the agent
MACHINE_GUN_POS = (0,4)                             # we have had to hardcode the dangerpoints for the agent for the machine gun 
MACHINE_GUN_DANGER = [(0,3), (0,4), (1,3), (1,4)]   # this is due to running out of time to test and debug the hazard

# TEST CASE
#MACHINE_GUN_POS = (4,0)
#MACHINE_GUN_DANGER = [(3,0), (3,1), (4,2)]

WUMPUS = "W"
PIT = "P"   #we labelled everything which will appear in the grid itself visually and the textgrid, which will help the agent identify what sense it has come across
GOLD = "G"
BREEZE = "B"
SMELLY = "S"
SMELLY_BREEZE = "B/S"
MACHINE_GUN = "M"
VIBRATION = "V"

def GridCreation():
    TextGrid = np.full((SizeOfGrid,SizeOfGrid), "?")
    ColourGrid = np.zeros((SizeOfGrid, SizeOfGrid), dtype=int)

    BreezeList = []                 # these lists are used to check whether breezes and smells share any coordinates, if they do they become a smelly breeze as shown below
    SmellyList = []


    #TEST CASE
    #    Pits = [(1,3)]
    Pits = [(3,1)]
    for column, row in Pits:
        TextGrid[column,row] = PIT
        if  (column-1,row) not in Pits and (column-1)>-1:   #here we are making sure that anything adjacent to the pit in any direction that is within the bounds of the
            TextGrid[column-1,row] = BREEZE
            BreezeList.append((column-1,row))               # grid is a breeze
        if  (column+1,row) not in Pits and (column+1)<5:
            TextGrid[column+1,row] = BREEZE
            BreezeList.append((column+1,row))
        if  (column,row-1) not in Pits and (row-1)>-1:      # we use the same method for the wumpus below
            TextGrid[column,row-1] = BREEZE
            BreezeList.append((column,row-1))
        if  (column,row+1) not in Pits and (row+1)<5:
            TextGrid[column,row+1] = BREEZE
            BreezeList.append((column,row+1))

    wumpuslocation = (4,4)
    TextGrid[wumpuslocation[0],wumpuslocation[1]] = WUMPUS
    if  (wumpuslocation[0]-1)>-1:
        TextGrid[wumpuslocation[0]-1,wumpuslocation[1]] = SMELLY
        SmellyList.append((wumpuslocation[0]-1,wumpuslocation[1]))
    if  (wumpuslocation[0]+1)<5:
        TextGrid[wumpuslocation[0]+1,wumpuslocation[1]] = SMELLY
        SmellyList.append((wumpuslocation[0]+1,wumpuslocation[1]))
    if  (wumpuslocation[1]-1)>-1:
        TextGrid[wumpuslocation[0],wumpuslocation[1]-1] = SMELLY
        SmellyList.append((wumpuslocation[0],wumpuslocation[1]-1))
    if  (wumpuslocation[1]+1)<5:
        TextGrid[wumpuslocation[0],wumpuslocation[1]+1] = SMELLY
        SmellyList.append((wumpuslocation[0],wumpuslocation[1]+1))
    
    for breezeindex in BreezeList:
        for smellyindex in SmellyList:
            if breezeindex == smellyindex:
                TextGrid[breezeindex[0],breezeindex[1]] = SMELLY_BREEZE


    Mcolumn,Mrow = MACHINE_GUN_POS
    if (Mcolumn-1)>-1:                              # here we do the same thing for machine gun
        TextGrid[Mcolumn-1,Mrow] = VIBRATION
    if  (Mcolumn+1)<5:
        TextGrid[Mcolumn+1,Mrow] = VIBRATION
    if (Mrow-1)>-1:
        TextGrid[Mcolumn,Mrow-1] = VIBRATION
    if  (Mrow+1)<5:
        TextGrid[Mcolumn,Mrow+1] = VIBRATION

    Mcolumn, Mrow = MACHINE_GUN_POS
    TextGrid[Mcolumn,Mrow] = MACHINE_GUN

#   TEST CASE
#    TextGrid[3,3] = GOLD

    TextGrid[2,0] = GOLD
    return TextGrid, ColourGrid             # setting up the GOLD position in the grid so it can be recognised by the agent and the grid creator

OnScreenGrid, axes = plot.subplots()        # setting up the grid
plot.ion()

AgentLocation = (0,0)
Alive = True
MachineGunEncountered = False

def InGunfire(pos):                                 #this function checks if the agent is within firing range if it is it returns true
    DeathFromGunfire = pos in MACHINE_GUN_DANGER
    return DeathFromGunfire

def AvoidMachineGunDangers(pos):                # this function makes sure the agent avoids any area which is near the machine gun so it doesnt die
    InGunfireRange = pos in MACHINE_GUN_DANGER
    return InGunfireRange

def ClosestRiskyNode(CurrentPos):
    column, row = CurrentPos
    LowestDistance = 100
    ClosestCoordinate = (0,0)
    ThreatLevelOne = False                  #this checks what is the closest node that is risky, we use this when there are no longer an safe nodes to travel to 
    for RiskyDistance in RiskyNodes:
        if RiskyDistance[1] == 1:
            Rcolumn, Rrow = RiskyDistance[0]
            CurrentDistance = abs(Rcolumn - column) + abs(Rrow - row)       # use the absolute distance to determine which is closest
            if CurrentDistance < LowestDistance:                            # we also check how risky this node is the lower the number the less risky it is
                LowestDistance = CurrentDistance                             # this is because it has been flagged by the agent x times, x representing the number at
                ClosestCoordinate = Rcolumn,Rrow                            #RiskyNode[1]
                ThreatLevelOne = True
        elif RiskyDistance[1] == 2 and ThreatLevelOne == False:            # we also check whether its closer than another riskynode
            Rcolumn, Rrow = RiskyDistance[0]
            CurrentDistance = abs(Rcolumn - column) + abs(Rrow - row)
            if CurrentDistance < LowestDistance:
                LowestDistance = CurrentDistance
                ClosestCoordinate = Rcolumn,Rrow
    return ClosestCoordinate, ThreatLevelOne #returned so the agent knows which node it should travel to next

def DisproveRiskyNodes():
    if len(RiskyNodes) > 0:
        NodeNeighbours = []
        for PossibleDanger in RiskyNodes[:]: # disprove is used to get rid of nodes which arent risky such as nodes we have already explored
            NodeNeighbours = []
            node, level = PossibleDanger  # also if any node has a safe node around it there is a good chance that it is not dangerous
            column, row = node
            if column+1 < 5:
                NodeNeighbours.append((column+1,row))
            if column-1 > -1:
                NodeNeighbours.append((column-1,row))           
            if row+1 < 5:
                NodeNeighbours.append((column,row+1))        
            if row-1 > -1:
                NodeNeighbours.append((column,row-1))
            for NeighIndex in NodeNeighbours:
                if NeighIndex in Explored:
                    for SenseNode, SenseCaptured in senses:
                        if SenseNode == NeighIndex and (SenseCaptured == "?" or SenseCaptured == "N") and len(RiskyNodes)>0 and NeighIndex in RiskyNodes:
                            RiskyNodes.remove(PossibleDanger)
    DefiniteDangers = []
    SensesRiskyNeighbours = []
    for SenseCheck in senses[:]:
        SensesRiskyNeighbours = []
        SensenodeR, SenseCapturedR = SenseCheck
        column, row = SensenodeR
        if SenseCapturedR != "?" and SenseCapturedR != "N":
            for dangernum, checkdangers in enumerate(dangers):
                DangerNode, DangerThreat = checkdangers
                for risknodesA in RiskyNodes[:]:
                    nodeA, levelA = risknodesA
                    columnA,rowA = nodeA
                    if columnA+1 < 5 and rowA+1<5 and (columnA+1,rowA+1) == DangerNode and DangerThreat == "P":
                        dangers[dangernum][1] = "?"
                        RiskyNodes.remove(risknodesA)
                    if columnA-1 > -1 and rowA+1<5 and (columnA-1,rowA+1) == DangerNode and DangerThreat == "P":
                        dangers[dangernum][1] = "?"
                        RiskyNodes.remove(risknodesA)
                    if rowA-1 > -1 and columnA+1<5 and (columnA+1,rowA-1) == DangerNode and DangerThreat == "P":
                        dangers[dangernum][1] = "?"
                        RiskyNodes.remove(risknodesA)
                    if rowA-1 > -1 and columnA-1>-1 and(columnA-1,rowA-1) == DangerNode and DangerThreat == "P":
                        dangers[dangernum][1] = "?"
                        RiskyNodes.remove(risknodesA)
    
    

def PathNavigation(CurrentPos,DestinationPos):
    global AgentLocation
    LocationNotMoving = []
    Ccolumn, Crow = CurrentPos    #pathnavigation is used to find the fastest way to the destination node, we need to use the global variable for agentlocation so that we
    Dcolumn, Drow = DestinationPos # can edit it, the comapre all lists are used to check all the safe nodes to use to get somewhere and if there are none we use risky nodes
    CompareAll = []                # the aim is to make sure to use risky nodes as a last resort
    CompareAllRisk = []
    hasMoved = False
    DistanceToDestination = abs(Dcolumn - Ccolumn) + abs(Drow - Crow) # we use this to ensure that the node we choose is closer and not further away from the destination
    while DistanceToDestination != 0:
        CompareAll = []
        CompareAllRisk = []
        hasMoved = False
        if Ccolumn+1 < 5:
            Distance1 = abs(Dcolumn - (Ccolumn+1)) + abs(Drow - Crow)
            Pos1 = Ccolumn+1,Crow
            CompareAll.append([Distance1,Pos1])
            CompareAllRisk.append([Distance1,Pos1])
        if Ccolumn-1 > -1:
            Distance2 = abs(Dcolumn - (Ccolumn-1)) + abs(Drow - Crow)
            Pos2 = Ccolumn-1,Crow
            CompareAll.append([Distance2,Pos2])
            CompareAllRisk.append([Distance2,Pos2])            
        if Crow+1 < 5:
            Distance3 = abs(Dcolumn - Ccolumn) + abs(Drow - (Crow+1))           # adding all the possible nodes we can use to the list
            Pos3 = Ccolumn,Crow+1
            CompareAll.append([Distance3,Pos3])
            CompareAllRisk.append([Distance3,Pos3])            
        if Crow-1 > -1:
            Distance4 = abs(Dcolumn - Ccolumn) + abs(Drow - (Crow-1))
            Pos4 = Ccolumn,Crow-1
            CompareAll.append([Distance4,Pos4])
            CompareAllRisk.append([Distance4,Pos4])
            
        for RDistance, RPos in CompareAll[:]:
            if AvoidMachineGunDangers(RPos) == True:            #removing risky nodes so only the safe node remain
                CompareAll.remove([RDistance,RPos])
                continue
            for PossibleDangerNode in RiskyNodes:
                if RPos in PossibleDangerNode:
                    CompareAll.remove([RDistance,RPos])
                if PossibleDangerNode[0] in Explored:
                    RiskyNodes.remove(PossibleDangerNode)
        for Distance, Pos in CompareAll:
            if Distance<DistanceToDestination and CheckDandSRisky(Pos[0],Pos[1]) == True:
                DistanceToDestination = Distance
                CurrentPos = Pos
                x, y = Pos
                if TextGrid[x,y] == BREEZE:         # checks if any the agent senses anything and reports it to updatesenses so that the position of this sense can be updated
                    print("AGENT FEELS A BREEZE")   # into the senses list
                    UpdateSenses(Pos,"B")           # also add to explored since senses arent dangerous themselves
                    if Pos not in Explored:
                        Explored.append(Pos)
                elif TextGrid[x,y] == SMELLY:
                    print("AGENT SMELLS A STINKY ODOUR")
                    UpdateSenses(Pos,"S")
                    if Pos not in Explored:
                        Explored.append(Pos)
                elif TextGrid[x,y] == SMELLY_BREEZE:
                    print("AGENT DETECTS A SMELLY BREEZE")
                    UpdateSenses(Pos,"B/S")
                    if Pos not in Explored:
                        Explored.append(Pos)
                    break
                elif TextGrid[x,y] == VIBRATION:
                    print("AGENT FEELS A VIBRATION")
                    UpdateSenses(Pos,"V")
                    if Pos not in Explored:
                        Explored,append(Pos)
            else:
                LocationNotMoving.append(CurrentPos)
        if 0<len(LocationNotMoving) or len(CompareAll) == 0:                        # here we use risky nodes as we have no choice
            if len(LocationNotMoving)>1:
                if LocationNotMoving[-1] == LocationNotMoving[-2]:
                    hasMoved = False
            for DistanceRisk, PosRisk in CompareAllRisk:
                if AvoidMachineGunDangers(RPos) == True:
                    continue 
                if DistanceRisk<DistanceToDestination and CheckDandSRisky(PosRisk[0],PosRisk[1]) == True:
                    DistanceToDestination = DistanceRisk
                    CurrentPos = PosRisk
                    break
        AgentLocation = CurrentPos                      # here we update currentpos so agentlocation can be updated and so it can move to the next square
        Travelled.append(CurrentPos)
        Ccolumn, Crow = CurrentPos
        if CurrentPos not in Explored:
            Explored.append(CurrentPos)
        for NavCheck in RiskyNodes:                     # adding to explored and removing any risky nodes
            RiskNodeExploredOrNot, risklevel = NavCheck
            if RiskNodeExploredOrNot in Explored:
                RiskyNodes.remove(NavCheck)
        DisproveRiskyNodes()
        GridDrawing(TextGrid, ColourGrid, AgentLocation) #updating the agent's location on the map
        print("Agent is at ",CurrentPos)
        if CurrentPos == DestinationPos:            # only exit while loop once the agent has reached its destination
            break
            

def ExploredOrNot(column,row):
    currentPos = column,row
    ExploredPosition = False
    for explorecheck in Explored:
        if explorecheck == currentPos:          # simply used to check if a node has been explored or not by checking the list, returns true if it has been and false if not
            ExploredPosition = True
    return ExploredPosition

def CheckDandS(column,row):
    possiblepos = column,row
    Safe = True                 
    if AvoidMachineGunDangers(possiblepos) == True and MachineGunEncountered == True:
        return False
    for checksenses in senses:
        if checksenses[0] == possiblepos and checksenses[1] != "?":         # checks if the node the agent is going to travel to is safe, to make sure it avoids risky nodes
            Safe = False                                                    # where possible
    for checkdangers in dangers:
        if checkdangers[0] == possiblepos and checkdangers[1] != "?":
            Safe = False
    return Safe

def CheckDandSRisky(column,row):
    possiblepos = column,row
    Safe = True
    if AvoidMachineGunDangers(possiblepos) == True and MachineGunEncountered == True: #simular to the previous function but this makes sure the agent avoids actual dangers
        return False                                                          # everything else is considered safe, we use this when we cannot explore any more nodes that seem
    for checkdangerLocation, checkdangerwarning in dangers:                   #  safe
        if checkdangerLocation == possiblepos and checkdangerwarning in ["P","W"]:
            Safe = False
    return Safe
        
def UnExploredNeighbours(currentPos):
    column,row = currentPos # this check whether a node has any neighbours which it hasnt explored yet, we use this to determine where to go next if the agent has seemingly
    NewNeighbours = False   # ran out of options
    NewPos = (0,0)
    RiskyCoordinates = [r[0] for r in RiskyNodes]
    if currentPos in RiskyCoordinates:
        if column+1 < 5 and ExploredOrNot(column+1,row) == False and CheckDandSRisky(column+1,row) == True:
            NewNeighbours = True
            NewPos = (column+1,row) #makes sure its within the grid hasnt been explored and is safe, and checks the safe nodes before the risky nodes
        elif column-1 > -1 and ExploredOrNot(column-1,row) == False and CheckDandSRisky(column-1,row) == True:
            NewNeighbours = True
            NewPos = (column-1,row)
        elif row+1 < 5 and ExploredOrNot(column,row+1) == False and CheckDandSRisky(column,row+1) == True:
            NewNeighbours = True
            NewPos = (column,row+1)
        elif row-1 > -1 and ExploredOrNot(column,row-1) == False and CheckDandSRisky(column,row-1) == True:
            NewNeighbours = True
            NewPos = (column,row-1)
    else:
        if column+1 < 5 and ExploredOrNot(column+1,row) == False and CheckDandS(column+1,row) == True:
            NewNeighbours = True
            NewPos = (column+1,row)
        elif column-1 > -1 and ExploredOrNot(column-1,row) == False and CheckDandS(column-1,row) == True:
            NewNeighbours = True
            NewPos = (column-1,row)
        elif row+1 < 5 and ExploredOrNot(column,row+1) == False and CheckDandS(column,row+1) == True:
            NewNeighbours = True
            NewPos = (column,row+1)
        elif row-1 > -1 and ExploredOrNot(column,row-1) == False and CheckDandS(column,row-1) == True:
            NewNeighbours = True
            NewPos = (column,row-1)
    return NewNeighbours,NewPos # we set the values to default values as well so if nothing matches the if and elif statements, we can confirm that there are no neighbours to 
                                                    # explore, otherwise the new node to explore is returned and true is returned to show that the area has neighbours
def CorrectMovement(CurrentPosition, NextPosition):
    nowColumn, nowRow = CurrentPosition
    NextColumn, NextRow = NextPosition
    AcceptablePosition = False
    NewPos = (0,0)
    if nowColumn+1 < 5 and nowColumn+1 == NextColumn:
        AcceptablePosition = True
        NewPos = nowColumn+1,nowRow                     #simply checks if the movement is within the grid and suggests where to go first, as this suggests right, up, left
    elif nowColumn-1 > -1 and nowColumn-1 == NextColumn: # and then down as the options for where the agent could move to next
        AcceptablePosition = True
        NewPos = nowColumn-1,nowRow
    elif nowRow+1 < 5 and nowRow+1 == NextRow:
        AcceptablePosition = True
        NewPos = nowColumn,nowRow+1
    elif nowRow-1 > -1 and nowRow-1 == NextRow:
        AcceptablePosition = True
        NewPos = nowColumn,nowRow-1
    return AcceptablePosition, NewPos

def UpdateDangers(DangerousLocation,ConfirmedDanger):
    dangerousLocations = []
    column, row = DangerousLocation
    if column+1 < 5:
        dangerousLocations.append((column+1,row))
    if column-1 > -1:
        dangerousLocations.append((column-1,row)) # this is used to determine what squares around the sense node could be dangerous
    if row+1 < 5:
        dangerousLocations.append((column,row+1))
    if row-1 > -1:
        dangerousLocations.append((column,row-1))


    for SafeNodeCheckIndex in SafePath:
        for threatsindex in dangerousLocations[:]:
            if SafeNodeCheckIndex == threatsindex:  #eliminates any safenodes since they cannot be dangerous
                dangerousLocations.remove(threatsindex)


    for UpdateDangersIndex, elementDanger in enumerate(dangers):
        for threatsindex in dangerousLocations:
            if elementDanger[0] == threatsindex:    #essentially if there is only one node around the sense that could be dangerous, we assume it is dangerous
                if len(dangerousLocations) == 1:
                    dangers[UpdateDangersIndex][1] = ConfirmedDanger
                else:
                    matchingDanger = False
                    dangers[UpdateDangersIndex][1] = "x"# otherwise we mark the riskynodes with an x in dangers so the agent avoids them when it can
                    for MultipleRisksIndex, elementRisk in enumerate(RiskyNodes):
                        if elementRisk[0] == threatsindex:
                            RiskyNodes[MultipleRisksIndex][1] += 1 ## adding 1 for each time the agent believes the square is dangerous, helps determine which nodes
                            matchingDanger = True               # are the most dangerous
                    if not matchingDanger:
                        RiskyNodes.append([threatsindex,1])
                                  
def UpdateSenses(Location,Threat):
    if Threat == "B":
        Danger = "P"
    elif Threat == "S":
        Danger = "W"
    elif Threat == "B/S":
        Danger = "W"
    elif Threat == "V":
        Danger = "M"
        global MachineGunEncountered
        MachineGunEncountered = True                # if a vibration was encounter it is automatically assumed to be dangerous, and we also encountered the machinegun
        for GunfireRisk in MACHINE_GUN_DANGER:      # so we will avoid anything near it from now on as otherwise the agent will die
            for UpdateDangerIndex, elementDanger in enumerate(dangers):
                if GunfireRisk == elementDanger[0]:
                    dangers[UpdateDangerIndex][1] = "M"
        for UpdateSensesIndex, checkelement in enumerate(senses):
            if Location == checkelement[0]: # we make sure to update which node had a breeze so we can use that later on
                senses[UpdateSensesIndex][1] = Threat
        return
    elif Threat == "N":
        Danger = "?"
    for UpdateSensesIndex, checkelement in enumerate(senses):
        if Location == checkelement[0]:
            senses[UpdateSensesIndex][1] = Threat # here we update danger with the node where we sensed something and also what the danger could be based off our sense
            UpdateDangers(senses[UpdateSensesIndex][0],Danger)# this is shown above in the if sense is equal to x

def MoveDirection(CurrentPosition): #suggests to the agent where to go next based off if its safe and unexplored
    column, row = CurrentPosition
    if row+1 < 5 and CheckDandS(column,row+1) == True and ExploredOrNot(column,row+1) == False:
        CurrentPosition = column,row+1
    elif column+1 < 5 and CheckDandS(column+1,row) == True and ExploredOrNot(column+1,row) == False:
        CurrentPosition = column+1,row
    elif row-1 > -1 and CheckDandS(column,row-1) == True and ExploredOrNot(column,row-1) == False:
        CurrentPosition = column,row-1
    elif column-1 > -1 and CheckDandS(column-1,row) == True and ExploredOrNot(column-1,row) == False:
        CurrentPosition = column-1,row
    return CurrentPosition

def DeathByGunfire(pos, gunfire):
    DeathByMachinegun = False
    if gunfire == True and InGunfire(pos) == True: # checks if agent is within the machine gun danger zone when the gun is firing
        DeathByMachinegun = True
    return DeathByMachinegun

def Movement():
    foundGold = False
    moves = 0 # counts the moves taken, used for machine gun
    global AgentLocation # we have the agent location so we can update it and the alive variable so we can update it incase the agent dies
    global Alive
    AllSafeNodesComplete = False
    RiskCount = 1
    RiskyPos = False # riskypos is true once we move to a risky square
    while foundGold == False and Alive == True: # we loop until we find gold or the agent dies
        Active_MachineGun_Gunfire = False
        TextGrid, ColourGrid = GridCreation() # update grid visually
        if MachineGunEncountered == True: # when we encounter the machine gun, it will fire every other turn
            Active_MachineGun_Gunfire = (moves % 2 == 1)
            print("MachineGun is firing bullets!")

        AlreadyKnewAboutGun = any(
            s[0] == AgentLocation and s[1] == "V" # checks if the agent has visited the vibrating area
            for s in senses
       )
        if DeathByGunfire(AgentLocation,Active_MachineGun_Gunfire) == True and AlreadyKnewAboutGun == True: # if the agent is within firing range when the machine gun is 
            Alive = False                                   # firing then it will die
            GridDrawing(TextGrid, ColourGrid, AgentLocation)
            print("AGENT IS DEAD :(")
            break
        if TextGrid[AgentLocation[0],AgentLocation[1]] == GOLD:# checks if the agent has found gold, if it has it can go to the start and win
            foundGold = True
            print("Found GOLD")
            GridDrawing(TextGrid, ColourGrid, AgentLocation)# update the grid
            PathNavigation(AgentLocation,(0,0))
        DisproveRiskyNodes()
        for checkindex, checkelement in enumerate(senses):
            if senses[checkindex][0] == MoveDirection(AgentLocation):
                CoordinatePos = checkindex # gets the index so we can used that to check whether the area is safe to move to, 
        if senses[CoordinatePos][1] == "?" and dangers[CoordinatePos][1] == "?" and senses[CoordinatePos][0] != AgentLocation and RiskyPos == False:
            AgentLocation = MoveDirection(AgentLocation)# enter and move to next square if its safe
            print("Agent is at ",AgentLocation)
            if TextGrid[AgentLocation[0],AgentLocation[1]] == BREEZE: # like earlier we will be checking if the agent has sensed anything after moving it
                print("AGENT FEELS A BREEZE")
                UpdateSenses(AgentLocation,"B")
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
                Travelled.append(AgentLocation)
            elif TextGrid[AgentLocation[0],AgentLocation[1]] == SMELLY:
                print("AGENT CAN SMELLY SOMETHING STINKY") #    add to explored and travelled if its not in the list
                UpdateSenses(AgentLocation,"S")
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
                Travelled.append(AgentLocation)
            elif TextGrid[AgentLocation[0],AgentLocation[1]] == SMELLY_BREEZE:
                print("AGENT FEELS A BREEZE AND CAN SMELL A STINK")
                UpdateSenses(AgentLocation,"B/S")
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
                Travelled.append(AgentLocation)
            elif TextGrid[AgentLocation[0],AgentLocation[1]] == VIBRATION:
                UpdateSenses(AgentLocation, "V")
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
                Travelled.append(AgentLocation)
                AgentLocation = Travelled[-2]
                print("AGENT FEELS A VIBRATION, RETREAT!!!")
                
            elif TextGrid[AgentLocation[0],AgentLocation[1]] == GOLD:
                foundGold = True
                GridDrawing(TextGrid, ColourGrid, AgentLocation)
                Travelled.append(AgentLocation)
                PathNavigation(AgentLocation,(0,0))
            else:
                column, row = AgentLocation
                if row+1 < 5 and (column,(row+1)) not in SafePath:
                    if (column,(row+1)) not in SafePath:
                        SafePath.append((column,(row+1)))
                if column+1 < 5 and ((column+1),row) not in SafePath: # adds anyhting around it that is adajcent as safe since this isnt a sense square
                    if ((column+1),row) not in SafePath:
                        SafePath.append(((column+1),row))
                if row-1 > -1 and (column,(row-1)) not in SafePath:
                    if (column,(row-1)) not in SafePath:
                        SafePath.append((column,(row-1)))
                if column-1 > -1 and ((column-1),row) not in SafePath:
                    if ((column-1),row) not in SafePath:
                        SafePath.append(((column-1),row))

                Travelled.append(AgentLocation)
                if AgentLocation not in SafePath:
                    SafePath.append(AgentLocation)
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)

                for SafeNode in SafePath:
                    for PossibleDangerNode in RiskyNodes:
                        if SafeNode in PossibleDangerNode:
                            RiskyNodes.remove(PossibleDangerNode)
                

        elif RiskyPos == True:
            RiskyPos = False
            if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
            if TextGrid[AgentLocation[0],AgentLocation[1]] == BREEZE: # we do the same thing for the risky node, but we need a seperate one otherwise we cannot enter it
                UpdateSenses(AgentLocation,"B")
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
                Travelled.append(AgentLocation)
            elif TextGrid[AgentLocation[0],AgentLocation[1]] == SMELLY:
                UpdateSenses(AgentLocation,"S")
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
                Travelled.append(AgentLocation)
            elif TextGrid[AgentLocation[0],AgentLocation[1]] == SMELLY_BREEZE:
                UpdateSenses(AgentLocation,"B/S")
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
                Travelled.append(AgentLocation)
            elif TextGrid[AgentLocation[0], AgentLocation[1]] == VIBRATION:
                UpdateSenses(AgentLocation, "V")
                if AgentLocation not in Explored:
                    Explored.append(AgentLocation)
                Travelled.append(AgentLocation) 
            else:
                Travelled.append(AgentLocation)
                SafePath.append(AgentLocation)
        
        else:
            AllSafeNodesComplete = True
            for unexplorednodesquestion in Explored: #checks if theres any other nodes it can explore since everything around is not seen as safe
                Neighbours, NewLocation = UnExploredNeighbours(unexplorednodesquestion)
                if Neighbours == True:
                    AllSafeNodesComplete = False
                    break
                
            if  AllSafeNodesComplete == True: # if theres no safe node to go to we will go to a risky node instead
                NextNode, LevelOne = ClosestRiskyNode(AgentLocation)
                Level = 0
                if LevelOne == True:
                    Level = 1
                else:
                    Level = 2
                StartLocation = AgentLocation
                PathNavigation(StartLocation,NextNode)# agent travels to this risky node
                if [NextNode,Level] in RiskyNodes:  
                    RiskyNodes.remove([NextNode,Level])# we remove the node from risky nodes since we have travelled to it
                RiskyPos = True

            else:
                NothingtoExplore = True
                for backback in Explored:# here if we got something to explre then we use this, and if nothing can be found we return to zero
                    NotNeighbours, NotNewLocation = UnExploredNeighbours(backback)
                    if NotNeighbours == True:
                        NothingtoExplore = False
                        StartLocation = AgentLocation
                        PathNavigation(StartLocation,NotNewLocation)
                        break
                if NothingtoExplore == True:
                    StartLocation = AgentLocation
                    PathNavigation(StartLocation,(0,0))
        moves += 1
        GridDrawing(TextGrid, ColourGrid, AgentLocation)
    GridDrawing(TextGrid, ColourGrid, AgentLocation) # update grid position

    if Alive == True:
        print("FOUNDDDDDDDDDDD THE GOLDDDDDDDD XD")


def GridDrawing(TextGrid, ColourGrid, AgentLocation):
    axes.clear()
    cmap = plot.get_cmap('tab10', 10)
    TemporaryGrid = np.copy(ColourGrid)
    column, row = AgentLocation
    TemporaryGrid[column,row] = 4

    for column in range(SizeOfGrid):
        for row in range(SizeOfGrid):
            text = "?"

            if TextGrid[column, row] == SMELLY_BREEZE:
                text = "B/S"
                TemporaryGrid[column,row] = 9
                axes.text(row, column, text, ha='center', va='center', fontsize=12)
            elif TextGrid[column, row] == MACHINE_GUN:
                text = "M"
                TemporaryGrid[column,row] = 6
                axes.text(row, column, text, ha='center', va='center', fontsize=12)
            elif TextGrid[column, row] == VIBRATION:
                text = "V"
                TemporaryGrid[column,row] = 5
                axes.text(row, column, text, ha='center', va='center', fontsize=12)
            elif TextGrid[column, row] == PIT:
                text = "P"
                TemporaryGrid[column,row] = 1
                axes.text(row, column, text, ha='center', va='center', fontsize=12)
            elif TextGrid[column, row] == WUMPUS:
                text = "W"
                TemporaryGrid[column,row] = 2
                axes.text(row, column, text, ha='center', va='center', fontsize=12)
            elif TextGrid[column, row] == BREEZE:
                text = "B"
                TemporaryGrid[column,row] = 3
                axes.text(row, column, text, ha='center', va='center', fontsize=12)
            elif TextGrid[column, row] == SMELLY:
                text = "S"
                TemporaryGrid[column,row] = 7
                axes.text(row, column, text, ha='center', va='center', fontsize=12)
            elif TextGrid[column, row] == GOLD:
                text = "G"
                TemporaryGrid[column,row] = 9
            if (column, row) == AgentLocation:
                text = "Agent"
            axes.text(row, column, text, ha='center', va='center', fontsize=12)
    axes.imshow(TemporaryGrid, cmap=cmap, vmin=0, vmax=10,origin='lower')
    axes.set_xticks(range(SizeOfGrid))
    axes.set_yticks(range(SizeOfGrid))
    plot.draw()
    plot.pause(0.1)

TextGrid, ColourGrid = GridCreation()
state = (0, 0)
Movement()
GridDrawing(TextGrid, ColourGrid, state)
plot.ioff()
plot.show()
