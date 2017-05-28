import click

from .core import adb_connect as _adb_connect
from .core import download_book as _download_book
from .core import download_imd_data as _download_imd_data
from .core import download_subtitles as _download_subtitles
from .core import fix_imports as _fix_imports
from .core import fix_build as _fix_build
from .core import ipa_install as _ipa_install
from .core import organize_downloads as _organize_downloads
from .core import ocr as _ocr
from .core import organize_books as _organize_books
from .core import organize_photos as _organize_photos
from .core import split_pdf as _split_pdf
from .core import send_to_kindle as _send_to_kindle
from .core import rate_movies as _rate_movies
from .core import rent_receipts as _rent_receipts
from .core import validate_aadhaar as _validate_aadhaar
from .core import procfile as _procfile


try:
    from isign import isign
except:
    isign = None


@click.group()
def cli():
    pass


@cli.command()
def adb_connect(interface=None):
    """
    Scan network and connect to adb via network.
    """
    _adb_connect(interface)


@cli.command()
@click.option('--source', '-s', default='~/Downloads/',
              help='Enter source location.')
@click.option('--destination', '-d', default='~/Dropbox/books/',
              help='Enter destination location.')
def send_to_kindle(source, destination):
    """
    Send books to kindle via Dropbox/IFTTT.
    """
    _send_to_kindle(source, destination)


@cli.command()
def fix_imports(directory=None):
    """
    Fix imports in a python project.
    """
    _fix_imports(directory)


@cli.command()
def fix_build(directory=None):
    """
    Fix a failing CI build.
    """
    _fix_build(directory)


@cli.command()
@click.option('--from_date', '-f', default=None)
@click.option('--to_date', '-t', default=None)
@click.option('--state', '-s', default=None)
def download_imd_data(from_date, to_date, state):
    """
    Download IMD data for given range.
    """
    _download_imd_data(from_date, to_date, state)


@cli.command()
@click.option('--ipa', '-i', default=None)
def ipa_install(ipa):
    """
    Resign & install iOS apps.
    """
    _ipa_install(ipa)


@cli.command()
@click.option('--engine', '-e', default=None)
@click.option('--file_name', '-f', default=None)
@click.option('--language', '-l', default=None)
@click.option('--output_dir', '-o', default=None)
def ocr(engine, file_name, language, output_dir):
    """
    Run given OCR engine on given image.
    """
    _ocr(engine, file_name, language, output_dir)


@cli.command()
@click.option('--source', '-s')
@click.option('--destination', '-d', default=None)
def split_pdf(source, destination):
    """
    Split pdf horizontally/vertically.
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
    _organize_books(directory)


@cli.command()
def organize_photos(directory=None):
    """
    Organize photos by date.
    """
    _organize_photos(directory)


@cli.command()
def organize_downloads(directory=None):
    """
    Organize downloaded files.
    """
    _organize_downloads(directory)


@cli.command()
def download_subtitles(directory=None):
    """
    Download subtitles for videos in a directory.
    """
    _download_subtitles(directory)


@cli.command()
@click.option('--sort', '-s', default=None)
def rate_movies(sort, directory=None):
    """
    Show IMDb/RT ratings for movies and series.
    """
    print(sort)
    _rate_movies(directory, sort)


@cli.command()
def rent_receipts():
    """
    Generate monthly rent receipts for a given FY.
    """
    name = input('Your name [Example: Raj Kumar]: ')
    amount = input('Rent amount [Ex: 8,000]: ')
    owner_name = input('Owner name [Ex: Sekhar Raju]: ')
    address = input('Address [Ex: #26, Gandhi Road, Bangalore]: ')
    year = input('Year [Ex: 2016-17]: ')
    year = int(year[:4])
    _rent_receipts(name, amount, owner_name, address, year)


@cli.command()
@click.option('--number', '-n', default=None)
def validate_aadhaar(number):
    """
    Check if given AADHAAR number is valid or not.
    """
    _validate_aadhaar(number)


@cli.command()
@click.option('--file', '-f', default='Procfile')
def procfile(file):
    """
    Start processes in Procfile
    """
    _procfile(file)
