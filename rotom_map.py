import bStream
import PalkiaPy
import ndspy.rom
import ndspy.narc

from pyrr import matrix44, Matrix44, Vector4, Vector3, Quaternion

loadedModels = {}
uildModelNarc = None
mapTexNarc = None
defaultMapTex = None

def SetBuildModelNarc(modelArc):
	buildModelNarc = modelArc

def SetMapTextureNarc(mapTextures):
	mapTexNarc = mapTextures
	#defaultMapTex = PalkiaPy.loadNSBTX(data=bytes(mapTextures.files[6]))

class RotomMapObject:
	def __init__(self, strm):
		self.modelID = strm.readUInt32()
		
		if(buildModelNarc != None and self.modelID not in loadedModels):
			loadedModels[self.modelID] = PalkiaPy.loadNSBMD(data=bytes(buildModelNarc.files[self.modelID]))

		self.x = (float(strm.readInt32() / (1 << 12)))
		self.y = (float(strm.readInt32() / (1 << 12)))
		self.z = (float(strm.readInt32() / (1 << 12)))

		#these most definatley have meaning, don't know what yet.
		self.misc = strm.fhandle.read(32)
	
	def __str__(self):
		return "Model ID: {0}".format(self.modelID)

	def write(self, strm):
		strm.writeUInt32(self.modelID)
		strm.writeInt32((int(self.x * (1 << 12))))
		strm.writeInt32((int(self.y * (1 << 12))))
		strm.writeInt32((int(self.z * (1 << 12))))

		strm.fhandle.write(self.misc)

class RotomMap:
	def __init__(self, raw, id):
		#In DPPT all maps are fixed 32x32
		#TODO: properly set up map matrix stuff
		mapData = bStream.bStream(data=raw)
		permissionsSize = mapData.readUInt32()
		objectSize = mapData.readUInt32()
		modelSize = mapData.readUInt32()

		mapData.fhandle.seek(0x10)
		
		self.id = id
		self.objectCount = int(objectSize / 0x30)
		
		self.MovementPermissions = [(mapData.readUInt8(), mapData.readUInt8()) for x in range(0, 32*32)]
		self.MapObjects = [RotomMapObject(mapData) for x in range(0, int(objectSize / 0x30))]
		
		#TODO: load embedded nsbmd and the proper textures for that map
		mapData.seek(permissionsSize + objectSize + 0x10)
		modelData = mapData.read(modelSize)
		self.MapModel = PalkiaPy.loadNSBMD(data=modelData)
		if(self.MapModel != None):
			self.MapModel.attachNSBTX(defaultMapTex)

	def getTilePermissions(self, x, y):
		return self.MovementPermissions[(y*32)+x]

	def setTilePermissions(self, x, y, permissions):
		self.MovementPermissions[(y*32)+x] = permissions

	def setObjectPosition(self, index, pos):
		self.MapObjects[index].x = pos[0]
		self.MapObjects[index].y = pos[1]
		self.MapObjects[index].z = pos[2]

	def draw(self, cx=0, cy=0, ch=0):
		self.MapModel.render(matrix44.create_from_translation([cx * 512, cy * 512, ch]).ravel().tolist())
		for obj in self.MapObjects:
			if(obj.modelID in loadedModels):
				loadedModels[obj.modelID].render(matrix44.create_from_translation([(cx * 512) + obj.x, (cy * 512) + obj.y, obj.z]).ravel().tolist())

	def saveMap(self, raw):
		mapData = bStream.bStream(data=raw)
		mapData.fhandle.seek(0x10)
		for x in range(32*32):
			mapData.writeUInt8(self.MovementPermissions[x][0])
			mapData.writeUInt8(self.MovementPermissions[x][1])

		for obj in self.MapObjects:
			obj.write(mapData)
			
		return bytearray(mapData.fhandle.getbuffer())
			
