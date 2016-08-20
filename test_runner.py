#!/usr/bin/env python

import argparse
import sys
import os

import pytest

SDK_PATH = '/usr/local/google_appengine'

def main(functional, sdk_path=SDK_PATH):
    sys.path.insert(0, sdk_path)

    import dev_appserver
    dev_appserver.fix_sys_path()

    if functional:
        pytest.main(['-x', 'functional_tests'])
    else:
        pytest.main(['-x', 'tests'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run blog app tests.')
    parser.add_argument('--functional', action='store_true')
    parser.add_argument('--sdk_path')
    args = parser.parse_args()

    if args.sdk_path:
        main(args.functional, args.sdk_path)
    else:
        main(args.functional)
