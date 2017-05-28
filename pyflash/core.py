import ast
import copy
import datetime as dt
import logging
import math
import calendar
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import multiprocessing
import operator
from os.path import abspath, dirname, expanduser, join

import babelfish
import importmagic
import PyPDF2
import pypandoc
import requests
from dateutil import rrule
from prettytable import PrettyTable
try:
    from isign import isign
except:
    isign = None
from subliminal import download_best_subtitles, region, save_subtitles, scan_videos

from .utils import get_active_hosts, get_ip, ping, run_shell_command, ebook_meta_data, matched_files, \
    convert_books, get_cache_file, file_list, relocate_file, checksum, execute_shell_command, \
    get_title, movie_info


FNULL = open(os.devnull, 'w')

formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(sh)

logger = logging.getLogger(__name__)


def organize_books(directory=None):
    if not directory:
        directory = os.getcwd()
    logger.info('Organizing books in {}'.format(directory))

    patterns = ['*.epub', '*.mobi', '*.pdf']
    files = matched_files(patterns, directory)
    for file_name in files:
        logger.info(file_name)
        meta_data = ebook_meta_data(file_name)
        title = meta_data.get('Title', '')
        if not title or title == 'Unknown':
            continue
        title = title.replace(" ", "_").lower()
        ext = file_name.split('.')[-1]
        dir_name = dirname(file_name)
        new_file_name = join(dir_name, '{}.{}'.format(title, ext))
        if new_file_name == file_name:
            continue
        shutil.move(file_name, os.path.join(directory, new_file_name))
        logger.info('Rearranged {} -> {}'.format(file_name, new_file_name))


def send_to_kindle(source, destination):
    logger.info('Search for books in {}'.format(source))
    source = expanduser(source)
    destination = expanduser(destination)
    convert_books(source, '.epub', '.mobi')
    patterns = ['*.azw3', '*.mobi', '*.pdf']
    files = matched_files(patterns, source)
    for filename in files:
        logger.info('Syncing {}'.format(filename))
        try:
            shutil.move(filename, destination)
        except shutil.Error as e:
            logger.error(e)


def fix_imports(index, source):
    scope = importmagic.Scope.from_source(source)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    source = importmagic.update_imports(
        source, index, unresolved, unreferenced
    )
    return source


def imp_mgc_fixup(project_root):
    index = importmagic.SymbolIndex()
    try:
        with open('index.json') as fd:
            index = importmagic.SymbolIndex.deserialize(fd)
    except:
        index.build_index(sys.path)
        with open('index.json', 'w') as fd:
            index.serialize(fd)

    files = matched_files(['*.py'], root=project_root)
    for f in files:
        with open(f, 'w+') as fh:
            py_source = fh.read()
            py_source = fix_imports(index, py_source)
            fh.write(py_source)


def pyformat(project_root):
    cmd = "find . -name '*.py' | xargs autopep8 -i"
    subprocess.check_output(shlex.split(cmd), shell=True)


def download_imd_data(from_date, to_date, state):
    if not from_date:
        now = dt.datetime.now()
        from_date = now.strftime('%d%2f%m%2f%Y')
        delta = dt.timedelta(days=31)
        month = now + delta
        to_date = month.strftime('%d%2f%m%2f%Y')

    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    host = 'http://imdaws.com/'
    endpoint = 'userdetails.aspx?Dtype=AWS&State={}&Dist=0&Loc=0&FromDate={}&ToDate={}&Time='

    username = os.environ.get('IMD_USERNAME')
    password = os.environ.get('IMD_PASSWORD')
    if not (username and password):
        logger.error('Please set IMD_USERNAME, IMD_PASSWORD env variables.')
        sys.exit()

    data = {
        'txtUserName': username,
        'txtPassword': password,
        'btnSave': 'Download',
    }
    states = range(1, 29)

    for state in states:
        ep = endpoint.format(state, from_date, to_date)
        url = host + ep

        resp = requests.post(url, data=data)
        if resp.status_code != 200:
            logger.error(url)
            continue

        data = resp.content.decode('utf-8')

        d_url = data.split("DownloadData('")[1].split("'")[0]
        r = requests.get(d_url)
        name = str(state) + '.csv'
        file_name = join(data_dir, name)
        with open(file_name, 'wb') as fh:
            fh.write(r.content)


def get_imports(tree):
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        if isinstance(node, ast.ImportFrom):
            for name in node.names:
                imports.append('{}.{}'.format(node.module, name.name))

    return imports


def organize_photos(directory=None):
    if not directory:
        directory = os.getcwd()
    logger.info('Organizing photos in {}'.format(directory))
    cmd = "exiftool -r '-FileName<CreateDate' -d '%Y-%m-%d_%H_%M_%S%%-c.%%le' {}".format(directory)
    run_shell_command(cmd)


def ocropus(file_name, language, output_dir):
    if not output_dir:
        output_dir = os.getcwd()
    py = 'python2'

    file_name = os.path.abspath(file_name)

    cmd = '{} ocropus-nlbin {} -o {} -n '.format(py, file_name, output_dir)
    run_shell_command(cmd)
    cmd = '{} ocropus-gpageseg {}/????.bin.png -n '.format(py, output_dir)
    run_shell_command(cmd)
    model = 'models/{}.pyrnn.gz'.format(language)
    cmd = '{} ocropus-rpred -Q 4 -m {} {}/????.bin.png -n'.format(py, model, output_dir)
    run_shell_command(cmd)


engines = {'ocropus': ocropus}


def ocr(engine, file_name, language, output_dir):
    engine = engines[engine]
    engine(file_name, language, output_dir)


def split_pdf(src, dst=None):
    if not src:
        print('Enter file to convert')
        sys.exit(0)
    if not dst:
        dst = src

    in_file = PyPDF2.PdfFileReader(src)
    out_file = PyPDF2.PdfFileWriter()

    for i in range(in_file.getNumPages()):
        p = in_file.getPage(i)
        q = copy.copy(p)
        q.mediaBox = copy.copy(p.mediaBox)

        x1, x2 = p.mediaBox.lowerLeft
        x3, x4 = p.mediaBox.upperRight

        x1, x2 = math.floor(x1), math.floor(x2)
        x3, x4 = math.floor(x3), math.floor(x4)
        x5, x6 = math.floor(x3/2), math.floor(x4/2)

        if x3 > x4:
            # horizontal
            p.mediaBox.upperRight = (x5, x4)
            p.mediaBox.lowerLeft = (x1, x2)

            q.mediaBox.upperRight = (x3, x4)
            q.mediaBox.lowerLeft = (x5, x2)
        else:
            # vertical
            p.mediaBox.upperRight = (x3, x4)
            p.mediaBox.lowerLeft = (x1, x6)

            q.mediaBox.upperRight = (x3, x6)
            q.mediaBox.lowerLeft = (x1, x2)

        out_file.addPage(p)
        out_file.addPage(q)

    with open(dst, 'wb') as fh:
        out_file.write(fh)


def download_book():
    pass


def organize_downloads(directory):
    if not directory:
        directory = os.getcwd()
    for filename in file_list(directory):
        relocate_file(filename)


def _fix_pep8(project_root):
    logger = logging.getLogger(__name__)
    logger.info('Fixing PEP8 issues')
    cmd = 'autopep8 --recursive --in-place {}'.format(project_root)
    run_shell_command(cmd)


def importmagic_fixup(index, code):
    scope = importmagic.Scope.from_source(code)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    code = importmagic.update_imports(code, index, unresolved, unreferenced)
    return code


def _fix_imports(project_root):
    index = importmagic.SymbolIndex()
    name = project_root.split('/')[-1]
    index.get_or_create_index(name=name, paths=[project_root] + sys.path)
    importmagic.Imports(index=index, source=None, root_dir=project_root)

    files = matched_files(['*.py'], project_root)
    for filename in files:
        with open(filename, 'r') as fh:
            code = fh.read()
        if not code:
            continue
        code = importmagic_fixup(index, code)
        with open(filename, 'w') as fh:
            fh.write(code)


def fix_build(directory):
    if not directory:
        directory = os.getcwd()
    _fix_pep8(directory)
    _fix_imports(directory)


def download_subtitles(directory):
    if not directory:
        directory = os.getcwd()
    logger.info('Downloading subtitles for videos in {}'.format(directory))
    backend = 'dogpile.cache.dbm'
    cache_file = get_cache_file('subliminal.cache')
    region.configure(backend, arguments={'filename': cache_file})
    videos = scan_videos(directory)
    subtitles = download_best_subtitles(videos, {babelfish.Language('eng')})
    for video in videos:
        save_subtitles(video, subtitles[video], single=True)


def adb_connect(interface):
    if not interface:
        interface = 'wlo1'
    logger.info('Scanning "{interface}" for open ports...')
    ip = get_ip(interface)
    network = '.'.join(ip.split('.')[:-1] + ['0']) + '/24'
    hosts = get_active_hosts(network)
    for host in hosts():
        up = ping(host, port=5555)
        if up:
            out = run_shell_command('adb connect {}'.format(host))
            print(out)


def rent_receipts(name, amount, owner_name, address, year):
    RENT_RECEIPT = """  # noqa

### RENT RECEIPT - {} {}

&nbsp;

Received sum of **Rs. {}** from **{}** towards the rent of property located at **{}** for the period from **{}** to **{}**.


&nbsp;

&nbsp;

**{}**

{}
"""
    start_date = dt.date(year, 4, 1)

    for date in rrule.rrule(freq=rrule.MONTHLY, count=12, dtstart=start_date):
        month = date.strftime('%B')
        month_start = date.strftime('%d %B %Y')
        _, month_days = calendar.monthrange(int(date.strftime('%Y')), int(date.strftime('%m')))
        month_end = date + dt.timedelta(days=month_days - 1)
        month_end = month_end.strftime('%d %B %Y')
        md = RENT_RECEIPT.format(
            month, year, amount, name, address, month_start, month_end, owner_name, month_end,
        )
        pdf_file = 'rent_receipt_{}.pdf'.format(date.strftime('%Y_%m'))
        print('Generating {}'.format(pdf_file))
        _, tmp_file = tempfile.mkstemp()
        with open(tmp_file, 'w') as fh:
            fh.write(md)
        pypandoc.convert_file(tmp_file, format='md', to='pdf', outputfile=pdf_file)
        os.remove(tmp_file)


def ipa_install(ipa):
    ipa = abspath(ipa)
    logger.info('Resigning ipa: {}'.format(ipa))
    isign.resign(ipa, output_path=ipa)
    cmd = 'ideviceinstaller -i {}'.format(ipa)
    run_shell_command(cmd)


def rate_movies(directory, sort):
    if not directory:
        directory = os.getcwd()
    logger.info('Fecting ratings for videos in {}'.format(directory))
    columns = ['TITLE', 'YEAR', 'GENRE', 'IMDB', 'RT', 'MC']
    table = PrettyTable(columns)
    for file in file_list(directory):
        title = get_title(file)
        if not title:
            continue
        data = movie_info(title)
        if not data:
            continue
        r = data['Ratings']
        table.add_row((
            data['Title'], data['Year'], data['Genre'], r[0]['Value'], r[1]['Value'], r[2]['Value'],
        ))
    if not sort:
        sort = 'TITLE'
    sort = sort.upper()
    sort_key = columns.index(sort.upper()) + 1
    print(table.get_string(sort_key=operator.itemgetter(sort_key, 0), sortby=sort))


def validate_aadhaar(number):
    if not number or len(number) != 12:
        print('Enter 12 digit AADHAR numner')
        sys.exit()

    chksum, aadhaar = number[0], number[1:]
    if str(checksum(aadhaar)) == chksum:
        print('Valid AADHAR number')
    else:
        print('Invalid AADHAR number')
    print(chksum, aadhaar, number, checksum(aadhaar))


def procfile(file):
    data = open(file).readlines()
    commands = [i.split(':')[-1].strip() for i in data]
    try:
        with multiprocessing.Pool(len(commands)) as pool:
            pool.map(execute_shell_command, commands)
    except KeyboardInterrupt:
        pool.close()
        pool.terminate()
        run_shell_command('pkill -f celery')
