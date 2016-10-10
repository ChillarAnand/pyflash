import os
import shutil

import click

from .utils import (convert_to_mobi, get_files_with_pattern, imp_mgc_fixup,
                    imd_data)


@click.command()
@click.option('--as-cowboy', '-c', is_flag=True, help='Greet as a cowboy.')
@click.argument('name', default='world', required=False)
def main(name, as_cowboy):
    """My Tool does one thing, and one thing well."""
    greet = 'Howdy' if as_cowboy else 'Hello'
    click.echo('{0}, {1}.'.format(greet, name))


@click.group()
def cli():
    # click.echo('You have got flash like super powers.')
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
    click.echo('Sending books to your kindle device.')

    patterns = ['*.epub']
    for pattern in patterns:
        files = get_files_with_pattern(pattern, source)
        for filename in files:
            convert_to_mobi(filename)
            shutil.move(filename, "/tmp/")

    patterns = ['*.azw3', '*.mobi']
    for pattern in patterns:
        files = get_files_with_pattern(pattern, source)
        for filename in files:
            # send_to_kindle_mail(filename, kindle)
            try:
                shutil.move(filename, destination)
            except shutil.Error as e:
                print(e)


@cli.command()
def im_fixup():
    click.echo('Fixing imports in python project')
    project_root = os.getcwd()
    imp_mgc_fixup(project_root)


@cli.command()
@click.option('--from_date', '-f', default=None)
@click.option('--to_date', '-t', default=None)
@click.option('--state', '-s', default=None)
def imd(from_date, to_date, state):
    click.echo('Getting IMD data')
    imd_data(from_date, to_date, state)
