import ast
import copy
import configparser
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

import pyotp


try:
    import babelfish
    import importmagic
    import PyPDF2
    import pypandoc
    import requests
    from dateutil import rrule
    from prettytable import PrettyTable
    from subliminal import download_best_subtitles, region, save_subtitles, scan_videos
    from isign import isign
except:
    isign = None


from . import utils as u
from . import utils


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
    files = u.matched_files(patterns, directory)
    for file_name in files:
        # logger.info(file_name)
        try:
            meta_data = u.ebook_meta_data(file_name)
        except Exception as e:
            logger.error(e)
            continue
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
    u.convert_books(source, '.epub', '.mobi')
    patterns = ['*.azw3', '*.mobi', '*.pdf']
    files = u.matched_files(patterns, source)
    for filename in files:
        logger.info('Syncing {}'.format(filename))
        try:
            shutil.move(filename, destination)
        except shutil.Error as e:
            logger.error(e)


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
    u.run_shell_command(cmd)


def ocropus(file_name, language, output_dir):
    file_name = os.path.abspath(file_name)
    if not output_dir:
        output_dir = os.getcwd()

    py = 'python2'
    ocropus_root = '/home/chillaranand/projects/ocr/ocropy'
    model = '{}/models/{}.pyrnn.gz'.format(ocropus_root, language)

    cmd = '{} {}/ocropus-nlbin {} -o {} -n '.format(py, ocropus_root, file_name, output_dir)
    u.run_shell_command(cmd)
    cmd = '{} {}/ocropus-gpageseg {}/????.bin.png -n '.format(py, ocropus_root, output_dir)
    u.run_shell_command(cmd)
    cmd = '{} {}/ocropus-rpred -Q 4 -m {} {}/????.bin.png -n'.format(py, ocropus_root, model, output_dir)
    u.run_shell_command(cmd)


def ocr(engine, file_name, language, output_dir):
    engines = {'ocropus': ocropus}
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
    for filename in u.file_list(directory):
        u.relocate_file(filename)


def pyformat(project_root):
    cmd = "find . -name '*.py' | xargs autopep8 -i"
    subprocess.check_output(shlex.split(cmd), shell=True)


def _fix_pep8(project_root):
    logger = logging.getLogger(__name__)
    logger.info('Fixing PEP8 issues')
    cmd = 'autopep8 --recursive --in-place {}'.format(project_root)
    u.run_shell_command(cmd)


def fix_imports_in_code(index, source):
    scope = importmagic.Scope.from_source(source)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    # start_line, end_line, import_block = importmagic.get_update(source, index, unresolved, unreferenced)
    source = importmagic.update_imports(
        source, index, unresolved, unreferenced
    )
    return source


def fix_imports(project_root):
    if not project_root:
        project_root = os.getcwd()
    index = importmagic.SymbolIndex()
    try:
        with open('.index.json') as fd:
            index = importmagic.SymbolIndex.deserialize(fd)
        print('Index loaded')
    except:
        print('Building index...')
        index.build_index(sys.path + [project_root])
        with open('.index.json', 'w') as fd:
            index.serialize(fd)

    # files = u.matched_files(['*.py'], root_dir=project_root)
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if not file.endswith('.py'):
                continue
            with open(file) as fh:
                py_source = fh.read()
            py_source = fix_imports_in_code(index, py_source)

            with open(file, 'w') as fh:
                fh.write(py_source)


def fix_build(directory):
    if not directory:
        directory = os.getcwd()
    _fix_pep8(directory)
    fix_imports(directory)


def download_subtitles(directory):
    if not directory:
        directory = os.getcwd()
    logger.info('Downloading subtitles for videos in {}'.format(directory))

    for dir_name, subdir, files in os.walk(directory):
        print(dir_name, subdir)
        for fname in files:
            print(fname)
    # return

    backend = 'dogpile.cache.dbm'
    cache_file = u.get_cache_file('subliminal.cache')
    region.configure(backend, arguments={'filename': cache_file})
    videos = scan_videos(directory)
    subtitles = download_best_subtitles(videos, {babelfish.Language('eng')})
    for video in videos:
        save_subtitles(video, subtitles[video], single=True)


def adb_connect(interface):
    if not interface:
        interface = 'wlo1'
    logger.info('Scanning "{interface}" for open ports...')
    ip = u.get_ip(interface)
    network = '.'.join(ip.split('.')[:-1] + ['0']) + '/24'
    hosts = u.get_active_hosts(network)
    print(hosts)
    for host in hosts():
        up = u.ping(host, port=5555)
        if up:
            out = u.run_shell_command('adb connect {}'.format(host))
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
    u.run_shell_command(cmd)


def rate_movies(directory, sort):
    if not directory:
        directory = os.getcwd()
    logger.info('Fecting ratings for videos in {}'.format(directory))
    columns = ['TITLE', 'YEAR', 'GENRE', 'IMDB', 'RT', 'MC']
    table = PrettyTable(columns)
    for file in u.file_list(directory):
        title = u.get_title(file)
        if not title:
            continue
        data = u.movie_info(title)
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
    if str(u.checksum(aadhaar)) == chksum:
        print('Valid AADHAR number')
    else:
        print('Invalid AADHAR number')
    print(chksum, aadhaar, number, u.checksum(aadhaar))


def procfile(file):
    data = open(file).readlines()
    commands = [i.split(':', 1)[-1].strip() for i in data]
    try:
        with multiprocessing.Pool(len(commands)) as pool:
            pool.map(u.execute_shell_command, commands)
    except KeyboardInterrupt:
        pool.close()
        pool.terminate()
        u.run_shell_command('pkill -f celery')


def otp():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.pyflash.ini'))
    for item in config['otp']:
        secret = config['otp'][item]
        try:
            otp = pyotp.TOTP(secret).now()
        except:
            continue
        row = '{}: {}'.format(item, otp)
        print(row)


def pg_stats(uri, column, duration):
    print(uri, column, duration)
    pg_stats = utils.PGStats(uri=uri)
    report = pg_stats.db_stats(column=column, duration=duration, include_emtpy=False)
    for k, v in report.items():
        print(k, v)
