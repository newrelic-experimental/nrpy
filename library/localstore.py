from pathlib import Path
import json
import os
import csv
import datetime
import library.nrpylogger as nrpy_logger
import library.utils as utils


logger = nrpy_logger.get_logger(os.path.basename(__file__))


def create_dirs(dir_path):
    logger.debug("Creating " + dir_path)
    if '/' in dir_path:
        dirs = dir_path.split('/')
        base_dir = Path(dirs[0])
        for i, sub_dir in enumerate(dirs):
            if i > 0:
                base_dir = base_dir / sub_dir
        storage_dir = base_dir
    else:
        storage_dir = Path(dir_path)
    storage_dir.mkdir(mode=0o777, parents=True, exist_ok=True)
    logger.debug("created " + str(storage_dir))
    return storage_dir


def create_storage_dirs(account_id, timestamp):
    logger.debug("Creating storage dirs")
    base_dir = Path("db")
    storage_dir = base_dir / account_id / "monitors" / timestamp
    storage_dir.mkdir(mode=0o777, parents=True, exist_ok=True)
    logger.debug("created " + str(storage_dir))
    return storage_dir


def save_json_to_file(entity_json, file_name):
    curr_dir = Path(".")
    to_file = curr_dir / file_name
    store_file = create_file(to_file)
    store_file.write_text(json.dumps(entity_json, indent=utils.DEFAULT_INDENT))


def create_file(file_name):
    if file_name.exists():
        logger.info("Removing existing file " + file_name.name)
        os.remove(file_name)
    file_name.touch()
    if file_name.exists():
        logger.info("Created " + file_name.name)
    else:
        logger.error("Could not create " + file_name.name)
    return file_name


def load_names(from_file):
    names = []
    with open(from_file) as input_names:
        for monitor_name in input_names:
            names.append(monitor_name.rstrip().lstrip())
    return names


# creates and returns a file in the output directory
def create_output_file(file_name):
    logger.debug("Creating output file")
    output_dir = Path("output")
    output_dir.mkdir(mode=0o777, exist_ok=True)
    monitor_names_file = output_dir / file_name
    return create_file(monitor_names_file)


def sanitize(name):
    illegal_characters = ['/', '?', '<', '>', '\\', ':', '*', '|']
    characters = list(name)
    for index, character in enumerate(characters):
        if characters[index] in illegal_characters:
            characters[index] = '~'
    name = ''.join(characters)
    return name


def save_json(dir_path, file_name, dictionary):
    dir_path.mkdir(mode=0o777, parents=True, exist_ok=True)
    logger.debug("created " + str(dir_path))
    json_file = dir_path / file_name
    create_file(json_file)
    json_file.write_text(json.dumps(dictionary, indent=utils.DEFAULT_INDENT))


def convert_timestamps_to_dates(violation):
    opened_at_date = datetime.fromtimestamp(violation['opened_at']/1000)
    violation['opened_at'] = opened_at_date
    if 'closed_at' in violation:
        closed_at_date = datetime.fromtimestamp(violation['closed_at']/1000)
        violation['closed_at'] = closed_at_date
    return violation