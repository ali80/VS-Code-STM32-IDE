# Readme (details)
This file answers some of the frequently asked questions and explains inner working and details of specific 'update*.py' scripts. Also, see README.md in this folder.

## FAQ:
* **What files can I modify?**  
  Basically, user should modify only 'c_cpp_properties.json' file, specifically 'user_*' fields. Other paths should be updated either with CubeMX or 'updatePaths.py' script.  

* **Can workspace files/folders paths contain spaces?**  
  No. This is a common issue and must be avoided - all user defined source folders and files must be without spaces, since GNU Make does not handle any paths with spaces. Anyway, paths to GCC/GNU/OPENOCD executables CAN include spaces because they are not used in the same manner as workspace sources.  

* **Can I add my custom tasks and launch configurations?**  
  Yes. See **updateTasks.py** description. Also, see *#TODO USER* markings in 'update*.py' code for specific how-to's.

* **Will user fields be overwritten when any of 'update\*.py' script is called?**  
  No. If '.json' files are a valid files, data is merged eg.: tasks are added to existing ones (only the same labeled tasks are overwritten). If '.json' files are not valid, '.backup' file is created and new valid file is created from template. User fields in 'c_cpp_properties.json' must be properly added, see example.

* **What is .SVD file needed for?**  
  SVD file is a CPU-specific register description file. It is needed for Cortex-Debug plugin to correctly display core/system registers and for OpenOCD to properly interface with chosen CPU. This files can be found from [Keil MDK Software Pack](https://www.keil.com/dd2/pack/).

* **Where do compiler flags in 'buildData.json' come from?**  
  This flags are fetched from current 'Makefile' with 'print-VARIABLE' function, which is added specifically for this purpose. Once project is updated with 'update.py' script, 'buildData.json' shows merged user and CubeMX compiler settings, while new 'Makefile' has added user settings to original 'Makefile'.

* **How do I compile specific file?**  
  Run 'Compile' task. Currently only C source files are supported by this task (assembler flags are not added to compile command).

* **Can I add custom compiler flags/switches?**  
  Yes. 'user_cFlags' and 'user_asmFlags' fields in 'c_cpp_properties.json' fields are meant for this purpose and are added to new 'Makefile' once *Update workspace* task is executed.

* **Where can I see when the workspace files were updated the last time?**  
  *Version* and *last run timestamp* are updated on every run of 'update.py' script and can be seen in 'Makefile' and 'buildData.json'.
  

# update.py
This is a parent script of all 'update*.py' scripts. It is the only file that needs to be called if 'Makefile' was modified with STM32CubeMX tool or if user modified 'c_cpp_properties.json'.  
Script calls other 'update*.py' scripts and generate all the necessary files for VS Code. See other scripts descirptions below for details.

## updatePaths.py
This script checks and update paths to all neccessary files/folders: GCC compiler, Make tool, OpenOCD, target configuration file, SVD description file. Script automatically fills data in 'buildData.json' which is later needed for other scripts.

## updateWorkspaceSources.py
This script (re)generate 'c_cpp_properties.json' file from existing 'Makefile' and 'c_cpp_properties.json' file. User can modify (add paths to sources/folders and defines) only fields marked with "user_*", otherwise fields will be overwritten with next update procedure.
Data fetched from 'Makefile' and user fields are storred in 'buildData.json' at the end.  
  
If any of files/paths are missing or invalid, new ones are created (and backup file is generated if available), and data is restored to default (see 'templateStrings.py' and 'updateWorkspaceSources.py' file).  

File adds 'print-variable' function to 'Makefile', while creating a backup 'Makefile'. Function is needed for fetching data from 'Makefile' with (example) 'make print-CFLAGS' call.

## updateWorkspaceFile.py
This file adds "cortex-debug" keys to '*.code-workspace' file. It is needed for Cortex-Debug extension and should not be modified by user. Instead, this fields are fetched from 'buildData.json' file.

## updateMakefile.py
This script generate new 'Makefile' from old 'Makefile' and user data. User data specified in 'c_cpp_properties.json' is merged with existing data from 'Makefile' and stored into 'buildData.json'. New 'Makefile' is created by making a copy and appending specific strings (c/asm sources, includes and defines) with proper multi-line escaping ( '\\' ).

## updateTasks.py
This script (re)generate 'tasks.json' file in '.vscode' workspace subfolder. Tasks could be separated to:  

**Building/compiling tasks:**
* Build (execute 'make' command - compile all source files and generate output binaries)
* Compile (compile currently opened source file with the same compiler flags as specified in 'Makefile')
* Clean build folder (delete)
  
**Target control tasks:**
* Download code and run CPU (program .elf output file and run CPU without attaching debugger)
* Reset and run CPU (do not download code, execute reset and run CPU without attaching debugger)
* Stop CPU
* Run CPU
  
**Python/IDE tasks:**
* Update (calls 'update.py' script and update all workspace sources)
  
User can add custom tasks in two ways: add task to 'updateTasks.py' file (added always even if 'tasks.json' previously does not exist) or add task directly to 'tasks.json' file.  
If 'tasks.json' file already exists when 'updateTasks.py' script is called, data is merged and task will not be overwritten. But, if existing 'tasks.json' file is not valid (faulty json format), backup is created and new clean 'tasks.json' file is generated, overwitting user added task (could be found in .backup file).  
See *#TODO USER* markings inside file for how to add custom tasks.

## updateLaunchConfig.py
This script (re)generate 'launch.json' file inside '.vscode' workspace subfolder. Two tasks are currently implemented:
* Debug (download code to the target, attach debugger and stop asap)
* Run current python file (run currently opened .py file)
  
Data for Debug Launch configuration is fetched from 'buildData.json' and should not be modified by user. Insteadm user shoud correctly specify target .cfg and .svd file with 'updatePaths.py'.  
Other launch configurations can be added in the simmilar way as tasks, see *updateTasks.py* description.

## updateBuildData.py
This file (re)generate 'buildData.json' file inside '.vscode' workspace subfolder. This file contains all workspace paths, sorces, defines and compiler settings combined from 'Makefile', 'c_cpp_properties.json' file and user defined tools paths. File is used by 'update*.py' scripts and can be used for user to inspect what settings are used/generated by CubeMX.  
User should not modify this file, since it will be overwritten or tasks/launch confgurations will be invalid. Instead, user should set CubeMX options, update paths with 'updatePaths.py' and correctly set data in 'c_cpp_properties.json' file.

## templateStrings.py
This file content is used from other 'update*.py' scripts as a template to generate other '*.json' fields. User can modify default strings as long as it sticks to a valid .json format.  

--------
## How it actually works?
First, all scripts check if file/folder structure is as expected ('\*.ioc' file in the same folder as '\*.code-workspace' file). Existing tools paths are checked and updated, and 'buildData.json' is created with this data.  
'Makefile' is checked to see if it was already altered with previous 'update' actions. If this is not the original 'Makefile', original is restored from 'Makefile.backup' file. 'print-variable' function is added to enable fetching internal 'Makefile' variables (sources and compiler flags) and 'c_cpp_properties.json' file is created/merged with existing one. Data in 'c_cpp_properties.json' from 'Makefile' is stored in 'cubemx_*' fields and is needed for *compile* task later on.  
On update, new 'Makefile' is generated with merged data from old 'Makefile' and *user_* fields from 'c_cpp_properties.json'. 'buildData.json' is updated with new 'Makefile' variables.  
Tasks and Launch configurations are generated with paths and data from existing 'buildData.json'. Syntax is VS Code predefined and is hard-coded into '.py' files, but can be changed.  
At the end, 'cortex-debug' settings are applied to '\*.code-workspace' file.
