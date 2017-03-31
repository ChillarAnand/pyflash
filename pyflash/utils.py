import contextlib
import fcntl
import glob
import logging
import os
import pathlib
import shlex
import shutil
import socket
import struct
import subprocess
from os.path import expanduser


logger = logging.getLogger(__name__)


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


def get_cache_file(name):
    file_path = '~/.cache/{}'.format(name)
    file_path = expanduser(file_path)
    if not os.path.exists(file_path):
        pathlib.Path(file_path).touch()
    return file_path
