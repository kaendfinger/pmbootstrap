"""
Copyright 2017 Oliver Smith

This file is part of pmbootstrap.

pmbootstrap is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pmbootstrap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pmbootstrap.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
This file tests all functions from pmb.build._package.
"""

import glob
import os
import pytest
import sys

# Import from parent directory
sys.path.append(os.path.realpath(
    os.path.join(os.path.dirname(__file__) + "/..")))
import pmb.build
import pmb.helpers.logging


@pytest.fixture
def args(tmpdir, request):
    import pmb.parse
    sys.argv = ["pmbootstrap", "--mirror-pmOS=", "init"]
    args = pmb.parse.arguments()
    args.log = args.work + "/log_testsuite.txt"
    pmb.helpers.logging.init(args)
    request.addfinalizer(args.logfd.close)
    return args


def test_buildroot_aarch64_init(args):
    # Remove aarch64 chroot
    pmb.chroot.shutdown(args)
    path = args.work + "/chroot_buildroot_aarch64"
    if os.path.exists(path):
        pmb.helpers.run.root(args, ["rm", "-rf", path])

    # Remove existing workaround packages
    pattern_workaround_apk = (args.work + "/packages/aarch64/"
                              "abuild-aarch64-qemu-workaround-*")
    for match in glob.glob(pattern_workaround_apk):
        pmb.helpers.run.root(args, ["rm", match])
    pmb.build.index_repo(args, "aarch64")

    # Build hello-world for aarch64, causing the chroot to initialize properly
    pmb.build.package(args, "hello-world", "aarch64", force=True)

    # Verify that the workaround was built and installed
    assert len(glob.glob(pattern_workaround_apk))
    assert os.path.exists(args.work + "/chroot_buildroot_aarch64/usr/bin"
                          "/abuild-tar-patched")
