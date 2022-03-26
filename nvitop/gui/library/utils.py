# This file is part of nvitop, the interactive NVIDIA-GPU process viewer.
# License: GNU GPL version 3.

# pylint: disable=missing-module-docstring,missing-function-docstring
# pylint: disable=disallowed-name,invalid-name

import getpass
import math
import os
import platform
import sys

from nvitop.core import host, NA
from nvitop.gui.library.widestring import WideString

if host.WINDOWS:
    try:
        from colorama import init
    except ImportError:
        pass
    else:
        init()

try:
    from termcolor import colored as _colored
except ImportError:
    def _colored(text, color=None, on_color=None, attrs=None):  # pylint: disable=unused-argument
        return text


COLOR = sys.stdout.isatty()


def set_color(value):
    global COLOR  # pylint: disable=global-statement
    COLOR = bool(value)


def colored(text, color=None, on_color=None, attrs=None):
    if COLOR:
        return _colored(text, color=color, on_color=on_color, attrs=attrs)
    return text


def cut_string(s, maxlen, padstr='...', align='left'):
    assert align in ('left', 'right')

    if not isinstance(s, str):
        s = str(s)
    s = WideString(s)

    if len(s) <= maxlen:
        return str(s)
    if align == 'left':
        return str(s[:maxlen - len(padstr)] + padstr)
    return str(padstr + s[-(maxlen - len(padstr)):])


def make_bar(prefix, percent, width):
    bar = '{}: '.format(prefix)
    if percent != NA and not (isinstance(percent, float) and not math.isfinite(percent)):
        if isinstance(percent, str) and percent.endswith('%'):
            percent = percent.replace('%', '')
            percent = float(percent) if '.' in percent else int(percent)
        percentage = max(0.0, min(float(percent) / 100.0, 1.0))
        quotient, remainder = divmod(max(1, round(8 * (width - len(bar) - 4) * percentage)), 8)
        bar += '█' * quotient
        if remainder > 0:
            bar += ' ▏▎▍▌▋▊▉'[remainder]
        if isinstance(percent, float) and len('{} {:.1f}%'.format(bar, percent)) <= width:
            bar += ' {:.1f}%'.format(percent)
        else:
            bar += ' {:d}%'.format(min(round(percent), 100)).replace('100%', 'MAX')
    else:
        bar += '░' * (width - len(bar) - 4) + ' N/A'
    return bar.ljust(width)


try:
    USERNAME = getpass.getuser()
except ModuleNotFoundError:
    USERNAME = os.getlogin()

if host.WINDOWS:  # pylint: disable=no-member
    import ctypes
    SUPERUSER = bool(ctypes.windll.shell32.IsUserAnAdmin())
else:
    try:
        SUPERUSER = (os.geteuid() == 0)
    except AttributeError:
        try:
            SUPERUSER = (os.getuid() == 0)
        except AttributeError:
            SUPERUSER = False

HOSTNAME = platform.node()
if host.WSL:
    HOSTNAME = '{} (WSL)'.format(HOSTNAME)

USERCONTEXT = '{}@{}'.format(USERNAME, HOSTNAME)
