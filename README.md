# VesperiaTools
Collection of scripts and tools to extract data from Tales of Vesperia Definitive Edition.

## Features
1. Extract meshes (with some issues).
2. Extract textures.
3. Parse SVO, DAT and FPS4 packages.
4. Export meshes as Wavefront OBJ.**

Take note that VesperiaTools will dump the parsed files within the same directory as the input file. Make sure to have enough free disk space.

_**Refer to Known Issues_

## Requirements
- Python 3.8+
- Windows 7 SP1 or newer, Linux or macOS

## Running VesperiaTools
![vesperia_tools_screenshot.png](docs/images/vesperia_tools_screenshot.png)

The use of virtual environment are highly recommended in isolating existing Python environment. Please refer to the steps below:
```bash
virtualenv --python python env
source env/Scripts/activate
pip install -r requirements/base.txt
python main.py
```

Refer to [https://realpython.com/python-virtual-environments-a-primer/](https://realpython.com/python-virtual-environments-a-primer/) for more details on setting up a virtual environment.

## Known Issues
1. The exported Wavefront OBJ works in 3ds Max 2015 and Houdini 16.5. Maya 2014 can't import the exported Wavefront OBJ due to overlapping face indices value (it is a known quirk for Maya OBJ plugin)
2. The UVs for non-character meshes are wonky (read: unusable).
3. There is no material support yet for this release.

## TODO
- Text extraction and fix typo issues (e.g. missing whitespace, linebreak, etc)
- Creating a patcher to assists patching of data.

## Credits
- __[Admiral Curtiss](https://github.com/AdmiralCurtiss)__
  - For creating HyoutaTools and figuring out the quirky unpacking method for PC Vesperia Definitive Edition [Link To Raised Issue](https://github.com/AdmiralCurtiss/HyoutaTools/issues/7).
  - GitHub repo: [HyoutaTools](https://github.com/AdmiralCurtiss/HyoutaTools)
- __[delguoqing](https://github.com/delguoqing)__
  - For sharing the Python 2 script that he wrote for extracting character meshes and textures for Xbox 360 Vesperia version.
  - GitHub repo: [tov_tools](https://github.com/delguoqing/various/tree/master/tov_tools)
- __Szkaradek123__ from Xentax forum
  - For sharing the Python 2 script for Blender 2.49 for extracting character meshes, skin weights, joints and textures for PC Vesperia Definitive Edition.
