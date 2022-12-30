import os

import dotenv
import requests

dotenv.load_dotenv(dotenv_path=".env")

BASE_URL = "https://api.github.com"


def get_gists_by_user(username: str = os.environ.get('GIT_USER')):
    response = requests.get(url="%s/users/%s/gists" % (BASE_URL, username))
    if response.ok:
        gists = response.json()
        for gist in gists:
            yield gist.get('html_url')
    else:
        response.raise_for_status()


def get_all_gists(per_page: int = None, page: int = None):
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer %s' % os.environ.get('GIT_PASS'),
        'X-GitHub-Api-Version': '2022-11-28',
    }
    response = requests.get('%s/gists' % BASE_URL, headers=headers, params={"per_page": per_page, "page": page})
    if response.ok:
        gists = response.json()
        for gist in gists:
            yield gist
            # print("%s: %s - %s" % (list(gist.get('files').keys())[0], gist.get('description'), gist.get('html_url')))
            # os.system("git clone %s" % gist.get('html_url'))


if __name__ == '__main__':
    print(list(get_gists_by_user()))
