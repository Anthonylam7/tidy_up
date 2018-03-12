import os
def generate_files(path, baseName, numFiles=1, extension="txt"):
    """
    creates numFiles number of files at a specified path
    :param path: path to directory, if directory is not there create it
    :param baseName: filename string
    :param numFiles: int number of files
    :return: None
    """
    if not isinstance(numFiles, (int)):
        raise ValueError("numFiles should be an integer!")
    if not isinstance(baseName, (str)):
        raise ValueError("baseName should be a string!")
    cwd = os.getcwd()
    if not os.path.exists(path):
        os.mkdir(os.path.join(cwd, path))
    # Path exists but does not lead to a directory
    if not os.path.isdir(path):
        raise ValueError("path should be a valid path to a directory!")
    #create empty files
    for num in range(numFiles):
        filePath = os.path.join(cwd, path, "{}{}.{}".format(baseName, num, extension))
        open(filePath, "w").close()


