import glob
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import click

from . import core


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


@cli.command()
@click.option('--python', '-p')
@click.option('--number', '-n', default=100)
def python_version_readiness(python, number):
    """
    Show version readiness of top python packages.
    """
    core.python_version_readiness(python, number)


BENCH_CLOUD_DIR = Path.home() / 'Cloud' / 'tech' / 'llm'
BENCH_SUITES = ('coding', 'reasoning', 'factual')
BENCH_LOCAL_URL = 'http://localhost:8004/v1'
BENCH_MODELS = {
    'qwen3.6-35b-4bit': (BENCH_LOCAL_URL, 'k', 'mlx-community/Qwen3.6-35B-A3B-4bit'),
    'qwen3.6-27b-4bit': (BENCH_LOCAL_URL, 'k', 'mlx-community/qwen3.6-27b-4bit'),
    'haiku':   ('https://api.anthropic.com/v1', None, 'claude-haiku-4-5-20251001'),
    'sonnet':  ('https://api.anthropic.com/v1', None, 'claude-sonnet-4-6'),
    'sonnet5': ('https://api.anthropic.com/v1', None, 'claude-sonnet-5'),
}


def _model_label(hf_id):
    """Derive a filesystem-safe label from a HuggingFace model ID."""
    return re.sub(r'[^a-zA-Z0-9]+', '_', hf_id).strip('_').lower()


def _local_server_model():
    """Return the model ID currently served at BENCH_LOCAL_URL, or None."""
    import urllib.request, json as _json
    try:
        with urllib.request.urlopen(f'{BENCH_LOCAL_URL}/models', timeout=3) as r:
            data = _json.loads(r.read())
        models = data.get('data', [])
        return models[0]['id'] if models else None
    except Exception:
        return None


def _start_rapid_mlx(hf_id):
    """Start rapid-mlx serving hf_id on port 8004. Returns the Popen handle."""
    click.echo(f'Starting rapid-mlx serve {hf_id} on port 8004 ...')
    proc = subprocess.Popen(
        ['rapid-mlx', 'serve', hf_id, '--port', '8004'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Wait up to 120s for the server to be ready
    import time, urllib.request
    for _ in range(120):
        try:
            urllib.request.urlopen(f'{BENCH_LOCAL_URL}/models', timeout=2)
            click.echo('Server ready.')
            return proc
        except Exception:
            time.sleep(1)
    proc.terminate()
    raise RuntimeError(f'rapid-mlx failed to start within 120s for {hf_id}')


def _validate_anthropic_key():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not key:
        click.echo('ERROR: ANTHROPIC_API_KEY not set')
        return None
    import urllib.request, json as _json
    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=_json.dumps({'model': 'claude-haiku-4-5-20251001', 'max_tokens': 1,
                          'messages': [{'role': 'user', 'content': 'hi'}]}).encode(),
        headers={'x-api-key': key, 'anthropic-version': '2023-06-01',
                 'content-type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req) as r:
            body = _json.loads(r.read())
    except Exception:
        body = {}
    if body.get('type') == 'error':
        click.echo(f"ERROR: ANTHROPIC_API_KEY invalid — {body.get('error', {}).get('message', '?')}")
        return None
    return key


def _latest_file(label, suite, ext):
    """Return most recent file for label+suite regardless of date, or None."""
    matches = sorted(BENCH_CLOUD_DIR.glob(f'{label}_{suite}_*.{ext}'), reverse=True)
    return matches[0] if matches else None


def _run_bench_model(label, url, key, model, timestamp, no_cache):
    BENCH_CLOUD_DIR.mkdir(parents=True, exist_ok=True)
    click.echo(f'=== {label} ===')
    for suite in BENCH_SUITES:
        if not no_cache:
            existing = _latest_file(label, suite, 'json')
            if existing:
                click.echo(f'  suite: {suite} — skipped ({existing.name} exists)')
                continue
        outfile = BENCH_CLOUD_DIR / f'{label}_{suite}_{timestamp}.json'
        click.echo(f'  suite: {suite} — writing {outfile}')
        cmd = ['bench-my-llm', 'run', '--suite', suite, '-u', url, '-k', key,
               '--model', model, '-o', str(outfile)]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            click.echo(f'  suite: {suite} — FAILED')
        elif outfile.exists():
            click.echo(f'  suite: {suite} — saved')
        else:
            click.echo(f'  suite: {suite} — completed but file not written')


def _bench_reports(labels):
    click.echo('\n=== Reports ===')
    for label in labels:
        for suite in BENCH_SUITES:
            f = _latest_file(label, suite, 'json')
            if not f:
                continue
            txt = f.with_suffix('.txt')
            click.echo(f'--- {f.name} ---')
            if txt.exists():
                click.echo(f'  (cached: {txt.name})')
            else:
                result = subprocess.run(['bench-my-llm', 'report', str(f)], capture_output=True, text=True)
                output = result.stdout
                if output:
                    txt.write_text(output)
                    click.echo(output, nl=False)


def _bench_summary(labels=None):
    if labels is None:
        found = set()
        for f in BENCH_CLOUD_DIR.glob('*.txt'):
            parts = f.stem.split('_')
            if len(parts) >= 3:
                found.add('_'.join(parts[:-2]))
        labels = sorted(found) if found else list(BENCH_MODELS.keys())

    click.echo('\n=== Summary: Quality Score by Model & Suite ===')
    suite_w = max(12, max((len(s) for s in BENCH_SUITES), default=0) + 2)
    col = max(14, max((len(lb) for lb in labels), default=0) + 2)

    def sep(left, mid, right, fill='─'):
        return left + fill * (suite_w + 2) + mid + (mid + fill * (col + 2)).join([''] * (len(labels) + 1)).lstrip(mid) + right

    def row_line(suite_val, scores):
        cells = f'│ {suite_val:<{suite_w}} │'
        for s in scores:
            cells += f' {s:>{col}} │'
        return cells

    top    = '┌' + '─' * (suite_w + 2) + ('┬' + '─' * (col + 2)) * len(labels) + '┐'
    middle = '├' + '─' * (suite_w + 2) + ('┼' + '─' * (col + 2)) * len(labels) + '┤'
    bottom = '└' + '─' * (suite_w + 2) + ('┴' + '─' * (col + 2)) * len(labels) + '┘'

    click.echo(top)
    click.echo(row_line('Suite', labels))
    click.echo(middle)
    for suite in BENCH_SUITES:
        scores = []
        for lb in labels:
            txt = _latest_file(lb, suite, 'txt')
            score = '—'
            if txt:
                try:
                    for line in txt.read_text().splitlines():
                        m = re.search(r'Quality Score\s*\│\s*([\d.]+%)', line)
                        if m:
                            score = m.group(1)
                            break
                except FileNotFoundError:
                    pass
            scores.append(score)
        click.echo(row_line(suite, scores))
    click.echo(bottom)


def _resolve_models(specs):
    """
    Resolve a list of model specs (predefined labels or HF model IDs) into
    a list of (label, url, key, model_id, is_local) tuples.
    """
    resolved = []
    for spec in specs:
        if spec in BENCH_MODELS:
            url, key, model_id = BENCH_MODELS[spec]
            resolved.append((spec, url, key, model_id, key == 'k'))
        else:
            label = _model_label(spec)
            resolved.append((label, BENCH_LOCAL_URL, 'k', spec, True))
    return resolved


@cli.command(name='bench-my-llm')
@click.argument('models', nargs=-1, required=False)
@click.option('--all', 'run_all', is_flag=True, default=False, help='Run all predefined models.')
@click.option('--no-cache', is_flag=True, default=False,
              help='Ignore existing results and generate fresh benchmarks.')
def benchmyllm(models, run_all, no_cache):
    """
    Benchmark and compare LLMs across coding/reasoning/factual suites.

    MODELS: predefined labels (q36_35b, haiku, sonnet, sonnet5) or any
    HuggingFace model ID. Local/HF models are served via rapid-mlx on
    localhost:8004; one is loaded at a time. Existing results are reused
    unless --no-cache is passed.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if run_all:
        specs = list(BENCH_MODELS.keys())
    elif models:
        specs = list(models)
    else:
        click.echo('No models selected.')
        click.echo(f'Predefined: {", ".join(BENCH_MODELS.keys())}')
        click.echo('Or pass any HuggingFace model ID.')
        sys.exit(0)

    resolved = _resolve_models(specs)
    run_labels = []
    anthropic_key = None
    anthropic_validated = False

    for label, url, key, model_id, is_local in resolved:
        run_labels.append(label)
        rapid_proc = None
        try:
            if is_local:
                needs_server = no_cache or any(
                    _latest_file(label, suite, 'json') is None for suite in BENCH_SUITES
                )
                if needs_server:
                    current = _local_server_model()
                    if current == model_id:
                        click.echo(f'Already serving {model_id}.')
                    else:
                        rapid_proc = _start_rapid_mlx(model_id)
            else:
                if not anthropic_validated:
                    anthropic_key = _validate_anthropic_key()
                    anthropic_validated = True
                if not anthropic_key:
                    click.echo(f'Skipping {label} — Anthropic key invalid.')
                    run_labels.remove(label)
                    continue
                key = anthropic_key

            _run_bench_model(label, url, key, model_id, timestamp, no_cache)
        finally:
            if rapid_proc and rapid_proc.poll() is None:
                click.echo('Stopping rapid-mlx server.')
                rapid_proc.terminate()

    _bench_reports(run_labels)
    _bench_summary(labels=run_labels)
