from base64 import b64decode
import json
import logging
import os
import shutil
import time
from psychtobase.src import Constants
from psychtobase.src.tools import ModConvertTools as ModTools
import threading

from psychtobase.src import files
from psychtobase.src.tools.CharacterTools import CharacterObject
from psychtobase.src.tools.ChartTools import ChartObject
from psychtobase.src.tools import VocalSplit, WeekTools, StageTool, StageLuaParse
from psychtobase.src import Utils

# Main

charts = []
vocalSplitEnabled = True

def folderMake(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
                                                    #i hate escape charcaters
        logging.warn(f'Folder ${folder_path} already exists! Didn\'t make the folder.')

def fileCopy(source, destination):
    if os.path.exists(source):
        shutil.copyfile(source, destination)
    else:
        logging.debug(f'File ${source} doesn\'t exist (not a problem)')
        logging.info(f'Ported ${source} to ${destination}')

def convert(psych_mod_folder, result_folder, options):
    runtime = time.time()

    logging.info('Converting started...')

    modName = psych_mod_folder # MOD FOLDER PSYCH ENGINE
    modFoldername = os.path.basename(psych_mod_folder)

    print(psych_mod_folder, result_folder)

    logging.info('Converting pack.json')

    dir = Constants.FILE_LOCS.get('PACKJSON')
    psychPackJson = dir[0]
    polymodMetaDir = dir[1]
    
    if os.path.exists(f'{modName}{psychPackJson}'):
        polymod_meta = ModTools.convertPack(json.loads(open(f'{modName}{psychPackJson}', 'r').read()))
        folderMake(f'{result_folder}/{modFoldername}/')
        open(f'{result_folder}/{modFoldername}/{polymodMetaDir}', 'w').write(json.dumps(polymod_meta, indent=4))

        logging.info('pack.json converted and saved')
    else:
        folderMake(f'{result_folder}/{modFoldername}/')
        open(f'{result_folder}/{modFoldername}/{polymodMetaDir}', 'w').write(json.dumps(ModTools.defaultPolymodMeta(), indent=4))
        logging.warn('pack.json not found. Replaced it with default')

    logging.info('Copying pack.png')
    dir = Constants.FILE_LOCS.get('PACKPNG')
    psychPackPng = dir[0]
    polymodIcon = dir[1]
    
    if os.path.exists(f'{modName}{psychPackPng}'):
        folderMake(f'{result_folder}/{modFoldername}/')
        try:
            fileCopy(f'{modName}{psychPackPng}', f'{result_folder}/{modFoldername}/{polymodIcon}')
        except Exception as e:
            logging.error(f'Could not copy pack.png file: {e}')

    logging.info('Converting data/credits.txt')
    dir = Constants.FILE_LOCS.get('CREDITSTXT')

    psychCredits = dir[0]
    modCredits = dir[1]

    if os.path.exists(f'{modName}{psychCredits}'):
        folderMake(f'{result_folder}/{modFoldername}/')
        resultCredits = ModTools.convertCredits(open(f'{modName}{psychCredits}', 'r').read())
        open(f'{result_folder}/{modFoldername}/{modCredits}', 'w').write(resultCredits)
    else:
        logging.warn('Could not find data/credits.txt')


    
        chartFolder = Constants.FILE_LOCS.get('CHARTFOLDER')
        psychChartFolder = modName + chartFolder[0]

        folderMake(f'{result_folder}/{modFoldername}{chartFolder[1]}')

        songs = files.findAll(f'{psychChartFolder}*')

        for song in songs:
            logging.info(f'Checking if {song} is a valid chart directory...')
            if os.path.isdir(song):
                logging.info(f'Loading charts in {song}')

                outputpath = f'{result_folder}/{modFoldername}'
                songChart = ChartObject(song, outputpath)
                
                logging.info(f'Converting charts of {song}...')
                try:
                    songChart.convert()

                    songName = songChart.songName
                    charts.append({
                        'songKey': songName,
                        'sections': songChart.sections,
                        'bpm': songChart.startingBpm,
                        'player': songChart.metadata['playData']['characters']['player'],
                        'opponent': songChart.metadata['playData']['characters']['opponent']
                    })

                    logging.info(f'{song} charts converted, saving')
                    songChart.save()
                except Exception as e:
                    logging.error(f'[{song}] Unable to convert charts: {e}')

    logging.info('Copying character assets...')

    dir = Constants.FILE_LOCS.get('CHARACTERASSETS')
    psychCharacterAssets = modName + dir[0]
    bgCharacterAssets = dir[1]

    folderMake(f'{result_folder}/{modFoldername}{bgCharacterAssets}')

    for character in files.findAll(f'{psychCharacterAssets}*'):
        if not os.path.isdir(character):
            logging.info(f'Copying asset {character}')
            try:
                fileCopy(character, result_folder + f'/{modFoldername}' + bgCharacterAssets + os.path.basename(character))
            except Exception as e:
                logging.error(f'Could not copy asset {character}: {e}')
        else:
            logging.warn(f'{character} is a directory, not a file! Skipped')

    logging.info('Converting character jsons...')

    dir = Constants.FILE_LOCS.get('CHARACTERJSONS')

    psychCharacters = modName + dir[0]
    bgCharacters = dir[1]

    folderMake(f'{result_folder}/{modFoldername}{bgCharacters}')

    for character in files.findAll(f'{psychCharacters}*'):
        logging.info(f'Checking if {character} is a file...')
        if not os.path.isdir(character) and character.endswith('.json'):
            converted_char = CharacterObject(character, result_folder + f'/{modFoldername}' + bgCharacters)

            converted_char.convert()
            converted_char.save()
        else:
            logging.warn(f'{character} is a directory, or not a json! Skipped')

    logging.info('Copying character icons...')

    dir = Constants.FILE_LOCS.get('CHARACTERICON')
    psychCharacterAssets = modName + dir[0]
    bgCharacterAssets = dir[1]

    folderMake(f'{result_folder}/{modFoldername}{bgCharacterAssets}')

    for character in files.findAll(f'{psychCharacterAssets}*'):
        if not os.path.isdir(character):
            logging.info(f'Copying asset {character}')
            try:
                fileCopy(character, result_folder + f'/{modFoldername}' + bgCharacterAssets + os.path.basename(character))
            except Exception as e:
                logging.error(f'Could not copy asset {character}: {e}')
        else:
            logging.warn(f'{character} is a directory, not a file! Skipped')

    dir = Constants.FILE_LOCS.get('SONGS')
    psychSongs = modName + dir[0]
    bgSongs = dir[1]

    folderMake(f'{result_folder}/{modFoldername}{bgSongs}')

    for song in files.findAll(f'{psychSongs}*'):
        logging.info(f'Checking if {song} is a valid song directory...')
        if os.path.isdir(song):
            logging.info(f'Copying files in {song}')
            for songFile in files.findAll(f'{song}/*'):
                if os.path.basename(songFile) == 'Inst.ogg':
                    logging.info(f'Copying asset {songFile}')
                    try:
                        folderMake(f'{result_folder}/{modFoldername}{bgSongs}{os.path.basename(song)}')
                        fileCopy(songFile,
                          f'{result_folder}/{modFoldername}{bgSongs}{os.path.basename(song)}/{os.path.basename(songFile)}')
                    except Exception as e:
                        logging.error(f'Could not copy asset {songFile}: {e}')
                elif os.path.basename(songFile) == 'Voices.ogg' and vocalSplitEnabled:
                    # Vocal Split
                    songKey = os.path.basename(song)

                    chart = None
                    for _chart in charts:
                        if _chart['songKey'] == songKey:
                            chart = charts[charts.index(_chart)]

                    if chart != None:
                        sections = chart['sections']
                        bpm = chart['bpm']
                        logging.info(f'Vocal Split ({songKey}) BPM is {bpm}')
                        path = song + '/'
                        resultPath = result_folder + f'/{modFoldername}{bgSongs}{songKey}/'
                        songChars = [chart['player'],
                                      chart['opponent']]
                        
                        #print(songChars)

                        logging.info(f'Vocal Split currently running for: {songKey}')
                        logging.info(f'Passed the following paths: {path} || {resultPath}')
                        logging.info(f'Passed characters: {songChars}')

                        vocal_split_thread = threading.Thread(target=VocalSplit.vocalsplit, args=(sections, bpm, path, resultPath, songKey, songChars))
                        vocal_split_thread.start()
                        vocal_split_thread.join()
                    else:
                        logging.warn(f'No chart was found for {songKey} so the vocal file will be copied instead.')
                        try:
                            folderMake(f'{result_folder}/{modFoldername}{bgSongs}{os.path.basename(song)}')
                            fileCopy(songFile,
                            f'{result_folder}/{modFoldername}{bgSongs}{os.path.basename(song)}/{os.path.basename(songFile)}')
                        except Exception as e:
                            logging.error(f'Could not copy asset {songFile}: {e}')
                else:
                    logging.info(f'Copying asset {songFile}')
                    try:
                        folderMake(f'{result_folder}/{modFoldername}{bgSongs}{os.path.basename(song)}')
                        fileCopy(songFile,
                          f'{result_folder}/{modFoldername}{bgSongs}{os.path.basename(song)}/{os.path.basename(songFile)}')
                    except Exception as e:
                        logging.error(f'Could not copy asset {songFile}: {e}')

    logging.info('Converting weeks (levels)...')

    dir = Constants.FILE_LOCS.get('WEEKS')
    psychWeeks = modName + dir[0]
    baseLevels = dir[1]

    folderMake(f'{result_folder}/{modFoldername}{baseLevels}')

    for week in files.findAll(f'{psychWeeks}*.json'):
        logging.info(f'Loading {week} into the converter...')

        weekJSON = json.loads(open(week, 'r').read())
        open(f'{result_folder}/{modFoldername}{baseLevels}{os.path.basename(week)}', 'w').write(json.dumps(WeekTools.convert(weekJSON, modName), indent=4))

    logging.info('Copying prop assets...')

    dir = Constants.FILE_LOCS.get('WEEKCHARACTERASSET')
    psychWeeks = modName + dir[0]
    baseLevels = dir[1]

    allXml = files.findAll(f'{psychWeeks}*.xml')
    allPng = files.findAll(f'{psychWeeks}*.png')
    for asset in allXml + allPng:
        logging.info(f'Copying {asset}')
        try:
            folderMake(f'{result_folder}/{modFoldername}{baseLevels}')
            fileCopy(asset,
                f'{result_folder}/{modFoldername}{baseLevels}{os.path.basename(asset)}')
        except Exception as e:
            logging.error(f'Could not copy asset {asset}: {e}')

    logging.info('Copying level titles...')

    dir = Constants.FILE_LOCS.get('WEEKIMAGE')
    psychWeeks = modName + dir[0]
    baseLevels = dir[1]

    allPng = files.findAll(f'{psychWeeks}*.png')
    for asset in allPng:
        logging.info(f'Copying {asset}')
        try:
            folderMake(f'{result_folder}/{modFoldername}{baseLevels}')
            fileCopy(asset,
                f'{result_folder}/{modFoldername}{baseLevels}{os.path.basename(asset)}')
        except Exception as e:
            logging.error(f'Could not copy asset {asset}: {e}')

    logging.info('Converting stages...')

    dir = Constants.FILE_LOCS.get('STAGE')
    psychStages = modName + dir[0]
    baseStages = dir[1]

    allStageJSON = files.findAll(f'{psychStages}*.json')
    for asset in allStageJSON:
        logging.info(f'Converting {asset}')
        folderMake(f'{result_folder}/{modFoldername}{baseStages}')
        stageJSON = json.loads(open(asset, 'r').read())
        assetPath = f'{result_folder}/{modFoldername}{baseStages}{os.path.basename(asset)}'
    
        stageLua = asset.replace('.json', '.lua')
        logging.info(f'Parsing .lua with matching .json name: {stageLua}')

        luaProps = []
        if os.path.exists(stageLua):
            logging.info(f'Parsing {stageLua} and attempting to extract methods and calls')
            try:
                luaProps = StageLuaParse.parseStage(stageLua)
            except Exception as e:
                logging.error(f'Could not complete parsing of {stageLua}: {e}')

        logging.info(f'Converting Stage JSON')
        stageJSONConverted = json.dumps(StageTool.convert(stageJSON, os.path.basename(asset), luaProps), indent=4)
        open(assetPath, 'w').write(stageJSONConverted)

    logging.info('Copying .png and .xml files...')

    dir = Constants.FILE_LOCS.get('IMAGES')
    psychImages = modName + dir[0]
    baseImages = dir[1]

    allimages = files.findAll(f'{psychImages}*.png') + files.findAll(f'{psychImages}*.xml')
    for asset in allimages:
        logging.info(f'Copying {asset}')

        try:
            folderMake(f'{result_folder}/{modFoldername}{baseImages}')
            fileCopy(asset, f'{result_folder}/{modFoldername}{baseImages}{os.path.basename(asset)}')
        except Exception as e:
            logging.error(f'Failed to copy {asset}: {e}')
    
    dir = Constants.FILE_LOCS.get('FREEPLAYICON')
    psychFreeplayIcon = modName + dir[0]
    baseFreeplayIcon = dir[1]

    logging.info(f'Conversion done! Thank\'s for using FNF Porter')
