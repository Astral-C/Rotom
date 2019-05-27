import os
import json
import ndspy.rom
import ndspy.narc
from rotom_map import RotomMap

class RotomEditor():
    def __init__(self):
        if(os.path.isdir("RotomFiles")):
            self.projects = json.load(open(os.path.join("RotomFiles", "projects.json")))["Projects"]

        else:
            os.mkdir("RotomFiles")
            #TODO: create projects.json file if one doesn't exist
        
        self.currentProject = None
        self.currentRom = None
        self.land_data = None
        self.currentMap = None

    def openProject(self, projectName):
        #TODO: Clean this up.

        temp = list(filter(lambda p: projectName in p['name'], self.projects))

        if(len(temp) > 0):
            self.currentProject = temp[0]

            self.currentRom = ndspy.rom.NintendoDSRom.fromFile(
                os.path.join("RotomFiles", self.currentProject["folder"], self.currentProject["rom"])
            )

            # The path changes slightly between DP and Pt. 
            # IDK if I will ever implement hgss/bw/bw2 but if I do this will have to change
            self.fieldDataPath = 'fielddata/land_data/land_data' + ('_release' if (self.currentProject["game"] == 'DP') else '') +'.narc'
            
            self.land_data = ndspy.narc.NARC(self.currentRom.getFileByName(self.fieldDataPath))

            #First map is Twinleaf Town for dppt, load it by default
            self.currentMap = RotomMap(self.land_data.files[0], 0)

            return True
        else:
            return False

    def setCurrentMap(self, mapID):
        self.currentMap = RotomMap(self.land_data.files[mapID], mapID)

    def saveCurrentMap(self):
        self.land_data.files[self.currentMap.id] = self.currentMap.saveMap(self.land_data.files[self.currentMap.id])
        self.currentRom.setFileByName(self.fieldDataPath, self.land_data.save())

    def getCurrentMap(self):
        return self.currentMap

    def saveProject(self):
        #TODO: add map/rom backup functions
        self.currentRom.saveToFile(os.path.join("RotomFiles", self.currentProject["folder"], self.currentProject["rom"]))