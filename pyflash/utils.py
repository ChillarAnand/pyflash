import datetime
import glob
import os
import shutil
import smtplib
import subprocess
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename

import requests

import importmagic
from email.utils import COMMASPACE, formatdate
from importmagic import SymbolIndex


FNULL = open(os.devnull, 'w')


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
            # send_to_kindle_mail(filename, kindle)
            print('Sending {}'.format(filename))
            try:
                shutil.move(filename, destination)
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
            # print('ssssssssss')
            # time.sleep(random.randint(15, 20))
