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
        print('Creation of the directory {} failed' .format(corpusdir) )
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


def compile_zlibng():
    """compile variants of gz"""

    methods = ['gcc', 'clang']
    ccompiler = ['gcc', 'clang']
    cppcompiler = ['g++', 'clang++']
    if platform.system() == 'Darwin':
        print('Warning MacOS alias gcc->clang!')
    basedir = os.getcwd()
    exedir = os.path.join(basedir, 'exe')
    #if os.path.isdir(exedir):
    #    rmtree(exedir)
    try:
        os.mkdir(exedir)
    except OSError:
        print ("Creation of the directory {} failed" .format(exedir) )
    gzdir = os.path.join(basedir, 'gz')
    if os.path.isdir(gzdir):
        rmtree(gzdir)
    cmd = 'git clone https://github.com/zlib-ng/zlib-ng.git '+gzdir
    subprocess.call(cmd, shell=True)
    gzdir = os.path.join(gzdir,'build')
    gzexe = os.path.join(gzdir, 'minigzip')
    ext = ''
    if platform.system() == 'Windows':
        ext = '.exe'
    gzexe = gzexe + ext
    for m in range(len(methods)):
        method = methods[m]
        os.chdir(basedir)
        if os.path.isdir(gzdir):
            rmtree(gzdir)
        os.mkdir(gzdir)
        os.chdir(gzdir)
        cmd = 'cmake -DCMAKE_C_COMPILER='+ccompiler[m]+' -DCMAKE_CXX_COMPILER='+cppcompiler[m]+' -DZLIB_COMPAT=ON  ..'
        subprocess.call(cmd, shell=True)
        #cmd = 'make'
        #if platform.system() == 'Windows':
        cmd = 'cmake --build . --config Release'
        subprocess.call(cmd, shell=True)
        outnm = os.path.join(exedir, 'minigz' + method + ext)
        print (gzexe + '->' + outnm)
        shutil.move(gzexe, outnm)
        st = os.stat(outnm)
        os.chmod(outnm, st.st_mode | stat.S_IEXEC)
        os.chdir(basedir)


def compile_cloudflare():
    """compile variants of gz"""

    methods = ['gccCF', 'clangCF']
    ccompiler = ['gcc', 'clang']
    cppcompiler = ['g++', 'clang++']
    if platform.system() == 'Darwin':
        print('Warning MacOS alias gcc->clang!')
    basedir = os.getcwd()
    exedir = os.path.join(basedir, 'exe')
    #if os.path.isdir(exedir):
    #    rmtree(exedir)
    try:
        os.mkdir(exedir)
    except OSError:
        print ("Creation of the directory {} failed" .format(exedir) )
    gzdir = os.path.join(basedir, 'gz')
    if os.path.isdir(gzdir):
        rmtree(gzdir)
    cmd = 'git clone https://github.com/rordenlab/zlib.git '+gzdir
    subprocess.call(cmd, shell=True)
    gzdir = os.path.join(gzdir,'build')
    gzexe = os.path.join(gzdir, 'minigzip')
    ext = ''
    if platform.system() == 'Windows':
        ext = '.exe'
    gzexe = gzexe + ext
    for m in range(len(methods)):
        method = methods[m]
        os.chdir(basedir)
        if os.path.isdir(gzdir):
            rmtree(gzdir)
        os.mkdir(gzdir)
        os.chdir(gzdir)
        cmd = 'cmake -DCMAKE_C_COMPILER='+ccompiler[m]+' -DCMAKE_CXX_COMPILER='+cppcompiler[m]+' -DBUILD_EXAMPLES=ON -DUSE_STATIC_RUNTIME=ON  ..'
        subprocess.call(cmd, shell=True)
        cmd = 'cmake --build .'
        subprocess.call(cmd, shell=True)
        outnm = os.path.join(exedir, 'minigz' + method + ext)
        print (gzexe + '->' + outnm)
        shutil.move(gzexe, outnm)
        st = os.stat(outnm)
        os.chmod(outnm, st.st_mode | stat.S_IEXEC)
        os.chdir(basedir)


if __name__ == '__main__':
    """compile variants of zlib and sample compression corpus"""

    install_silesia_corpus()
    compile_cloudflare()
    compile_zlibng()
