import os
from library import localstore as store


def test_create_dirs():
    created_dir = store.create_dirs("test_dir")
    assert created_dir.exists() and created_dir.is_dir()
    #os.rmdir(created_dir)
    created_dir = store.create_dirs("test_dir/subdir1/subdir2")
    assert created_dir.exists() and created_dir.is_dir()
    #os.rmdir(created_dir)
