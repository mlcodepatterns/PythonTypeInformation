[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5919637.svg)](https://doi.org/10.5281/zenodo.5919637)
# PythonTypeInformation
The folder TYPE_REPO contains type information of commits of 1000 Python-ML projects. 

## Folder structure
TYPE_REPO is the root folder. The next two child folders are the GitHub user name and the project name. For example, in the following example, the user name is scikit-learn, and the project name is scikit-learn. Inside the project name folder, you can find type information of each commit, named with commit hex postfixed by N or O. The folders end with "N" contain the type information after the change, and the folder ends with O contain the type information before the change.


<img src="https://github.com/mlcodepatterns/PythonTypeInformation/blob/master/folder_structure.png" width="430" height="150" />


## Infer type information of new projects
You can use the python script [script_pytype_type_infer.py](https://github.com/mlcodepatterns/PythonTypeInformation/blob/master/script_pytype_type_infer.py) to infer type information of other projects. 


The steps outlined below leads you through inferring type information of projects.
 
* You may make a new folder to hold all of the data as well as a virtual Python environment.
* `cd` to the new folder
* execute `python3.7 -m venv ./VENV` to create new virtual environment 
* execute `source VENV/bin/activate` to activate the virtual environment 
* execute `pip install -r requirements.txt`. [requirements.txt](https://github.com/mlcodepatterns/PythonTypeInformation/blob/master/requirements.txt) is available in the root folder of this repository
* execute `mkdir TYPE_REPO Pytypestorage GitHub`
* execute `python3 script_pytype_type_infer.py ./Pytypestorage/ ./GitHub/ ./TYPE_REPO/ author/project_name https://github.com/author/project_name.git`
  * > The script script_pytype_type_infer.py can be found [here](https://github.com/mlcodepatterns/PythonTypeInformation/blob/master/script_pytype_type_infer.py) ). There are five parameters to the script: 1) a directory for pytype's intermediate processing files, 2) a directory to store the GitRepos, 3) a directory to store type information, 4) GitHub full name of the project e.g., author/project_name, and 5) GitHub clone url e.g., https://github.com/author/project_name.git. 
  * > author/project_name is the GitHub full name of the project. e.g., maldil/MLEditsTest
  * > The new type information will be generated in the TYPE_REPO folder. To infer the results with new type information, update the folder??TYPE_REPO of the tools [Py-RefactoringMiner](https://github.com/maldil/RefactoringMiner) and [R-CPATMiner](https://github.com/maldil/R-CPATMiner).
