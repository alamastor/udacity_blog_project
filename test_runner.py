#!/usr/bin/env python

import argparse
import sys
import os

import pytest

SDK_PATH = '/usr/local/google_appengine'


def main(functional, sdk_path=SDK_PATH, files=[], fail_fast=False):
    # Add App Engine SKD to Python path
    sys.path.insert(0, sdk_path)

    import dev_appserver
    dev_appserver.fix_sys_path()

    # Add blog dir to Python path.
    sys.path.append(os.getcwd() + '/blog')

    if files:
        for file_ in files:
            cmd = [file_]
    elif functional:
        cmd = ['functional_tests']
    else:
        cmd = ['tests']

    if fail_fast:
        cmd.append('-x')
    pytest.main(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run blog app tests.')
    parser.add_argument('files', type=str, nargs='*')
    parser.add_argument(
        '--functional', action='store_true', help='Run functional tests.'
    )
    parser.add_argument('--sdk_path')
    parser.add_argument(
        '-x',
        '--fail_fast',
        help="exit after first test fail",
        action='store_true'
    )
    args = parser.parse_args()

    if args.sdk_path:
        main(
            args.functional,
            args.sdk_path,
            files=args.files,
            fail_fast=args.fail_fast
        )
    else:
        main(args.functional, files=args.files, fail_fast=args.fail_fast)
