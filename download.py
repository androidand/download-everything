import os
import requests
from bs4 import BeautifulSoup
import signal
import sys
from tqdm.auto import tqdm
from zipfile import ZipFile
from concurrent.futures import ThreadPoolExecutor


class TqdmConnectionErrorWrapper(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

    def set_description_from_response(self, response):
        if response.headers.get("Content-Length"):
            self.total = int(response.headers["Content-Length"])
            self.refresh()

        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition:
            filename = content_disposition.split("filename=")[-1].strip('"')
            self.set_description(filename)


def decode_filename(encoded_filename):
    return requests.utils.unquote(encoded_filename)


def download_with_retry(url, filename):
    for retry in range(3):
        try:
            with requests.get(url, timeout=10, stream=True) as response:
                response.raise_for_status()
                with TqdmConnectionErrorWrapper(unit='B', unit_scale=True, miniters=1, desc=filename) as progress_bar:
                    progress_bar.set_description_from_response(response)
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                progress_bar.update_to(len(chunk))
                    return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")
    if os.path.exists(filename):
        os.remove(filename)
    return False


def is_zipfile_valid(zip_filename):
    try:
        with ZipFile(zip_filename) as zf:
            return zf.testzip() is None
    except Exception as e:
        print(f"Error validating {zip_filename}: {e}")
        return False


def signal_handler(signal, frame):
    print("\nProgram interrupted. Finishing up and exiting.")
    sys.exit("Exiting")


def read_validated_files(file_path):
    if not os.path.exists(file_path):
        open(file_path, 'a').close()
    with open(file_path, 'r') as f:
        return set(line.strip() for line in f)


def write_validated_file(file_path, filename):
    with open(file_path, 'a') as f:
        f.write(filename + '\n')


def download_and_validate_file(base_url, link, validated_files, validated_files_path):
    filename = decode_filename(link['href'])
    download_url = base_url + link['href']
    if filename in validated_files:
        print(f"Skipping {filename} - already validated.")
        return
    if os.path.exists(filename) and is_zipfile_valid(filename):
        print(f"Skipping {filename} - already downloaded and valid.")
        validated_files.add(filename)
        return
    print(f"Downloading {filename}...")
    success = download_with_retry(download_url, filename)
    if success and is_zipfile_valid(filename):
        print(f"{filename} downloaded and validated.")
        validated_files.add(filename)
        write_validated_file(validated_files_path, filename)
    else:
        print(f"{filename} is not a valid zip file. Deleting...")
        if os.path.exists(filename):
            os.remove(filename)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    validated_files_path = 'validated_files'
    validated_files = read_validated_files(validated_files_path)
    base_url = 'https://the-eye.eu/public/Games/eXo/eXoDOS_v5/eXo/eXoDOS/'
    html_page = requests.get(base_url).text
    soup = BeautifulSoup(html_page, 'html.parser')
    links = soup.find_all('a', href=lambda x: x and x.endswith('.zip'))

    with ThreadPoolExecutor() as executor:
        for link in links:
            executor.submit(download_and_validate_file, base_url,
                            link, validated_files, validated_files_path)


if __name__ == "__main__":
    main()
