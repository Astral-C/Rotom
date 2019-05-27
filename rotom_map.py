import bStream

class RotomMapObject:
	def __init__(self, strm):
		self.modelID = strm.readUInt32()
		
		self.x = (float(strm.readInt32() / (1 << 16)))
		self.y = (float(strm.readInt32() / (1 << 16)))
		self.z = (float(strm.readInt32() / (1 << 16)))

		#these most definatley have meaning, don't know what yet.
		self.misc = strm.fhandle.read(32)
	
	def __str__(self):
		return "Model ID: {0}".format(self.modelID)

	def write(self, strm):
		strm.writeUInt32(self.modelID)
		strm.writeInt32((int(self.x * (1 << 16))))
		strm.writeInt32((int(self.y * (1 << 16))))
		strm.writeInt32((int(self.z * (1 << 16))))

		strm.fhandle.write(self.misc)

class RotomMap:
	def __init__(self, raw, id):
		#In DPPT all maps are fixed 32x32
		#TODO: properly set up map matrix stuff
		mapData = bStream.bStream(data=raw)
		permissionsSize = mapData.readUInt32()
		objectSize = mapData.readInt32()
		
		mapData.fhandle.seek(0x10)
		
		self.id = id
		self.objectCount = int(objectSize / 0x30)
		
		self.MovementPermissions = [(mapData.readUInt8(), mapData.readUInt8()) for x in range(0, 32*32)]
		self.MapObjects = [RotomMapObject(mapData) for x in range(0, int(objectSize / 0x30))]
		
		#TODO: load embedded nsbmd and the proper textures for that map
		
		self.MapModel = None

	def getTilePermissions(self, x, y):
		return self.MovementPermissions[(y*32)+x]

	def setTilePermissions(self, x, y, permissions):
		self.MovementPermissions[(y*32)+x] = permissions

	def setObjectPosition(self, index, pos):
		self.MapObjects[index].x = pos[0]
		self.MapObjects[index].y = pos[1]
		self.MapObjects[index].z = pos[2]

	def saveMap(self, raw):
		mapData = bStream.bStream(data=raw)
		mapData.fhandle.seek(0x10)
		for x in range(32*32):
			mapData.writeUInt8(self.MovementPermissions[x][0])
			mapData.writeUInt8(self.MovementPermissions[x][1])

		for obj in self.MapObjects:
			obj.write(mapData)
			
		return bytearray(mapData.fhandle.getbuffer())
			
