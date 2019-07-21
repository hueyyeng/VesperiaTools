# VesperiaTools
Collection of scripts and tools to extract data from Tales of Vesperia Definitive Edition.

## Features
1. Extract meshes (with some issues).
2. Extract textures.*
3. Unpack DAT packages.*
4. Export meshes as Wavefront OBJ.**

_*Requires HyoutaTools._
_**Refer to Known Issues_

## Requirements
- Python 3.6+
- Windows 7 SP1 or newer (for HyoutaTools)

## Dependencies
Uses Admiral Curtiss' [HyoutaTools](https://github.com/AdmiralCurtiss/HyoutaTools) to perform certain data extraction. Knowledge of compiling Visual Studio project are required to compile HyoutaTools.

Place the compiled executables and DLLs into `hyoutatools` directory at root level.

## Known Issues
1. The exported Wavefront OBJ works in 3ds Max 2015 and Houdini 16.5. Maya 2014 can't import the exported Wavefront OBJ due to overlapping face indices value (it is a known quirk for Maya OBJ plugin)
2. The UVs for non-character meshes are wonky (read: unusable).
3. There is no material support yet for this release.

## TODO
- Remove dependencies for HyoutaTools (make this scripts purely dependant on Python's libraries so it can be run on macOS and Linux)
- Text extraction and fix typo issues (e.g. missing whitespace, linebreak, etc)
- Creating a patcher to assists patching of data.

## Credits
- __[Admiral Curtiss](https://github.com/AdmiralCurtiss)__
  - For creating HyoutaTools and figuring out the quirky unpacking method for PC Vesperia Definitive Edition (refer to the issue that I raised on the repo).
  - GitHub repo: [HyoutaTools](https://github.com/AdmiralCurtiss/HyoutaTools)
- __[delguoqing](https://github.com/delguoqing)__
  - For sharing the Python 2 script that he wrote for extracting character meshes and textures for Xbox 360 Vesperia version.
  - GitHub repo: [tov_tools](https://github.com/delguoqing/various/tree/master/tov_tools)
- __Szkaradek123__ from Xentax forum
  - For sharing the Python 2 script for Blender 2.49 for extracting character meshes, skin weights, joints and textures for PC Vesperia Definitive Edition.
