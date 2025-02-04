import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import toml

from gen.log import get_logger

MAX_DEPTH = 5
GA_TRACKING_ID = 'G-YNLYYEX7MN'
INDEX_MOD = 'index'

log = get_logger(__name__)


def collect_files(root_path: str, predicate: Callable[[str, list[str], list[str]], bool], max_depth=MAX_DEPTH) -> list[
    str]:
    book_dirs = []
    for current_dir, subdirs, files in os.walk(root_path):
        relative_path = os.path.relpath(current_dir, root_path)
        current_depth = 0 if relative_path == '.' else relative_path.count(os.sep) + 1

        if current_depth > max_depth:
            subdirs.clear()
            continue

        if predicate(current_dir, subdirs, files):
            log.info(f'Found book in {current_dir}')
            book_dirs.append(current_dir)
    return book_dirs


def collect_books(root_path: str) -> list[str]:
    return collect_files(root_path, lambda current_dir, subdirs, files: 'book.toml' in files)


@dataclass
class BookConfig:
    site_url: str
    build_dir: str
    title: str
    description: str
    dir: str


def load_book_config(book_dir: str) -> BookConfig:
    dirname = os.path.basename(book_dir)
    raw_config = toml.load(os.path.join(book_dir, 'book.toml'))

    book_config = raw_config.get('book', {})
    build_config = raw_config.get('build', {})
    html_config = raw_config.get('output', {}).get('html', {})
    site_url = html_config.get('site-url', dirname)

    if site_url.startswith('/'):
        site_url = site_url[1:]

    config = BookConfig(
        site_url=site_url,
        build_dir=build_config.get('build-dir', 'book'),
        title=book_config.get('title', None),
        description=book_config.get('description', None),
        dir=book_dir
    )
    return config


def build_book(config: BookConfig):
    subprocess.run(
        ['mdbook', 'build'],
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
        check=True,
        cwd=config.dir
    )


def is_subdir(path: str | Path, parent: str | Path) -> bool:
    # Convert to Path objects and resolve to absolute paths
    path = Path(path).resolve()
    parent = Path(parent).resolve()

    try:
        # Use relative_to to check if path starts with parent
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def add_ga_tracking(book_dir: str):
    config_path = os.path.join(book_dir, 'book.toml')
    raw_config = toml.load(config_path)
    if 'output' not in raw_config:
        raw_config['output'] = {}
    if 'html' not in raw_config['output']:
        raw_config['output']['html'] = {}
    raw_config['output']['html']['google-analytics'] = GA_TRACKING_ID
    with open(config_path, 'w') as f:
        toml.dump(raw_config, f)


def run(root_dir: str):
    submodules = os.listdir(os.path.join(root_dir, 'submodules'))

    # Put the index module first since it outputs to the public directory, which will be deleted
    # by the book processor
    index_module_idx = submodules.index(INDEX_MOD)
    submodules[0], submodules[index_module_idx] = submodules[index_module_idx], submodules[0]

    mods_by_book = []

    for mod in submodules:
        book_dirs = collect_books(os.path.join(root_dir, 'submodules', mod))
        configs = []
        for book_dir in book_dirs:
            add_ga_tracking(book_dir)
            configs.append(load_book_config(book_dir))
        mods_by_book.append((mod, configs))

    # Generate the README.md file for the index module
    with open(os.path.join(root_dir, 'submodules', 'index', 'src', 'README.md'), 'a') as f:
        for mod, configs in mods_by_book:
            if mod == INDEX_MOD:
                continue
            f.write(f'## `ethereum-optimism/{mod}`\n\n')
            for config in configs:
                config = load_book_config(config.dir)
                f.write(f'- [{config.title}](https://devdocs.optimism.io/{config.site_url.replace('/', '')})\n')
            f.write('\n')

    for mod, configs in mods_by_book:
        log.info(f'Processing submodule {mod}')

        for config in configs:
            log.info(f'Building book {config.title}')
            build_book(config)

            if mod == INDEX_MOD:
                outdir = os.path.join(root_dir, 'public')
            else:
                outdir = os.path.join(root_dir, 'public', config.site_url)

            log.info(f'Moving book {config.title} to public dir {outdir}')

            if not is_subdir(outdir, root_dir):
                raise ValueError(f'Output directory {outdir} is not a subdirectory of root dir {root_dir}!')
            if os.path.exists(outdir):
                log.info(f'Removing existing build dir {outdir}')
                shutil.rmtree(outdir)
            os.mkdir(outdir)

            os.rename(
                os.path.join(config.dir, config.build_dir),
                outdir
            )
