import os
import sys
import platform

def milis_to_alpha(mili: 'int|str'):
    '''Converts each digit in milisecond to alphabet in lower case.'''
    alpha = ''
    for digit in str(mili):
        alpha += chr(ord('a') + int(digit))
    return alpha


def cls():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
