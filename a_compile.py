#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import stat
import shutil
import subprocess
import platform
import zipfile
from distutils.dir_util import copy_tree

def rmfile(path, retries = 10, sleep = 0.1):
    for i in range(retries):
        try:
            os.chmod(path, stat.S_IWUSR)
            os.remove(path)
        except WindowsError:
            time.sleep(sleep)
        else:
            break


def rmtree(path):
    """Delete folder and contents: shutil.rmtree has issues with read-only files on Windows"""

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            rmfile(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)


def install_silesia_corpus():
    """Install popular Silesia corpus"""

    basedir = os.getcwd()
    corpusdir = os.path.join(basedir, 'silesia')
    if os.path.isdir(corpusdir):
        return
    try:
        os.mkdir(corpusdir)
    except OSError:
        print('Creation of the directory {} failed' .format(corpusdir))
    cmd = 'git clone https://github.com/MiloszKrajewski/SilesiaCorpus silesia'
    print("Installing "+corpusdir);
    subprocess.call(cmd, shell=True)
    os.chdir(corpusdir)
    fnm = 'README.md'
    if os.path.isfile(fnm):
        os.remove(fnm)
    ext = '.zip'
    for item in os.listdir(corpusdir):  # loop through items in dir
        print("+"+item)
        if item.endswith(ext):  # check for ".zip" extension
            file_name = os.path.abspath(item)  # get full path of files
            print(file_name)
            zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
            zip_ref.extractall(corpusdir)  # extract file to dir
            zip_ref.close()  # close file
            os.remove(file_name)  # delete zipped file
    os.chdir(basedir)


def compile_minigzip(name, repository_url, cmake_args):
    """compile variants of gz"""

    methods = ['intel', 'clang', 'gcc', 'msvc']
    method_cmake_args = [
        '-G "NMake Makefiles" -DCMAKE_C_COMPILER=icl',
        '-T ClangCl',
        '-G "MinGW Makefiles"',
        ''
    ]

    if platform.system() == 'Darwin':
        print('Warning MacOS alias gcc->clang!')

    rebuild = False
    repository_tag = None

    basedir = os.getcwd()
    exedir = os.path.join(basedir, 'exe')
    if rebuild:
        if os.path.isdir(exedir):
            rmtree(exedir)
    if not os.path.exists(exedir):
        os.mkdir(exedir)

    gzdir = os.path.join(basedir, 'gz')
    if rebuild:
        if os.path.isdir(gzdir):
            rmtree(gzdir)
        cmd = 'git clone {0} {1}'.format(repository_url, gzdir)
        subprocess.call(cmd, shell=True)
        if repository_tag:
            cmd = 'git checkout {0}'.format(repository_tag)
            subprocess.call(cmd, shell=True)

    gzdir = os.path.join(gzdir, 'build')
    gzexe = os.path.join(gzdir, 'minigzip')
    ext = ''
    if platform.system() == 'Windows':
        ext = '.exe'
    gzexe = gzexe + ext
    for m in range(len(methods)):

        method = methods[m]
        os.chdir(basedir)

        if rebuild:
            if os.path.isdir(gzdir):
                rmtree(gzdir)
            os.mkdir(gzdir)
        else:
            cache_file = os.path.join(gzdir, "CMakeCache.txt")
            if os.path.exists(cache_file):
                rmfile(cache_file)

        os.chdir(gzdir)

        cmd = 'cmake .. {0} {1}'.format(method_cmake_args[m], cmake_args)
        print(cmd)
        subprocess.call(cmd, shell=True)

        cmd = 'cmake --build . --config Release'
        subprocess.call(cmd, shell=True)
        outnm = os.path.join(exedir, 'minigz-{0}-{1}{2}'.format(name, method, ext))

        gzexe = os.path.join(gzdir, 'Release', 'minigzip') + ext
        if not os.path.exists(gzexe):
            gzexe = os.path.join(gzdir, 'minigzip') + ext
        print(gzexe + '->' + outnm)
        shutil.move(gzexe, outnm)

        st = os.stat(outnm)
        os.chmod(outnm, st.st_mode | stat.S_IEXEC)
        os.chdir(basedir)


if __name__ == '__main__':
    """compile variants of zlib and sample compression corpus"""

    install_silesia_corpus()
    compile_minigzip('ng', 'https://github.com/zlib-ng/zlib-ng.git', '-DZLIB_ENABLE_TESTS=ON -DZLIB_COMPAT=ON')
    #compile_minigzip('cf', 'https://github.com/rordenlab/zlib.git', ' -DBUILD_EXAMPLES=ON -DUSE_STATIC_RUNTIME=ON')
