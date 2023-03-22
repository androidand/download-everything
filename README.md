## Download Everything
This script fetches a web page, identifies all files with the ".zip" extension, and downloads them to a specified directory. If a file has already been downloaded (by matching both the filename and the size of the file), it will be skipped. The script also provides a progress update for each downloaded file.
Usage
The script can be run from the command line with the following command:



python download.py <url> <directory>
* url (optional): the URL of the web page to fetch files from. If not provided, the default URL will be used.
* directory (optional): the name of the directory to download files to. If not provided, the default directory "downloads" will be used.
Example usage:



python download.py "https://example.com/downloads/" "my_downloads"
This will fetch all files with the ".zip" extension from the URL "https://example.com/downloads/", and download them to the directory "my_downloads". If a file has already been downloaded, it will be skipped. The script will output a progress update for each downloaded file.
Note: The script requires the Python requests and beautifulsoup4 libraries to be installed. If you don't have them installed, you can install them with the following command:


pip install requests beautifulsoup4
To ensure that the downloaded files are not committed to version control, add the "downloads" directory to your .gitignore file.
