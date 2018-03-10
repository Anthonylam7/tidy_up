# Tidy Up
This project several scripts for organizing files in various ways.<br><br>
<strong>"organize.py"</strong> is a flexible script for keep files neat and orderly. It is
most useful for settings such as academia where keeping a consistent file format helps in 
maintain good notes.
<br>

### Example: ~/school/ENEE440_HOMEWORK_1.pdf
```bash
~$ ls school/
ENEE440_HOMEWORK_1.pdf
~$ organize.py school
~$ ls school/
ENEE440
~$ ls school/ENEE440/
HOMEWORK
~$ ls school/ENEE440/HOMEWORK/
ENEE440_HOMEWORK_1.pdf
```
<strong>organize.py</strong> uses a default pattern "GROUP1_GROUP2_GROUP3.EXTENSION" to 
match file names. This makes it very useful for course (as intended). In the example 
above, the file will be placed at the path 
`/school/ENEE440/HOMEWORK/ENEE440_HOMEWORK_1.pdf`
<br><br>

<strong>"collect.py"</strong> is useful for grouping files by extension. Similar to 
<strong>"organize.py"</strong>, it create subdirectories at a specified path and groups
files by their extension. It is ideal for sorting out large download folders.

### Example
```bash
~$ ls Downloads/
junk.zip cat.jpeg important.pdf lecture1.ppt thatcoolsong.mp3 mustwatchclip.mp4
~$ collect.py Downloads
~$ ls Downloads/
others images docs video audio fileLUT.txt
```
<strong>"collect.py"</strong> optionally uses a config to map extensions to directories.
Additionally, file hierarchy can be specified for nesting directories. A look up table
is created/managed at the specified source directory to allow users to provide an
alternative way to search for files.


## Basic Usage
```bash
~$ chmod 700 organize.py
~$ organize.py /path/to/source
```
This will create subdirectories based on regex capture groups in the path to source directory and move files to their corresponding directories.
