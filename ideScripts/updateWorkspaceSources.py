'''
Update/generate 'c_cpp_properties.json' file in .vscode subfolder.

See details in "README_DETAILS.md'.

'c_cpp_properties.json' fields description:
https://github.com/Microsoft/vscode-cpptools/blob/master/Documentation/LanguageServer/c_cpp_properties.json.md
'''

import json

import utilities as utils
import templateStrings as tmpStr

import updatePaths as pth
import updateMakefile as mkf
import updateBuildData as build

__version__ = utils.__version__


class CPropertiesStrings():
    user_cSources = 'user_cSources'
    user_asmSources = 'user_asmSources'
    user_cIncludes = 'user_cIncludes'
    user_asmIncludes = 'user_asmIncludes'
    user_cDefines = 'user_cDefines'
    user_asmDefines = 'user_asmDefines'
    user_cFlags = 'user_cFlags'
    user_asmFlags = 'user_asmFlags'

    cubemx_sourceFiles = 'cubemx_sourceFiles'
    cubemx_includes = 'cubemx_includes'
    cubemx_defines = 'cubemx_defines'
    gccExePath = 'gccExePath'
    gccIncludePath = 'gccIncludePath'


class CProperties():
    def __init__(self):
        self.cPStr = CPropertiesStrings()
        self.mkfStr = mkf.MakefileStrings()
        self.bStr = build.BuildDataStrings()

    def checkCPropertiesFile(self):
        '''
        Check if 'c_cpp_properties.json' file exists. If it does, check if it is a valid JSON file.
        If it doesn't exist, create new according to template.
        '''
        if utils.fileFolderExists(utils.cPropertiesPath):
            # file exists, check if it loads OK
            try:
                with open(utils.cPropertiesPath, 'r') as cPropertiesFile:
                    json.load(cPropertiesFile)

                print("Existing 'c_cpp_properties.json' file found.")
                return

            except Exception as err:
                errorMsg = "Invalid 'c_cpp_properties.json' file. Creating backup and new one.\n"
                errorMsg += "Possible cause: invalid json format or comments (not supported by this scripts). Error:\n"
                errorMsg += str(err)
                print(errorMsg)

                utils.copyAndRename(utils.cPropertiesPath, utils.cPropertiesBackupPath)

                self.createCPropertiesFile()

        else:  # 'c_cpp_properties.json' file does not exist jet, create it according to template string
            self.createCPropertiesFile()

    def createCPropertiesFile(self):
        '''
        Create fresh 'c_cpp_properties.json' file.
        '''
        try:
            with open(utils.cPropertiesPath, 'w') as cPropertiesFile:
                data = json.loads(tmpStr.c_cpp_template)
                dataToWrite = json.dumps(data, indent=4, sort_keys=False)

                cPropertiesFile.seek(0)
                cPropertiesFile.truncate()
                cPropertiesFile.write(dataToWrite)

                print("New 'c_cpp_properties.json' file created.")

        except Exception as err:
            errorMsg = "Exception error creating new 'c_cpp_properties.json' file:\n"
            errorMsg += str(err)
            utils.printAndQuit(errorMsg)

    def getCPropertiesData(self):
        '''
        Get data from current 'c_cpp_properties.json' file.
        File existance is previoulsy checked in 'checkCPropertiesFile()'.
        '''
        with open(utils.cPropertiesPath, 'r') as cPropertiesFile:
            data = json.load(cPropertiesFile)

        return data

    def addMakefileDataToCPropertiesFile(self, cPropertiesData, makefileData):
        '''
        Add data from Makefile to 'cubemx_...' fields in 'c_cpp_properties.json' file.
        Returns new data to be written to 'c_cpp_properties.json' file.
        '''
        # source files
        sourceFiles = makefileData[self.mkfStr.cSources]
        sourceFiles += makefileData[self.mkfStr.asmSources]
        cPropertiesData["env"][self.cPStr.cubemx_sourceFiles] = sourceFiles

        # includes
        includes = makefileData[self.mkfStr.cIncludes]
        # includes += makefileData[self.mkfStr.asmIncludes]  # TODO Should assembler includes be included here?
        cPropertiesData["env"][self.cPStr.cubemx_includes] = includes

        # defines
        defines = makefileData[self.mkfStr.cDefines]
        # defines += makefileData[self.mkfStr.asmDefines]  # TODO Should assembler defines be included here?
        cPropertiesData["env"][self.cPStr.cubemx_defines] = defines

        return cPropertiesData

    def addBuildDataToCPropertiesFile(self, cPropertiesData, buildData):
        '''
        Add data from buildData to tools fields in 'c_cpp_properties.json' file.
        Returns new data to be written to 'c_cpp_properties.json' file.
        '''
        # gcc
        cPropertiesData["env"][self.cPStr.gccExePath] = buildData[self.bStr.gccExePath]
        cPropertiesData["env"][self.cPStr.gccIncludePath] = buildData[self.bStr.gccInludePath]

        return cPropertiesData

    def overwriteCPropertiesFile(self, data):
        '''
        Overwrite existing 'c_cpp_properties.json' file with new data.
        '''
        try:
            with open(utils.cPropertiesPath, 'r+') as cPropertiesFile:
                cPropertiesFile.seek(0)
                cPropertiesFile.truncate()
                dataToWrite = json.dumps(data, indent=4, sort_keys=False)
                cPropertiesFile.write(dataToWrite)

            print("'c_cpp_properties.json' file updated!")

        except Exception as err:
            errorMsg = "Exception error overwriting 'c_cpp_properties.json' file:\n"
            errorMsg += str(err)
            utils.printAndQuit(errorMsg)

    def addCustomDataToCPropertiesFile(self, cProperties, makefileData, buildData):
        '''
        TODO USER Add custom data to 'c_cpp_properties.json' file.
        '''
        cProperties["configurations"][0]["name"] = utils.getWorkspaceName()

        # TODO USER can add other specific here
        # Note: be careful not to override other parameters that are added from 'Makefile' and 'buildData.json'

        return cProperties


########################################################################################################################
if __name__ == "__main__":
    utils.verifyFolderStructure()

    paths = pth.UpdatePaths()
    cP = CProperties()
    makefile = mkf.Makefile()
    bData = build.BuildData()

    # Makefile must exist
    makefile.checkMakefileFile()  # no point in continuing if Makefile does not exist
    makefile.restoreOriginalMakefile()

    # check if 'buildData.json' exists. Create it or/and get tool paths
    bData.checkBuildDataFile()
    buildData = bData.getBuildData()
    if not paths.verifyExistingPaths(buildData):
        buildData = paths.forceUpdatePaths(buildData)
        bData.overwriteBuildDataFile(buildData)
    makeExePath = buildData[bData.bStr.buildToolsPath]
    gccExePath = buildData[bData.bStr.gccExePath]

    # data from original makefile
    makefileData = makefile.getMakefileData(makeExePath, gccExePath)

    # create 'c_cpp_properties.json' file
    cP.checkCPropertiesFile()
    cPropertiesData = cP.getCPropertiesData()
    cPropertiesData = cP.addBuildDataToCPropertiesFile(cPropertiesData, buildData)
    cPropertiesData = cP.addMakefileDataToCPropertiesFile(cPropertiesData, makefileData)
    cPropertiesData = cP.addCustomDataToCPropertiesFile(cPropertiesData, makefileData, buildData)
    cP.overwriteCPropertiesFile(cPropertiesData)

    # create build folder if it does not exist jet
    buildFolderName = makefileData[mkf.MakefileStrings.buildDir]
    utils.createBuildFolder(buildFolderName)
