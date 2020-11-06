import os
import requests # get the requsts library from https://github.com/requests/requests
import datetime
import urllib.request
from datetime import timedelta, datetime

def daterange(start_date, end_date):
    n = 0

    while True:
        d = start_date + timedelta(days=n)
        if d > end_date:
            break
        n += 4
        yield d


# overriding requests.Session.rebuild_auth to mantain headers when redirected
class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'
    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

   # Overrides from the library to keep headers when redirected to or from
   # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname) and redirect_parsed.hostname != self.AUTH_HOST and original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']

        return




def get_fnames(date):
    fnames = []
    url = 'https://e4ftl01.cr.usgs.gov/MOTA/MCD43A4.006/{}/'.format(date.strftime("%Y.%m.%d"))
    au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]

    with urllib.request.urlopen(url) as f:
        line = f.readline()
        while line:
            parts = line.decode('utf-8').split('"')
            if len(parts) > 6:
                fname = parts[5]
                if fname[-4:] == ".hdf":
                    tile_id = fname.split('.')
                    if tile_id[2] in au_tiles:
                        fnames.append(fname)
            line = f.readline()

    return fnames


def download_file(session, fname, date):
    url = "https://e4ftl01.cr.usgs.gov/MOTA/MCD43A4.006/{}/{}".format(date.strftime("%Y.%m.%d"), fname)
    # extract the filename from the url to be used when saving the file

    try:
        # submit the request using the session
        response = session.get(url, stream=True)
        print(response.status_code)
        # raise an exception in case of http errors
        response.raise_for_status()
        # save the file
        with open(fname, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024*1024):
                fd.write(chunk)

    except requests.exceptions.HTTPError as e:
        # handle any errors here
        print(e)
        exit()


# create session with the user credentials that will be used to authenticate access to the data
username = "xxxxx"
password= "xxxxxxxx"
session = SessionWithHeaderRedirection(username, password)

for date in daterange(datetime(2019, 9, 14), datetime.now()):
    for fname in get_fnames(date):
        print("Downloading...", fname)
        download_file(session, fname, date)

print("Done!")
