#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__appname__ = "MBuseful"
__author__  = "Mark Butterworth"
__version__ = "0.2 1909"
__license__ = "GNU GPL 3.0 or later"

import re
from contextlib import contextmanager
from collections import deque
import itertools
import os
import sys
import glob
import ctypes



_NSRE = re.compile('([0-9]+)')
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in _NSRE.split(s)]



@contextmanager
def working_directory(path):
    current_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(current_dir)
# use case;
# with working_directory('mytemp'):



def moving_average(iterable, n=3):
    # moving_average([40, 30, 50, 46, 39, 44]) --> 40.0 42.0 45.0 43.0
    it = iter(iterable)
    d = deque(itertools.islice(it, n-1))
    d.appendleft(0)
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield s / float(n)



def listsummary(inlist, minprefixlen=2, minprefixpercent=0.5, groupthreshold=2):
    '''
    Given a list of strings produce a summary dictionary keyed by prefix with list of suffixs

    Keyword args:
    minprefix = minimum length of prefix
    groupthreshold = minimum number of items grouped

    '''

    if not inlist: return {}

    #Change the input list into a unique set then sort by reverse length.
    sa=sorted(set(inlist),key=lambda x: -len(x))
    maxlen=len(sa[0])

    fd=dict()
    for i in range(maxlen-1,minprefixlen-1,-1):
        d=dict()
        for item in sa:
            if len(item)<=i: break
            if i > (len(item)*minprefixpercent):
                k=item[:i]
                if k in d:
                    d[k].append(item)
                else:
                    d[k]=[item]

        for k in d:
            if len(d[k]) >= groupthreshold:
                for v in d[k]:
                    if k in fd:
                        fd[k].append(v[i:])
                    else:
                        fd[k]=[v[i:]]
                    sa.remove(v)

    for i in sa:
        fd[i]=[]

    return fd



def findrelfile(rootdir, filenames):
    """Find file based on list of relative filenames of usual locations"""
    
    if type(filenames) == str: filenames = [ filenames ]

    for relpath in filenames:
        if rootdir[-len(relpath):] == relpath: # captures case where rootdir is same as one of filenames
            return rootdir 
        basename = None
        while relpath != '':
            relpath, nextbase = os.path.split(relpath)
            if basename: basename = os.path.join(nextbase, basename) 
            else: basename = nextbase
            lookfor = os.path.join(rootdir, basename)
            #print(f'lookfor {lookfor}')
            if os.path.exists(lookfor): return lookfor
    return None



def findfilespec(rootdir, wildcards):
    """Find files based on relative wildcards of usual locations"""
    
    if type(wildcards) == str: wildcards = [ wildcards ]

    for spec in wildcards:
        path = spec
        basename = None
        while path != '':
            path, nextbase = os.path.split(path)
            if basename: basename = os.path.join(nextbase, basename) 
            else: basename = nextbase
            lookfor = os.path.join(rootdir, basename)
            files = glob.glob(lookfor)
            if len(files) > 0: return os.path.dirname(lookfor)
    return None



def copy2clip(text, stdout=None): # seems no longer to work under python3
    """Uses tkinter (which is distributed with python) to copy text into the clipboard"""
    # try:
    #     from Tkinter import Tk  # python2
    # except ImportError:
    from tkinter import Tk # python3
    

    if not stdout:
        stdout = sys.stdout
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.update()  # now it stays on the clipboard after the window is closed
    r.destroy()
    print('(copied to clipboard)', file=stdout)



def otherclip(text, stdout=None):
    """uses pyperclip library to copy text to clipboard"""
    try:
        import pyperclip
    except ImportError:
        return

    if not stdout:
        stdout = sys.stdout

    pyperclip.copy(text)
    print('(copied to clipboard)', file=stdout)



# uses ctypes to directly access win32 api and get clipboard
CF_TEXT = 1
kernel32 = ctypes.windll.kernel32
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
user32 = ctypes.windll.user32
user32.GetClipboardData.restype = ctypes.c_void_p

def get_clipboard_text():
    user32.OpenClipboard(0)
    try:
        if user32.IsClipboardFormatAvailable(CF_TEXT):
            data = user32.GetClipboardData(CF_TEXT)
            data_locked = kernel32.GlobalLock(data)
            text = ctypes.c_char_p(data_locked)
            value = text.value
            kernel32.GlobalUnlock(data_locked)
            return value
    finally:
        user32.CloseClipboard()



def filescan(text, filename):
    """returns a list of positions in file of text"""

    with open(filename) as fh:
        data = fh.read()
        index = list()
        pos = 0
        while True:
            pos = data.find(text, pos)
            if pos == -1: break
            index.append(pos)
            pos = pos+len(text)
        return index