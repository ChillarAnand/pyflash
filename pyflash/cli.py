import os
import subprocess

import click
from isign import isign

from .utils import imd_data, imp_mgc_fixup, to_kindle, ak_dynamic_scan
from .utils import pyformat as _pyformat
from .utils import mopy as _mopy


@click.group()
def cli():
    pass


@cli.command()
@click.option('--source', '-s', default='/home/chillaranand/Downloads/',
              help='Enter source location.')
@click.option('--destination', '-d',
              default='/home/chillaranand/Dropbox/books/',
              help='Enter source location.')
@click.option('--kindle', '-k', default='anand21nanda@kindle.com',
              help='Your kindle mail.')
def send_to_kindle(source, destination, kindle):
    click.echo('Looking for books...')
    to_kindle(source, destination)


@cli.command()
def im_fixup():
    click.echo('Fixing imports in python project')
    project_root = os.getcwd()
    imp_mgc_fixup(project_root)


@cli.command()
def pyformat():
    click.echo('Fixing code style in project')
    project_root = os.getcwd()
    _pyformat(project_root)


@cli.command()
def mopy():
    cwd = os.getcwd()
    _mopy(cwd=cwd)


@cli.command()
@click.option('--from_date', '-f', default=None)
@click.option('--to_date', '-t', default=None)
@click.option('--state', '-s', default=None)
def imd(from_date, to_date, state):
    click.echo('Getting IMD data')
    imd_data(from_date, to_date, state)


@cli.command()
@click.option('--num', '-n', default=None)
@click.option('--debug', '-d', default=False)
def ak_dynamic(num, debug):
    ak_dynamic_scan(num, debug)


@cli.command()
@click.option('--ipa', '-i', default=None)
def ios_install(ipa):
    ipa = os.path.abspath(ipa)
    print('Resigning ipa: {}'.format(ipa))
    isign.resign(ipa, output_path=ipa)
    cmd = 'ideviceinstaller -i {}'.format(ipa)
    subprocess.check_output(cmd.split())
