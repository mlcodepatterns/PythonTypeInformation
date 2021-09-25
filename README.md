# PythonTypeInformation
The folder TYPE_REPO contains type information of commits of 1000 Python-ML projects.

## Folder structure
TYPE_REPO is the root folder. The next two child folders are the GitHub user name and the project name. For example, in the following example, the user name is scikit-learn, and the project name is scikit-learn. Inside the project name folder, you can find type information of each commit named with commit hex postfixed by N or O. The folders end with "N" contain the type information after the change, and the folder ends with O contain the type information after the change.

![](https://github.com/mlcodepatterns/PythonTypeInformation/blob/master/folder_structure.png)

## Infer type information of new projects
You can use the python script [script_pytype_type_infer.py](https://github.com/mlcodepatterns/PythonTypeInformation/blob/master/script_pytype_type_infer.py) to infer type information of other projects. 

