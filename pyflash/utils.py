import glob
import os
import smtplib
import subprocess
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename

import importmagic
from importmagic import SymbolIndex


FNULL = open(os.devnull, 'w')


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
    source = importmagic.update_imports(source, index, unresolved, unreferenced)
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
            py_source = fix_imports(index, py_source)
            fh.write(py_source)
