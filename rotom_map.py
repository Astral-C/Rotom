import bStream
import PalkiaPy
import ndspy.rom
import ndspy.narc

from pyrr import matrix44, Matrix44, Vector4, Vector3, Quaternion

loadedModels = {}
buildModelNarc = None
mapTexNarc = None
defaultMapTex = None

mapTextures = {}

class RotomMapObject:
	def __init__(self, strm=None):
		if(strm != None):
			self.modelID = strm.readUInt32()
			
			if(buildModelNarc != None and self.modelID not in loadedModels):
				loadedModels[self.modelID] = PalkiaPy.loadNSBMD(data=bytes(buildModelNarc.files[self.modelID]))

			self.x = (float(strm.readInt32() / (1 << 12)))
			self.y = (float(strm.readInt32() / (1 << 12)))
			self.z = (float(strm.readInt32() / (1 << 12)))

			#these most definatley have meaning, don't know what yet.
			self.misc = strm.fhandle.read(32)
		else:
			self.modelID = 0
			self.x = 0
			self.y = 0
			self.z = 0

			#these most definatley have meaning, don't know what yet.
			self.misc = bytes(32)

	
	def __str__(self):
		return "Model ID: {0}".format(self.modelID)

	def write(self, strm):
		strm.writeUInt32(self.modelID)
		strm.writeInt32((int(self.x * (1 << 12))))
		strm.writeInt32((int(self.y * (1 << 12))))
		strm.writeInt32((int(self.z * (1 << 12))))

		strm.fhandle.write(self.misc)

class RotomAreaData:
	def __init__(self, data):
		stream = bStream.bStream(data=data)
		self.buildingSet = stream.readUInt16()
		self.mapTileset = stream.readUInt16()
		self.unknown = stream.readUInt16()
		self.lightType = stream.readUInt16()
		

class RotomMapHeader:
	def __init__(self, stream, areaDataArc):
		self.areaID = stream.readUInt8()
		print(f"Loading Area {self.areaID}")
		if(self.areaID < len(areaDataArc.files)):
			self.areData = RotomAreaData(areaDataArc.files[self.areaID])
		else:
			self.areaID = None
		self.moveModelID = stream.readUInt8()
		self.matrixID = stream.readUInt16()
		self.scriptID = stream.readUInt16()
		self.spScriptID = stream.readUInt16()
		self.msgID = stream.readUInt16()
		self.bgmDayID = stream.readUInt16()
		self.bgmNightID = stream.readUInt16()
		self.encDataID = stream.readUInt16()
		self.eventDataID = stream.readUInt16()
		self.placeNameID = stream.readUInt16() & 0xFF
		self.textBoxType = self.placeNameID & 0x00FF
		self.weatherID = stream.readUInt8()
		self.cameraID = stream.readUInt8()
		self.mapType = stream.readUInt8()
		byte = stream.readUInt8()
		self.battleBGType = byte & 0b11110000
		self.bicycleFlag = byte & 0b00001000
		self.dashFlag = byte & 0b00000100
		self.escapeFlag = byte & 0b00000010
		self.flyFlag = byte & 0b00000001

class RotomMapChunk:
	def __init__(self,  data):
		#In DPPT all maps are fixed 32x32
		#TODO: properly set up map matrix stuff
		mapData = bStream.bStream(data=data)
		
		permissionsSize = mapData.readUInt32()
		objectSize = mapData.readUInt32()
		modelSize = mapData.readUInt32()
		bdhcSize = mapData.readUInt32()
		
		self.id = id
		self.objectCount = int(objectSize / 0x30)
		
		self.MovementPermissions = [(mapData.readUInt8(), mapData.readUInt8()) for x in range(0, 32*32)]
		self.MapObjects = [RotomMapObject(mapData) for x in range(0, int(objectSize / 0x30))]
		
		#TODO: load embedded nsbmd and the proper textures for that map
		mapData.seek(permissionsSize + objectSize + 0x10)

		self.modelData = mapData.read(modelSize)
		self.MapModel = PalkiaPy.loadNSBMD(data=self.modelData)

		mapData.seek(modelSize + permissionsSize + objectSize + 0x10)
		self.bdhcData = mapData.read(bdhcSize)

	def setMapTextureSet(self, textureset):
		if(self.MapModel != None):
			if(textureset not in mapTextures):
				mapTextures[textureset] = PalkiaPy.loadNSBTX(data=bytes(mapTexNarc.files[textureset]))
			self.MapModel.attachNSBTX(mapTextures[textureset])

	def getTilePermissions(self, x, y):
		return self.MovementPermissions[(y*32)+x]

	def setTilePermissions(self, x, y, permissions):
		self.MovementPermissions[(y*32)+x] = permissions

	def setObjectPosition(self, index, pos):
		self.MapObjects[index].x = pos[0]
		self.MapObjects[index].y = pos[1]
		self.MapObjects[index].z = pos[2]

	def draw(self, cx=0, cy=0, ch=0):
		if(self.MapModel != None):
			self.MapModel.render(matrix44.create_from_translation([cx * 512, ch * 8, cy * 512]).ravel().tolist())
		for obj in self.MapObjects:
			if(obj.modelID in loadedModels):
				loadedModels[obj.modelID].render(matrix44.create_from_translation([(cx * 512) + obj.x, obj.y, (cy * 512) + obj.z]).ravel().tolist())

	def saveChunk(self, data):
		mapData = bStream.bStream(data=data)
		mapData.writeUInt32(32*32)
		mapData.writeUInt32(0x30 * len(self.MapObjects))
		mapData.writeUInt32(len(self.modelData))
		mapData.writeUInt32(len(self.bdhcData))
		for x in range(32*32):
			mapData.writeUInt8(self.MovementPermissions[x][0])
			mapData.writeUInt8(self.MovementPermissions[x][1])

		for obj in self.MapObjects:
			obj.write(mapData)

		mapData.fhandle.write(self.modelData)
		mapData.fhandle.write(self.bdhcData)
			
		return bytearray(mapData.fhandle.getbuffer())

class RotomMap: #map matrix
	def __init__(self, data, mapID, headers, fieldData, zoneHeaders=None):
		self.mapHeaders = {}
		self.mapChunks = {}
		stream = bStream.bStream(data=data)
		self.currentPlaceName = ""
		self.width = stream.readUInt8()
		self.height = stream.readUInt8()
		self.hasHeader = stream.readUInt8()
		self.hasHeight = stream.readUInt8()
		self.name = stream.readStr(len=stream.readUInt8())
		print(f"Reading Matrix {self.name}")
		
		self.headers = [[0 for x in range(self.width)] for y in range(self.height)]
		self.altitudes = [[0 for x in range(self.width)] for y in range(self.height)]
		self.chunkIDs = [[0 for x in range(self.width)] for y in range(self.height)]

		if(self.hasHeader == True):
			for y in range(self.height):
				for x in range(self.width):
					self.headers[y][x] = stream.readUInt16()

		if(self.hasHeight == True):
			for y in range(self.height):
				for x in range(self.width):
					self.altitudes[y][x] = stream.readUInt8()

		for y in range(self.height):
			for x in range(self.width):
				self.chunkIDs[y][x] = stream.readUInt16()

				if(self.chunkIDs[y][x] != 0xFFFF):
					if(self.chunkIDs[y][x] not in self.mapChunks and self.hasHeader and headers[self.headers[y][x]].placeNameID == mapID):
						self.mapChunks[self.chunkIDs[y][x]] = RotomMapChunk(fieldData.files[self.chunkIDs[y][x]])
						if(self.hasHeader and self.headers[y][x] != 0xFFFF):
							self.mapChunks[self.chunkIDs[y][x]].setMapTextureSet(headers[self.headers[y][x]].areData.mapTileset)
							self.mapHeaders[self.headers[y][x]] = headers[self.headers[y][x]]
						else:
							self.mapChunks[self.chunkIDs[y][x]].setMapTextureSet(headers[mapID].areData.mapTileset)
							self.mapHeaders[self.headers[y][x]] = headers[mapID]
					elif(self.chunkIDs[y][x] not in self.mapChunks and not self.hasHeader and zoneHeaders):
						self.mapChunks[self.chunkIDs[y][x]] = RotomMapChunk(fieldData.files[self.chunkIDs[y][x]])
						self.mapChunks[self.chunkIDs[y][x]].setMapTextureSet(zoneHeaders[-1].areData.mapTileset)
						self.mapHeaders[self.headers[y][x]] = zoneHeaders[-1]						

	def draw(self, location):
		for y in range(self.height):
			for x in range(self.width):
				if(self.chunkIDs[y][x] != 0xFFFF and self.chunkIDs[y][x] in self.mapChunks):
					self.mapChunks[self.chunkIDs[y][x]].draw(x, y, self.altitudes[y][x])