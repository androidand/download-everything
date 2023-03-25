import os
import requests
import signal
from tqdm import tqdm
from zipfile import ZipFile

# function to decode url-encoded filename
def decode_filename(encoded_filename):
    return requests.utils.unquote(encoded_filename)

# function to download file from url and retry on failure
def download_with_retry(url, filename):
    retry = 0
    while retry < 3:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")
        retry += 1
    if os.path.exists(filename):
        os.remove(filename)
    return False

# function to check if a zip file is valid
def is_zipfile_valid(zip_filename):
    try:
        with ZipFile(zip_filename) as zf:
            return zf.testzip() is None
    except Exception as e:
        print(f"Error validating {zip_filename}: {e}")
        return False

# define signal handler to handle interrupts
def signal_handler(signal, frame):
    print("\nProgram interrupted. Finishing up and exiting.")
    global interrupted
    interrupted = True

def main():
    # set up interrupt handler
    signal.signal(signal.SIGINT, signal_handler)

    # create validated_files if it does not exist
    if not os.path.exists('validated_files'):
        open('validated_files', 'a').close()

    # read validated_files into a set
    with open('validated_files', 'r') as f:
        validated_files = set(line.strip() for line in f)

    # base url for the files
    base_url = 'https://the-eye.eu/public/Games/eXo/eXoDOS_v5/eXo/eXoDOS/'

    # retrieve the HTML page with links
    html_page = requests.get(base_url).text

    # loop through each link and download the corresponding file
    interrupted = False
    for line in html_page.splitlines():
        if '.zip' in line:
            href_start = line.find('href=') + 6
            href_end = line.find('.zip') + 4
            href_value = line[href_start:href_end]
            filename = decode_filename(href_value)
            download_url = base_url + href_value
            if filename in validated_files:
                print(f"Skipping {filename} - already validated.")
                continue
            if os.path.exists(filename):
                if is_zipfile_valid(filename):
                    print(f"Skipping {filename} - already downloaded and valid.")
                    validated_files.add(filename)
                    continue
                else:
                    print(f"{filename} exists but is not a valid zip file. Redownloading...")
            print(f"Downloading {filename}...")
            with tqdm(unit='B', unit_scale=True, miniters=1, desc=filename) as progress_bar:
                success = download_with_retry(download_url, filename)
                while not success and not interrupted:
                    print(f"Retrying {filename}...")
                    success = download_with_retry(download_url, filename)
                if interrupted:
                    break
                progress_bar.update(len(requests.get(download_url).content))
            if is_zipfile_valid(filename):
                print(f"{filename} downloaded and validated.")
                validated_files.add(filename)
                with open('validated_files', 'a') as f:
                    f.write(filename + '\n')
            else:
                print(f"{filename} is not a valid zip file. Deleting...")
                os.remove(filename)

if __name__ == "__main__":
    main()
