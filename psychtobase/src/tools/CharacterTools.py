import json
import os
import logging
import copy
from psychtobase.src import window, Constants
from psychtobase.src import files

class CharacterObject:
	def __init__(self, path: str, resultPath) -> None:
		self.charName:str = os.path.basename(path)
		self.resultPath = resultPath
		self.pathName:str = path
		self.psychChar = {}
		self.character:dict = Constants.CHARACTER.copy()
		self.characterName:str = None

		self.loadCharacter()

	def loadCharacter(self):
		self.psychChar = json.loads(open(self.pathName, 'r').read())
		self.characterJson = files.removeTrail(self.charName)

	def convert(self):
		char = self.psychChar

		logging.info(f'Converting character {self.charName}')

		englishCharacterName = ' '.join([string.capitalize() for string in self.characterJson.split('-')])
		self.character['name'] = englishCharacterName
		self.character['assetPath'] = char['image']
		self.character['singTime'] = char['sing_duration']
		self.character['scale'] = char['scale']
		self.character['isPixel'] = char['scale'] >= 6
		self.character['healthIcon']['id'] = char['healthicon']
		self.character['healthIcon']['isPixel'] = char['scale'] >= 6
		self.character['flipX'] = char.get('flip_x', False)

		animTemplate = copy.deepcopy(Constants.ANIMATION)

		#left are base game values, right are psych engine values
		animTemplate['name'] = char['anim']
		animTemplate['prefix'] = char['name']
		animTemplate['offsets'] =char['offsets']

		logging.info(f'''Converting some character animations:
		${char['animation']}
		${char['offsets']}
		${char['offsets']}''')
		#note to remove this later

		self.character['animations'].append(animTemplate)

		logging.info(f'Character {englishCharacterName} successfully converted')

	def save(self):
		savePath = os.path.join(self.resultPath, self.characterJson)

		logging.info(f'Character {self.characterName} saved to {savePath}.json')

		with open(f'{savePath}.json', 'w') as f:
			json.dump(self.character, f, indent=4)