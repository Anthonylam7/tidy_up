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


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)



if __name__ == "__main__":
    cl_inp = parser.parse_args()