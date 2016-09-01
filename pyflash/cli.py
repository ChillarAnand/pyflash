import os
import shutil

import click

from .utils import convert_to_mobi, get_files_with_pattern, send_to_kindle_mail, imp_mgc_fixup


@click.command()
@click.option('--as-cowboy', '-c', is_flag=True, help='Greet as a cowboy.')
@click.argument('name', default='world', required=False)
def main(name, as_cowboy):
    """My Tool does one thing, and one thing well."""
    greet = 'Howdy' if as_cowboy else 'Hello'
    click.echo('{0}, {1}.'.format(greet, name))


@click.group()
def cli():
    click.echo('You have got flash like super powers.')


@cli.command()
@click.option('--source', '-s', default='/home/chillaranand/Downloads/',
              help='Enter source location.')
@click.option('--destination', '-d', default='/home/chillaranand/Documents/',
              help='Enter source location.')
@click.option('--kindle', '-k', default='anand21nanda@kindle.com',
              help='Your kindle mail.')
def send_to_kindle(source, destination, kindle):
    print(source, destination)
    click.echo('Sending books to your kindle device.')

    patterns = ['*.epub', '*.pdf']
    for pattern in patterns:
        files = get_files_with_pattern(pattern, source)
        for filename in files:
            convert_to_mobi(filename)
            shutil.move(filename, destination)

    patterns = ['*.azw3', '*.mobi']
    for pattern in patterns:
        files = get_files_with_pattern(pattern, source)
        for filename in files:
            send_to_kindle_mail(filename, kindle)
            shutil.move(filename, destination)


@cli.command()
def im_fixup():
    click.echo('Fixing imports in python project')
    project_root = os.getcwd()
    imp_mgc_fixup(project_root)
