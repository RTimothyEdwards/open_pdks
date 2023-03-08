#!/usr/bin/env python3
import os
import re
from io import BytesIO, BufferedReader, BufferedRandom
import tarfile

"""
  This module tars and compresses a filder location and
  all subdirectories.
"""

# tar and compress a directory in memory and return the result.
def tar_directory(source_dir):
    output = BytesIO()
    with tarfile.open(fileobj=output, mode='w:gz') as archive:
        archive.add(source_dir, arcname=os.path.basename(source_dir), recursive=True)

    return output

# tar and compress the files in a directory, not to include the directory itself.
# 'nodescend' is a list of directories not to descend into, although the directory
# itself will be added.
def tar_directory_contents(source_dir, exclude=[]):
    output = BytesIO()
    curdir = os.getcwd()
    os.chdir(source_dir)

    rexclude = []
    for pattern in exclude:
        rexclude.append(re.compile(pattern))

    with tarfile.open(fileobj=output, mode='w:gz') as archive:
        for root, dirs, files in os.walk('.'):
            for filename in files:
                if root == '.':
                    filepath = filename
                else:
                    rootnodot = os.path.normpath(root)
                    filepath = os.path.join(rootnodot, filename)
                doexclude = False
                for regexp in rexclude:
                    if re.match(regexp, filepath):
                        doexclude = True
                        break
                if not doexclude:
                    try:
                        archive.add(filepath, recursive=False)
                    except PermissionError:
                        pass
            for dirname in dirs[:]:
                if root == '.':
                    dirpath = dirname
                else:
                    rootnodot = os.path.normpath(root)
                    dirpath = os.path.join(rootnodot, dirname)
                doexclude = False
                for regexp in rexclude:
                    if re.match(regexp, dirpath):
                        doexclude = True
                        break
                if doexclude:
                    dirs.remove(dirname)
                else:
                    try:
                        archive.add(dirpath, recursive=False)
                    except PermissionError:
                        pass


    os.chdir(curdir)
    return output

def tar_directory_contents_to_file(source_dir, tarballname, exclude=[]):
    curdir = os.getcwd()
    os.chdir(source_dir)

    rexclude = []
    for pattern in exclude:
        rexclude.append(re.compile(pattern))

    with tarfile.open(tarballname, mode='w:gz') as archive:
        for root, dirs, files in os.walk('.'):
            for filename in files:
                if root == '.':
                    filepath = filename
                else:
                    rootnodot = os.path.normpath(root)
                    filepath = os.path.join(rootnodot, filename)
                doexclude = False
                for regexp in rexclude:
                    if re.match(regexp, filepath):
                        doexclude = True
                        break
                if not doexclude:
                    try:
                        archive.add(filepath, recursive=False)
                    except PermissionError:
                        pass
            for dirname in dirs[:]:
                if root == '.':
                    dirpath = dirname
                else:
                    rootnodot = os.path.normpath(root)
                    dirpath = os.path.join(rootnodot, dirname)
                doexclude = False
                for regexp in rexclude:
                    if re.match(regexp, dirpath):
                        doexclude = True
                        break
                if doexclude:
                    dirs.remove(dirname)
                else:
                    try:
                        archive.add(dirpath, recursive=False)
                    except PermissionError:
                        pass

    os.chdir(curdir)
