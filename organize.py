#! /usr/bin/env python3
"""

    Name:
        organize - regex-based file grouping tools

    Synopsis:
        organize path [options]

    Description:
        "organize" is a program used to organize a directory of files by creating a network of subdirectories
        based on files contained in the root "path" and moving said files into a corresponding subdirectory.
        "organize" uses a pattern to match with filenames to determine which folders to create. By default
        the pattern is as follows:
            "^(.*?)_(_*?)_.*?\\..{3,4}$"
        Each captured group corresponds to a layer of subdirectories created. Not matching files are ignored.
        Sample file format and name:
            COURSE_ASSIGNMENT_NAME.EXTENSION
            ENEE408_Homework1_BOB.pdf

        -p, --pattern
            specify a pattern to match using groups to indicate subdirectories

        -v, --verbose
            output detailed logs to standard out

    Author:
        Written by Anthony Lam
"""

import os, re, argparse, logging

# Configure parse
parser = argparse.ArgumentParser(
    description="Organize a directory using patterns",
    usage="python3 organize [-h] [options] path/to/source/directory"
)
parser.add_argument(
    "src",
    help="Path to directory containing files to be organized.",
    metavar="SOURCE"
)
parser.add_argument(
    "-d", "--destination",
    help="Path to a target directory to create subdirectories and move files to. If excluded will be the same as src.",
    dest="dest",
    metavar="DESTINATION"
)
parser.add_argument(
    "-p", "--pattern",
    help="Specify custom regex to match files.",
    default="^(.*?)_(.*?)_.*?\\..{3,4}$"
)
parser.add_argument(
    "-v", "--verbose",
    help="Set verbose output.",
    action="store_true"
)

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def get_file_paths_table(path, **kwargs):
    """
    :param path: path to root directory
    :param kwargs: optional
    :return: {sub_dir_path: set(file names)}
    """
    logger.info("Building file LUT...")
    paths = dict()
    pattern = kwargs.get("pattern", None)
    if not pattern:
        pattern = "^(.*?)_(.*?)_.*?\\..{3,4}$"
    logger.info("Using pattern: {}".format(pattern))
    regex = re.compile(pattern)
    try:
        for file in os.listdir(path):
            logger.debug("Checking: {}".format(file))
            match = regex.match(file)
            if match:
                logger.info("Found match: {}".format(file))
                logger.debug("Group captured: {}".format(match.groups()))
                subdir_path = os.path.join("", *match.groups())
                if not paths.get(subdir_path):
                    logger.info("Building path at {}.".format(subdir_path))
                    paths[subdir_path] = set()
                paths[subdir_path].add(file)

    except FileNotFoundError as err:
        logger.error("{} is an invalid path.".format(path))
        raise FileNotFoundError("Please provide a valid path.")
    if not paths:
        logger.warning("No files were found. Please check directory or provide a different regex.")
    return paths


def create_subdirectories(root_path, paths_table, **kwargs):
    """
    Creates subdirectory at root_path using keys from paths_table
    :param root_path: path to directory where folders are to be made
    :param paths_table: {"subDirPath" : set of file names}
    :param kwargs:
    :return:
    """
    num_made = 0
    for path, files in paths_table.items():
        # Note: need to ensure parent directory also does not conflict with any files
        path = os.path.join(root_path, path)
        if os.path.exists(path):
            if os.path.isfile(path):
                logger.warning("Dir name conflicts with file at {}.".format(path))
                # Move file to a temp location to deal with conflicts.
                logger.info("Moving file to temp directory in target directory")
                suspected_filename = os.path.basename(path.rstrip(os.sep))
                temp_path = os.path.join(root_path, "temp")
                dest = os.path.join(temp_path, suspected_filename)
                if not os.path.exists(temp_path):
                    os.makedirs(temp_path, mode=0o744)
                if not os.path.exists(dest):
                    os.rename(path, dest)
                else:
                    os.rename(path, dest+"temp")
            # No need to remake any directories
            else:
                continue
        try:
            os.makedirs(path, mode=0o744)
            logger.info("Dir made at {} with permission set to {}.".format(path, "0o744"))
            num_made += 1
        except OSError as err:
            logger.warning(err)
            logger.warning("Failed to make path. Skipping. Path might already exist")
    logger.info("{} leaf directories made.".format(num_made))
    return len(paths_table.keys()) - num_made


def organize(source, destination, **kwargs):
    """
    Scans source for files that fit pattern. When files are found, create any need directory at destination, if needed,
    and moves source file to correct based on pattern match.
    :param source: dir to take files from
    :param destination: destination root folder of all the files
    :param kwargs:
    :return:
    """
    table = get_file_paths_table(source, pattern=kwargs.get("pattern"), verbose=kwargs.get("verbose", False))
    # stop when nothing left to do
    if not table:
        logger.info("Did not find anything to organize.")
        return
    create_subdirectories(destination, table, verbose=kwargs.get("verbose", False))
    for path, files in table.items():
        for file in files:
            src_path = os.path.join(source, file)
            dest_path = os.path.join(destination, path, file)
            # avoid writing over files already in the destination & avoid conflicts with dir
            if os.path.exists(dest_path):
                logger.warning("Skipping {} because a file is already detected at {}.".format(file, dest_path))
                continue
            logger.debug("Moving {} to {}.".format(file, dest_path))
            os.rename(src_path, dest_path)
            logger.info("{} moved to {}.".format(file, dest_path))



if __name__ == "__main__":
    cl_inp = parser.parse_args()
    src = cl_inp.src
    dest = cl_inp.dest if cl_inp.dest else src
    pattern = cl_inp.pattern
    verbose = cl_inp.verbose
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)
    organize(src, dest, pattern=pattern, verbose=verbose)
