import contextlib
import glob
import logging
import os
import pathlib
import sys
import shlex
import shutil
import socket
import struct
import subprocess
from enum import Enum
from os.path import expanduser
from urllib.parse import quote_plus
import pickle
import collections

import fcntl
import requests
import guessit

logger = logging.getLogger(__name__)


class FileType(Enum):
    BOOK = 0
    IMAGE = 1
    VIDEO = 2


TARGET_DIRS = {
    FileType.BOOK: expanduser('~/Documents/'),
    FileType.IMAGE: expanduser('~/Pictures/'),
    FileType.VIDEO: expanduser('~/Videos/'),
}


@contextlib.contextmanager
def cd(directory):
    cwd = os.getcwd()
    os.chdir(os.path.expanduser(directory))
    try:
        yield
    finally:
        os.chdir(cwd)


def ebook_meta_data(filename):
    cmd = 'ebook-meta "{}"'.format(filename)
    output = run_shell_command(cmd)
    split_strs = (line.split(' : ') for line in output.split('\n') if line)
    meta_data = {key.strip(): value.strip() for key, value in split_strs}
    return meta_data


def matched_files(patterns, root_dir):
    for pattern in patterns:
        path = os.path.join(root_dir, '**', pattern)
        for filename in glob.iglob(path, recursive=True):
            yield filename


def convert_books(directory, source='.epub', target='.mobi'):
    patterns = ['*{}'.format(source)]
    files = matched_files(patterns, directory)
    for filename in files:
        file_path, ext = os.path.splitext(filename)
        target_file = file_path + target
        command = ['ebook-convert', filename, target_file]
        logger.info(command)
        subprocess.check_output(command)
        shutil.move(filename, "/tmp/")


def get_ip(iface='wlo1'):
    ifreq = struct.pack(
        '16sH14s', iface.encode('utf-8'), socket.AF_INET, b'\x00'*14
    )
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockfd = sock.fileno()
        SIOCGIFADDR = 0x8915
        res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
    except:
        return None
    ip = struct.unpack('16sH2x4s8x', res)[2]
    return socket.inet_ntoa(ip)


def ping(host, port=80):
    print(host)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((host, port))
        sock.close()
        return True
    except Exception as e:
        return False


def envar(var):
    var = var.upper()
    var = os.environ.get(var, None)
    if not var:
        print('{} not set in environment'.var.upper())
    return var


def run_shell_command(cmd):
    logger.info(cmd)
    cmd = shlex.split(cmd)
    out = subprocess.check_output(cmd)
    return out.decode('utf-8')


def execute_shell_command(cmd):
    logger.info(cmd)
    cmd = shlex.split(cmd)
    subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stdout)


def get_active_hosts(network):
    cmd = 'nmap -sP {}'.format(network)
    out = run_shell_command(cmd)
    return out


def file_list(directory):
    """
    Recursively yield full path of files in a directory.
    """
    for root_dir, subdirs, files in os.walk(directory):
        for fname in files:
            yield os.path.join(root_dir, fname)


def get_cache_file(filename):
    file_path = '~/.cache/{}'.format(filename)
    file_path = expanduser(file_path)
    if not os.path.exists(file_path):
        if file_path.endswith('.pkl'):
            with open(file_path, 'wb') as fh:
                pickle.dump(collections.defaultdict(dict), fh)
        else:
            pathlib.Path(file_path).touch()
    return file_path


def guess_file_type(file):
    ext = file.split('.')[-1].lower()
    if ext in {'png', 'jpg'}:
        return FileType.IMAGE
    if ext in {'mp4', 'mkv', 'avi'}:
        return FileType.VIDEO
    if ext in {'mobi', 'pdf', 'epub'}:
        return FileType.BOOK


def relocate_file(file):
    f_type = guess_file_type(file)
    if not f_type:
        return
    target_dir = TARGET_DIRS[f_type]
    logger.info('Relocating {} -> {}'.format(file, target_dir))
    shutil.move(file, os.path.join(target_dir))


def movie_info(title):
    cache = get_cache()
    try:
        data = cache['omdbapi'][title]
    except KeyError:
        url = 'http://www.omdbapi.com/?t={}'.format(quote_plus(title))
        logger.info('Fetching {}'.format(url))
        response = requests.get(url)
        data = response.json()
        if 'Error' in data:
            data = None
        cache['omdbapi'][title] = data
        update_cache(cache)

    return data


def rt_rating(movie):
    return 5


verhoeff_table_d = (
    (0,1,2,3,4,5,6,7,8,9),
    (1,2,3,4,0,6,7,8,9,5),
    (2,3,4,0,1,7,8,9,5,6),
    (3,4,0,1,2,8,9,5,6,7),
    (4,0,1,2,3,9,5,6,7,8),
    (5,9,8,7,6,0,4,3,2,1),
    (6,5,9,8,7,1,0,4,3,2),
    (7,6,5,9,8,2,1,0,4,3),
    (8,7,6,5,9,3,2,1,0,4),
    (9,8,7,6,5,4,3,2,1,0))
verhoeff_table_p = (
    (0,1,2,3,4,5,6,7,8,9),
    (1,5,7,6,2,8,3,0,9,4),
    (5,8,0,3,7,9,6,1,4,2),
    (8,9,1,6,0,4,3,5,2,7),
    (9,4,5,3,1,2,6,8,7,0),
    (4,2,8,6,5,7,3,9,0,1),
    (2,7,9,3,8,0,6,4,1,5),
    (7,0,4,6,9,1,3,2,5,8))


verhoeff_table_inv = (0,4,3,2,1,5,6,7,8,9)


def calcsum(number):
    """For a given number returns a Verhoeff checksum digit"""
    c = 0
    for i, item in enumerate(reversed(str(number))):
        c = verhoeff_table_d[c][verhoeff_table_p[(i+1)%8][int(item)]]
    return verhoeff_table_inv[c]


def checksum(number):
    """For a given number generates a Verhoeff digit and
    returns number + digit"""
    c = 0
    for i, item in enumerate(reversed(str(number))):
        c = verhoeff_table_d[c][verhoeff_table_p[i % 8][int(item)]]
    return c


def generateVerhoeff(number):
    """For a given number returns number + Verhoeff checksum digit"""
    return "%s%s" % (number, calcsum(number))


def validateVerhoeff(number):
    """Validate Verhoeff checksummed number (checksum is last digit)"""
    return checksum(number) == 0


def get_cache():
    cache_file = get_cache_file('pyflash.pkl')
    with open(cache_file, 'rb') as fh:
        return pickle.load(fh)


def update_cache(cache):
    cache_file = get_cache_file('pyflash.pkl')
    with open(cache_file, 'wb') as fh:
        return pickle.dump(cache, fh)


def get_title(file):
    movie = guessit.guessit(file)
    container = movie.get('container', None)
    if container and container in {'srt'}:
        return
    return movie['title']
