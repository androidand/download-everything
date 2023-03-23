import os
import requests
from tqdm import tqdm
from zipfile import ZipFile


# function to decode url-encoded filename
def decode_filename(encoded_filename):
    return requests.utils.unquote(encoded_filename)

# function to download file from url and retry on failure
def download_with_retry(url, filename):
    retry = 0
    while retry < 3:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        retry += 1
    return False

# function to check if a zip file is valid
# def is_zipfile_valid(filename):
#     with zipfile.ZipFile(filename) as zf:
#         return zf.testzip() is None
def is_zipfile_valid(zip_filename):
    try:
        with ZipFile(zip_filename) as zf:
            return zf.testzip() is None
    except Exception as e:
        print(f"Error validating {zip_filename}: {e}")
        return False

# base url for the files
base_url = 'https://the-eye.eu/public/Games/eXo/eXoDOS_v5/eXo/eXoDOS/'

# retrieve the HTML page with links
html_page = requests.get(base_url).text

# loop through each link and download the corresponding file
for line in html_page.splitlines():
    if '.zip' in line:
        href_start = line.find('href=') + 6
        href_end = line.find('.zip') + 4
        href_value = line[href_start:href_end]
        filename = decode_filename(href_value)
        download_url = base_url + href_value
        if os.path.exists(filename):
            if is_zipfile_valid(filename):
                print(f"Skipping {filename} - already downloaded and valid.")
                continue
            else:
                print(f"{filename} exists but is not a valid zip file. Redownloading...")
        print(f"Downloading {filename}...")
        with tqdm(unit='B', unit_scale=True, miniters=1, desc=filename) as progress_bar:
            success = download_with_retry(download_url, filename)
            while not success:
                print(f"Retrying {filename}...")
                success = download_with_retry(download_url, filename)
            progress_bar.update(len(requests.get(download_url).content))
        if not is_zipfile_valid(filename):
            os.remove(filename)
            print(f"{filename} is not a valid zip file. Deleted.")
