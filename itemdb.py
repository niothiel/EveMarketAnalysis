class ItemDb:
	def __init__(self):
		self.typeid_to_name = {}
		self.name_to_typeid = {}

		with open('data/typeid.txt', 'r') as f:
			for line in f:
				splitString = line.split('\t')
				typeId = int(splitString[0].strip())
				name = splitString[1].strip()
				self.typeid_to_name[typeId] = name
				self.name_to_typeid[name] = typeId

	def get_name(self, typeid):
		if typeid not in self.typeid_to_name.keys():
			return None

		return self.typeid_to_name[typeid]

	def get_typeid(self, name):
		if name not in self.name_to_typeid.keys():
			return None

		return self.name_to_typeid[name]

	def get_typeids(self):
		return self.typeid_to_name.keys()