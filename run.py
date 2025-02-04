import os

from gen.log import get_logger

from gen import run

log = get_logger(__name__)


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    log.info(f'Starting book generation from {root_dir}')
    run(root_dir)


if __name__ == "__main__":
    main()
