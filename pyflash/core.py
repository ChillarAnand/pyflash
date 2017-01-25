import ast
import datetime
import glob
import os
import smtplib
import shlex
import shutil
import subprocess
import sys
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename

import requests
import importmagic
from importmagic import SymbolIndex
import math
from PyPDF2 import PdfFileReader, PdfFileWriter

from .utils import cd


FNULL = open(os.devnull, 'w')


def envar(var):
    var = var.upper()
    var = os.environ.get(var, None)
    if not var:
        print('{} not set in environment'.var.upper())
    return var


def run_shell_command(cmd):
    cmd = shlex.split(cmd)
    print(cmd)
    out = subprocess.check_output(cmd)
    return out.decode('utf-8')


def get_info(filename):
    cmd = 'ebook-meta {}'.format(filename)
    out = run_shell_command(cmd)
    title = out.split('\n')[0].split('    : ')[-1]
    authors = out.split('\n')[1].split('    : ')[-1]
    return title


def sort_books(directory=None):
    for file_name in os.listdir(directory):
        print(os.path.abspath(file_name))


def to_kindle(source, destination):
    patterns = ['*.epub']
    for pattern in patterns:
        files = get_files_with_pattern(pattern, source)
        for filename in files:
            convert_to_mobi(filename)
            shutil.move(filename, "/tmp/")

    patterns = ['*.azw3', '*.mobi', '*.pdf']
    for pattern in patterns:
        files = get_files_with_pattern(pattern, source)
        for filename in files:
            print('Sending {}'.format(n_filename))
            try:
                shutil.move(n_filename, destination)
            except shutil.Error as e:
                print(e)


def get_files_with_pattern(pattern, root):
    path = os.path.join(root, '**', pattern)
    for filename in glob.iglob(path, recursive=True):
        yield filename


def convert_to_mobi(filename):
    file_path, ext = os.path.splitext(filename)
    mobi_file = file_path + '.mobi'
    command = ['ebook-convert', filename, mobi_file]
    print(' '.join(command))
    subprocess.check_output(command)


def send_to_kindle_mail(filename, kindle):
    send_mail(
        'anand21nanda@gmail.com',
        ['anand21nanda@kindle.com'],
        'Kindle book: {}'.format(filename),
        'Kindle book: {}'.format(filename),
        files=[filename]
    )


def send_mail(m_from, m_to, subject, text,
              files=None, server='smtp.gmail.com'):
    msg = MIMEMultipart()
    msg['From'] = m_from
    msg['To'] = COMMASPACE.join(m_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files:
        with open(f, "rb") as fh:
            part = MIMEApplication(
                fh.read(),
                Name=basename(f)
            )
            part['Content-Disposition'] = 'attachment; filename={}'.format(
                basename(f)
            )
            msg.attach(part)

    server = smtplib.SMTP_SSL(server, 465)
    server.ehlo()
    g_user = os.environ.get('GMAIL_USERNAME')
    g_pass = os.environ.get('GMAIL_PASSWORD')
    if not (g_user and g_pass):
        print('Please set GMAIL_USERNAME, GMAIL_PASSWORD env variables.')
        sys.exit()
    server.login(g_user, g_pass)
    server.sendmail(m_from, m_to, msg.as_string())
    server.close()
    print('Email sent!')


# send_mail('a@a.com', 'anand21nanda@gmail.com', 'f', 'f')


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
        print('loading index')
        with open('index.json') as fd:
            index = SymbolIndex.deserialize(fd)
    except:
        print('building index')
        index.build_index(sys.path)
        with open('index.json', 'w') as fd:
            index.serialize(fd)

    files = get_files_with_pattern('*.py', root=project_root)
    for f in files:
        with open(f, 'w+') as fh:
            py_source = fh.read()
            print(py_source)
            py_source = fix_imports(index, py_source)
            print(py_source)
            fh.write(py_source)


def pyformat(project_root):
    cmd = "find . -name '*.py' | xargs autopep8 -i"
    subprocess.check_output(shlex.split(cmd), shell=True)


def imd_data(from_date, to_date, state):
    """
    Download data from IMD for given period.
    """
    if not from_date:
        now = datetime.datetime.now()
        from_date = now.strftime('%d%2f%m%2f%Y')
        delta = datetime.timedelta(days=31)
        month = now + delta
        to_date = month.strftime('%d%2f%m%2f%Y')

    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    base_url = 'http://imdaws.com/'
    endpoint = 'userdetails.aspx?Dtype={}&State={}&Dist=0&Loc=0&FromDate={}&ToDate={}&Time='

    username = os.environ.get('IMD_USERNAME')
    password = os.environ.get('IMD_PASSWORD')
    if not (username and password):
        print('Please set IMD_USERNAME, IMD_PASSWORD env variables.')
        sys.exit()

    data = {
        'txtUserName': username,
        'txtPassword': password,
        'btnSave': 'Download',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': '/wEPDwUKMTY1MTEwNzczMw9kFgICBA9kFgICAQ8PFgIeBFRleHQFBjg0NDk1M2RkZC6DYVzVd15uvyThvNG6/M2DvFM9',
        '__EVENTVALIDATION': '/wEWBQKWseTfCwKl1bKzCQK1qbSRCwKct7iSDAK+rvNOIfrKsC5vyGsh5LvcfjWT2CXjvbA=',
    }

    d_types = ['AWS', 'ARG']
    d_types = ['AWS']

    states = range(1, 29)

    for d_type in d_types:
        for s in states:
            ep = endpoint.format(d_type, s, from_date, to_date)
            url = base_url + ep
            print(url)

            resp = requests.post(url, data=data)
            if not resp.status_code == 200:
                print('error', url)
                continue

            data = resp.content.decode('utf-8')

            try:
                # capture url
                d_url = data.split("DownloadData('")[1].split("'")[0]
            except:
                # import ipdb; ipdb.set_trace()
                # print(data)
                print('error', url)
                continue

            r = requests.get(d_url)
            name = '_'.join((d_type, str(state))) + '.csv'
            file_name = os.path.join(data_dir, name)
            with open(file_name, 'wb') as fh:
                fh.write(r.content)


def ak_dynamic_scan(num, debug):
    if debug:
        base_url = 'http://0.0.0.0:8000/'
    else:
        base_url = 'https://api.appknox.com/'
    url = base_url + 'api/token/new.json'
    print(url)
    data = {
        'username': os.environ.get('AK_USER'),
        'password': os.environ.get('AK_PASS')
    }
    response = requests.post(url, data=data)

    try:
        data = response.json()
        token = data['token']
        user_id = data['user']
    except:
        print(response.text)
        return

    url = base_url + 'api/dynamic_shutdown/{}'.format(num)
    print(url)
    response = requests.post(url, data=data, auth=(user_id, token))
    time.sleep(4)
    url = base_url + 'api/dynamic/{}'.format(num)
    print(url)
    response = requests.post(url, data=data, auth=(user_id, token))
    print(response.text)


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


def mopy(cwd=None):
    if cwd:
        for fn in glob.glob('**/*.py', recursive=True):
            print(fn)

            try:
                tree = ast.parse(open(fn).read())
            except:
                continue
            imports = get_imports(tree)
            print(imports)
            # pass


def organize_photos():
    src_dir = '~/Dropbox/Camera\ Uploads'
    tgt_dir = '~/Pictures'
    bkp_dir = '~/Dropbox/photos'
    cmd = 'mv {}/* {}'.format(src_dir, tgt_dir)


def ocropus(file_name, language, output_dir):
    if not output_dir:
        output_dir = os.getcwd()
    ocropy = '/home/chillaranand/projects/python/ocr/ocropy'
    py = 'python2'

    file_name = os.path.abspath(file_name)

    with cd(ocropy):
        cmd = '{} ocropus-nlbin {} -o {} -n '.format(
            py, file_name, output_dir)
        print(cmd)
        subprocess.call(cmd.split())

        cmd = '{} ocropus-gpageseg {}/????.bin.png -n '.format(
            py, output_dir)
        print(cmd)
        subprocess.call(cmd.split())

        model = 'models/{}.pyrnn.gz'.format(language)
        cmd = '{} ocropus-rpred -Q 4 -m {} {}/????.bin.png -n'.format(
            py, model, output_dir)
        print(cmd)
        subprocess.call(cmd.split())

    print(file_name, output_dir, language)


engines = {'ocropus': ocropus}


def ocr(engine, file_name, language, output_dir):
    engine = ocropus
    engine(file_name, language, output_dir)


def split_pdf(src, dst):
    if not dst:
        dst = src

    in_file = PdfFileReader(src)
    out_file = PdfFileWriter()

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
