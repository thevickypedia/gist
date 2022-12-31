import logging
import os
import shutil

import dotenv
import requests
from git import Repo

dotenv.load_dotenv(dotenv_path=".env")

FORMATTER = logging.Formatter(datefmt='%b-%d-%Y %I:%M:%S %p',
                              fmt='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s')
LOGGER = logging.getLogger(__name__)
HANDLER = logging.StreamHandler()
HANDLER.setFormatter(fmt=FORMATTER)
LOGGER.addHandler(hdlr=HANDLER)
LOGGER.setLevel(level=logging.DEBUG)

BASE_URL = "https://api.github.com"

GIT_USER = os.environ.get('GIT_USER') or os.environ.get('git_user')
GIT_PASS = os.environ.get('GIT_PASS') or os.environ.get('git_pass')


def get_gists_by_user(username: str = GIT_USER):
    response = requests.get(url="%s/users/%s/gists" % (BASE_URL, username))
    if response.ok:
        gists = response.json()
        for gist in gists:
            yield gist.get('html_url')
    else:
        response.raise_for_status()


def get_all_gists(per_page: int = None, page: int = None, log: bool = True):
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer %s' % GIT_PASS,
        'X-GitHub-Api-Version': '2022-11-28',
    }
    response = requests.get('%s/gists' % BASE_URL, headers=headers, params={"per_page": per_page, "page": page})
    if response.ok:
        gists = response.json()
        for gist in gists:
            if log:
                LOGGER.info("%s: %s" % (list(gist.get('files').keys())[0], gist.get('description')))
            yield gist


def clone_gist_by_filename(filename: str):
    repo = Repo()
    _cloned = False
    for gist in get_all_gists(log=False):
        if filename in list(gist.get('files').keys()):
            clone = gist.get('html_url').split('/')[-1]
            if os.path.isdir(clone):
                LOGGER.warning("Deleting existing gist %s" % clone)
                shutil.rmtree(clone)
            LOGGER.info("Cloning to %s" % clone)
            repo.clone_from(url=gist.get('html_url'), to_path=clone)
            _cloned = True
    if not _cloned:
        LOGGER.warning("No repo with '%s' file was found" % filename)


def gist_push(repo_path: str, commit_msg: str, delete_after: bool = True):
    repo = Repo(path=repo_path)
    repo.git.add(update=True)
    repo.index.commit(message=commit_msg)
    origin = repo.remote(name='origin')
    origin.push()
    LOGGER.info("Changes pushed to origin")
    if delete_after:
        LOGGER.info("Deleting repo %s" % repo_path)
        shutil.rmtree(repo_path)
