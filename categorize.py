#! /usr/bin/env python3
"""
    Name:
        categorize - extension based file grouping tool

    Synopsis:
        categorize.py path [options]

    Description:
        "categorize" is a program written to easily group files into sub-directories by extension. By default it maps
        file extensions to preset subdirectories (For more details looks at --config).

         -v --verbose
            output verbose logs

        -c --config path/to/config/file
            changes file extension mapping to directories. Excluded extension will be ignored.
            By default, the following extensions are used:
                {
                    "audio": [.wav, .mp3, .mid, .midi, .mpa, .wma, .ogg]
                    "documents": [.doc, .docx, .xls, .xlsx, .ppt, .pptx, .odt, .odt, .pdf, .txt],
                    "compressed": [.zip, .7z, .gz, .arj, .pkg, .deb, .rpm, .z, .zip],
                    "data": [.csv, .dat, .db, .dbf, .log, .mdb, .sql, .sav, .xml],
                    "images": [.ai, .bmp, .png, .jpeg, .jpg, .gif, .ico, .ps, .psd, .svg, .tif, .tiff],
                    "videos": [.3g2, .3gp, .avi, .flv, .h264, .m4v, .mkv, .mov, .mp4, .mpg, .mpeg, .swf, .rm, .vob ,.wmv]
                }
            Additionally, a default mapping exists for directories as well. If there exists multiple different
            categories that share the same parent directory then they will be created under the parent directory
            otherwise the folder will be made by themselves. e.g. if only audio files exist then and audio directory
            will be made but if both audio and images exists then then a media directory will be made that contains
            both audio and images subdirectories.
            By default, the following directory mapping is used:
                {
                    "media": [audio, images, videos]
                }
            A config file can be used to allow for custom extension mapping. To do so, the file is expected to obey
            the following format.
            [EXTENSION]
            dirname: [list of extensions]

            [DIRECTORY]
            parentDir: [list of subdirectories]

        -d --destination path/to/target
            Files can optionally be grouped under a different folder.

        -s --specific dirname [list of comma seperated extensions]
            Target only a certain group of directories.

    Author:
        Written by Anthony Lam
"""

import os
import re
import logging
import argparse
import configparser


DEFAULT_CONFIG = {
    "EXTENSION": {
        "audio": {".wav", ".mp3", ".mid", ".midi", ".mpa", ".wma", ".ogg"},
        "documents": {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".odt", ".pdf", ".txt"},
        "compressed": {".zip", ".7z", ".gz", ".arj", ".pkg", ".deb", ".rpm", ".z", ".zip"},
        "data": {".csv", ".dat", ".db", ".dbf", ".log", ".mdb", ".sql", ".sav", ".xml"},
        "images": {".ai", ".bmp", ".png", ".jpeg", ".jpg", ".gif", ".ico", ".ps", ".psd", ".svg", ".tif", ".tiff"},
        "videos": {".3g2", ".3gp", ".avi", ".flv", ".h264", ".m4v", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".swf",
                   ".rm", ".vob", ".wmv"}
    },
    "DIRECTORY":{
        "media": {"images", "videos", "audio"}
    }

}


# Setup argparser
parser = argparse.ArgumentParser(
    description="extension based file grouping tool",
    usage="python3 categorize.py [-h] [options] path/to/source/directory ",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help= "Output verbose."
)
parser.add_argument(
    "-d", "--destination",
    dest="dest",
    help="Files can optionally be grouped under a different folder.",
    metavar="path/to/target/directory"
)
parser.add_argument(
    "-c", "--config",
    metavar="path/to/config/file",
    help="""
    changes file extension mapping to directories. Excluded extension will be ignored.
            By default, the following extensions are used:
                {
                    "audio": [.wav, .mp3, .mid, .midi, .mpa, .wma, .ogg]
                    "documents": [.doc, .docx, .xls, .xlsx, .ppt, .pptx, .odt, .odt, .pdf, .txt],
                    "compressed": [.zip, .7z, .gz, .arj, .pkg, .deb, .rpm, .z, .zip],
                    "data": [.csv, .dat, .db, .dbf, .log, .mdb, .sql, .sav, .xml],
                    "images": [.ai, .bmp, .png, .jpeg, .jpg, .gif, .ico, .ps, .psd, .svg, .tif, .tiff],
                    "videos": [.3g2, .3gp, .avi, .flv, .h264, .m4v, .mkv, .mov, .mp4, .mpg, .mpeg, .swf, .rm, .vob ,.wmv]
                }
            Additionally, a default mapping exists for directories as well. If there exists multiple different 
            categories that share the same parent directory then they will be created under the parent directory
            otherwise the folder will be made by themselves. e.g. if only audio files exist then and audio directory
            will be made but if both audio and images exists then then a media directory will be made that contains
            both audio and images subdirectories.
            By default, the following directory mapping is used:
                {
                    "media": [audio, images, videos]
                }
            A config file can be used to allow for custom extension mapping. 
            To do so, the file is expected to obey the following format:
            [EXTENSION]
            dirname: [list of extensions]
            
            [DIRECTORY]
            parentDir: [list of subdirectories]
    """
)
parser.add_argument(
    "src",
    help="Path to source directory.",
    metavar="path/to/source/directory"
)


# Set logger with only handler of standard out
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def parse_config_dict(config, **kwargs):
    """
    Takes a config dictionary where values are sequ of strings and creates a new dictionary where each string becomes
    the key and the original key becomes the new value
    :param config: dict {"dirnam" : set {extensions}}
    :return: dict {"extensions": "dirnam"}
    """
    if not isinstance(config, (dict,)):
        raise TypeError("Argument should be of type dict!")
    lut = {}
    for k, v in config.items():
        if not hasattr(v, "__iter__") or isinstance(v, (str,)):
            raise TypeError("Values should be a seq of strings!")
        for item in v:
            lut[item] = k
    return lut


def create_file_table(target, ext_map, **kwargs):
    '''
    Collects all the files in a given directory and group them together by extension based on ext_map
    :param target: path to target dir
    :param ext_map: dict {dirname: set {extensions,}
    :param kwargs:
    :return: dict {"dirname": set {filenames}
    '''
    table = {}
    pattern = "^.*(\\..*)$"
    regex = re.compile(pattern)
    try:
        for basename in os.listdir(target):
            if os.path.isfile(os.path.join(target, basename)):
                match = regex.match(basename)
                ext = match.group(1)
                logger.debug("Matched extension {}".format(ext))
                dir_name_key = ext_map[ext]
                if not table.get(dir_name_key):
                    table[dir_name_key] = set()
                table[dir_name_key].add(basename)
    except FileNotFoundError:
        logger.error("File not found.")
        raise FileNotFoundError("Please provide a valid path to a directory!")
    return table


def categorize(src, destination, config_dict=DEFAULT_CONFIG, **kwargs):
    dir_ext_lut = config_dict["EXTENSION"]
    dir_subdir_lut = config_dict["DIRECTORY"]
    ext_dir_lut = parse_config_dict(dir_ext_lut)
    subdir_dir_lut = parse_config_dict(dir_subdir_lut)
    file_table = create_file_table(src, ext_dir_lut)

    for dir, files in file_table.items():
        path = []
        path.append(dir)
        parent_dir = subdir_dir_lut.get(dir, None)
        while parent_dir:
            path.append(parent_dir)
            parent_dir = subdir_dir_lut.get(parent_dir, None)
        path.reverse()
        path = os.path.join(destination, *path)
        if not os.path.exists(path):
            os.makedirs(path)
        for file in files:
            file_loc = os.path.join(src, file)
            dest_loc = os.path.join(path, file)
            if os.path.exists(dest_loc):
                logger.warning("File at {} naming conflict with file at {}. Skipping.".format(file_loc, dest_loc))
                continue
            os.rename(file_loc, dest_loc)



if __name__ == "__main__":
    cl_inp = parser.parse_args()
    # Set config parser
    config = configparser.ConfigParser()
