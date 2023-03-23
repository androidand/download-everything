import os
import requests
from tqdm import tqdm

# function to decode url-encoded filename
def decode_filename(encoded_filename):
    return requests.utils.unquote(encoded_filename)

# function to download file from url and retry on failure
def download_with_retry(url, filename):
    retry = 0
    while retry < 3:
        # check if the file already exists
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            headers = {'Range': f'bytes={file_size}-'}
            response = requests.get(url, headers=headers, stream=True)
            mode = 'ab'  # append to the file if it already exists
        else:
            response = requests.get(url, stream=True)
            mode = 'wb'  # write a new file if it doesn't exist
        if response.status_code == 200 or response.status_code == 206:
            with open(filename, mode) as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    # update progress bar
                    progress_bar.update(len(chunk))
            return True
        retry += 1
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
        if not os.path.exists(filename):
            print(f"Downloading {filename}...")
            with tqdm(unit='B', unit_scale=True, miniters=1, desc=filename) as progress_bar:
                success = download_with_retry(download_url, filename)
                while not success:
                    print(f"Retrying {filename}...")
                    success = download_with_retry(download_url, filename)
        else:
            print(f"{filename} already exists. Skipping download.")
