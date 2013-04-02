
class EveApi:

	pass

if __name__ == '__main__':
	api = EveApi('keyId', 'vCode')
	character = api.character('Name' or 'id')
	corporation = api.corporation('Name' or 'id')
