import click

from . import core


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
    core.adb_connect(interface)


@cli.command()
@click.option('--source', '-s', default='~/Downloads/',
              help='Enter source location.')
@click.option('--destination', '-d', default='~/Dropbox/books/',
              help='Enter destination location.')
def send_to_kindle(source, destination):
    """
    Send books to kindle via Dropbox/IFTTT.
    """
    core.send_to_kindle(source, destination)


@cli.command()
@click.option('--directory', '-d', default=None)
def fix_imports(directory):
    """
    Fix imports in a python project.
    """
    core.fix_imports(directory)


@cli.command()
def fix_build(directory=None):
    """
    Fix a failing CI build.
    """
    core.fix_build(directory)


@cli.command()
@click.option('--from_date', '-f', default=None)
@click.option('--to_date', '-t', default=None)
@click.option('--state', '-s', default=None)
def download_imd_data(from_date, to_date, state):
    """
    Download IMD data for given range.
    """
    core.download_imd_data(from_date, to_date, state)


@cli.command()
@click.option('--ipa', '-i', default=None)
def ipa_install(ipa):
    """
    Resign & install iOS apps.
    """
    core.ipa_install(ipa)


@cli.command()
@click.option('--engine', '-e', default=None)
@click.option('--file_name', '-f', default=None)
@click.option('--language', '-l', default=None)
@click.option('--output_dir', '-o', default=None)
def ocr(engine, file_name, language, output_dir):
    """
    Run given OCR engine on given image.
    """
    core.ocr(engine, file_name, language, output_dir)


@cli.command()
@click.option('--source', '-s')
@click.option('--destination', '-d', default=None)
def split_pdf(source, destination):
    """
    Split pdf horizontally/vertically.
    """
    core.split_pdf(source, destination)


@cli.command()
@click.option('--book', '-b')
def download_book(book):
    """
    Search and download book by name
    """
    core.download_book(book)


@cli.command()
@click.option('--directory', '-d', default=None)
def organize_books(directory):
    """
    Organize books in a specified directory.
    """
    core.organize_books(directory)


@cli.command()
def organize_photos(directory=None):
    """
    Organize photos by date.
    """
    core.organize_photos(directory)


@cli.command()
def organize_downloads(directory=None):
    """
    Organize downloaded files.
    """
    core.organize_downloads(directory)


@cli.command()
def download_subtitles(directory=None):
    """
    Download subtitles for videos in a directory.
    """
    core.download_subtitles(directory)


@cli.command()
@click.option('--sort', '-s', default=None)
def rate_movies(sort, directory=None):
    """
    Show IMDb/RT ratings for movies and series.
    """
    print(sort)
    core.rate_movies(directory, sort)


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
    core.rent_receipts(name, amount, owner_name, address, year)


@cli.command()
@click.option('--number', '-n', default=None)
def validate_aadhaar(number):
    """
    Check if given AADHAAR number is valid or not.
    """
    core.validate_aadhaar(number)


@cli.command()
@click.option('--file', '-f', default='Procfile')
def procfile(file):
    """
    Start processes in Procfile
    """
    core.procfile(file)


@cli.command()
def nsedb():
    """
    Create/Sync NSE stocks OHLC data.
    """
    core.nsedb()


@cli.command()
def otp():
    """
    Show OTP
    """
    core.otp()


@cli.command()
@click.option('--column', '-c')
@click.option('--uri', '-u')
@click.option('--duration', '-d', default=1)
def pg_stats(uri,column, duration):
    """
    Show stats for postgres database.
    """
    core.pg_stats(uri, column, duration)
