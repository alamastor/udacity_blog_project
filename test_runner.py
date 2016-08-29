#!/usr/bin/env python

import argparse
import sys
import os

import pytest

SDK_PATH = '/usr/local/google_appengine'

def main(functional, sdk_path=SDK_PATH, files=[]):
    sys.path.insert(0, sdk_path)

    import dev_appserver
    dev_appserver.fix_sys_path()

    if files:
        for file_ in files:
            pytest.main(['-x', file_])
    elif functional:
        pytest.main(['functional_tests'])
    else:
        pytest.main(['tests'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run blog app tests.')
    parser.add_argument('files', type=str, nargs='*')
    parser.add_argument('--functional', action='store_true', help='Run functional tests.')
    parser.add_argument('--sdk_path')
    args = parser.parse_args()

    if args.sdk_path:
        main(args.functional, args.sdk_path, files=args.files)
    else:
        main(args.functional, files=args.files)
