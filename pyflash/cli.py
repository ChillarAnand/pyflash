import os
import subprocess

import click

from .core import imd_data, imp_mgc_fixup
from .core import download_book as _download_book
from .core import mopy as _mopy
from .core import ocr as _ocr
from .core import organize_books as _organize_books
from .core import organize_downloads as _organize_downloads
from .core import organize_photos as _organize_photos
from .core import pyformat as _pyformat
from .core import split_pdf as _split_pdf
from .core import send_to_kindle as _send_to_kindle


try:
    from isign import isign
except:
    isign = None


@click.group()
def cli():
    pass


@cli.command()
@click.option('--source', '-s', default='~/Downloads/',
              help='Enter source location.')
@click.option('--destination', '-d', default='~/Dropbox/books/',
              help='Enter destination location.')
def send_to_kindle(source, destination):
    """
    Convert and send books to kindle.
    """
    click.echo('Locating books...')
    _send_to_kindle(source, destination)


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
@click.option('--ipa', '-i', default=None)
def ios_install(ipa):
    ipa = os.path.abspath(ipa)
    print('Resigning ipa: {}'.format(ipa))
    isign.resign(ipa, output_path=ipa)
    cmd = 'ideviceinstaller -i {}'.format(ipa)
    subprocess.check_output(cmd.split())


@cli.command()
@click.option('--engine', '-e', default=None)
@click.option('--file_name', '-f', default=None)
@click.option('--language', '-l', default=None)
@click.option('--output_dir', '-o', default=None)
def ocr(engine, file_name, language, output_dir):
    """
    Run given OCR engine on a given image
    """
    _ocr(engine, file_name, language, output_dir)


@cli.command()
@click.option('--source', '-s')
@click.option('--destination', '-d', default=None)
def split_pdf(source, destination):
    """
    Split pdf horizontally/vertically
    """
    _split_pdf(source, destination)


@cli.command()
@click.option('--book', '-b')
def download_book(book):
    """
    Search and download book by name
    """
    _download_book(book)


@cli.command()
@click.option('--directory', '-d', default=None)
def organize_books(directory):
    """
    Organize books in a specified directory.
    """
    click.echo('Organizing books. Please wait...')
    _organize_books(directory)


@cli.command()
def organize_photos():
    """
    Locate photos and organize them by date.
    """
    click.echo('Sorting & syncing photos')
    _organize_photos()


@cli.command()
def organize_downloads():
    """
    Monitor and organize downloaded files.
    """
    click.echo('Sorting & syncing photos')
    _organize_downloads()
