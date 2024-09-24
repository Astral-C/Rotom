import os
import json
import text
import ndspy.rom
import ndspy.narc
import rotom_map as Map
from rotom_map import RotomMap, RotomMapHeader
import PalkiaPy
import bStream

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
        self.maps = {}

    def openProject(self, projectName):
        #TODO: Clean this up.

        temp = list(filter(lambda p: projectName in p['name'], self.projects))

        if(len(temp) > 0):
            self.currentProject = temp[0]

            self.currentRom = ndspy.rom.NintendoDSRom.fromFile(
                os.path.join("RotomFiles", self.currentProject["folder"], self.currentProject["rom"])
            )

            Map.buildModelNarc = ndspy.narc.NARC(self.currentRom.getFileByName('fielddata/build_model/build_model.narc'))
            Map.mapTexNarc = ndspy.narc.NARC(self.currentRom.getFileByName('fielddata/areadata/area_map_tex/map_tex_set.narc'))
            #Map.defaultMapTex = PalkiaPy.loadNSBTX(data=bytes(Map.mapTexNarc.files[6]))
            
            # The path changes slightly between DP and Pt. 
            # IDK if I will ever implement hgss/bw/bw2 but if I do this will have to change
            self.fieldDataPath = 'fielddata/land_data/land_data' + ('_release' if (self.currentProject["game"] == 'DP') else '') +'.narc'
            
            landData = ndspy.narc.NARC(self.currentRom.getFileByName(self.fieldDataPath))
            matrixArc = ndspy.narc.NARC(self.currentRom.getFileByName('fielddata/mapmatrix/map_matrix.narc'))

            textArc = ndspy.narc.NARC(self.currentRom.getFileByName('msgdata/pl_msg.narc'))
            locationNames = text.decodeList(textArc.files[433])

            arm9 = bStream.bStream(data=self.currentRom.arm9)

            arm9.seek(0xE601C)

            mapHeaders = []
            while(True):
                header = RotomMapHeader(arm9) # these are zone info structs
                if(header.placeNameID > len(locationNames)):
                    break

                mapHeaders.append(header)
            
            
            for location in locationNames:
                print(f"Loading Map for Zone {location}")
                zoneHeaders = []
                for header in mapHeaders:
                    if(locationNames[header.placeNameID] == location):
                        zoneHeaders.append(header)
                self.maps[location] = RotomMap(location, zoneHeaders, landData, matrixArc)




            #First map is Twinleaf Town for dppt, load it by default
            #self.currentMap = RotomMap(self.land_data.files[0], 0)

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