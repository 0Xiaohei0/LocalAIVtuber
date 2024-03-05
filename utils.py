import os
import requests
import zipfile
import io
from tqdm import tqdm


def summarize_bytes(data, max_length=10):
    """Summarize bytes-like data with a maximum length."""
    if len(data) > max_length:
        # Convert the sliced bytes to a string and append the total length
        data_summary = data[:max_length].decode(
            "utf-8", "replace") + f"... ({len(data)} bytes total)"
    else:
        data_summary = data.decode("utf-8", "replace")
    return data_summary


def queue_to_list(q):
    # Convert queue to list without modifying the original queue
    temp_list = list(q.queue)

    # Start the result list with the queue's length
    result_list = [str(len(temp_list))]

    # Append each item from the list to the result list
    for item in temp_list:
        if isinstance(item, bytes):
            # Summarize bytes-like data
            summarized = summarize_bytes(item)
            result_list.append(summarized)
        else:
            result_list.append(str(item))

    return result_list


def download_and_extract_zip(url, extract_to='.', folder_name=None):
    """
    Downloads a ZIP file from the given URL, shows a progress bar, and extracts it to the specified directory.

    Args:
    url (str): The URL of the zip file to download.
    extract_to (str): The directory to extract the contents to. Defaults to the current directory.
    folder_name (str, optional): The folder name within the extract_to directory where contents are extracted.

    Returns:
    the name of the extracted folder
    """
    print(f"Downloading from {url}.")
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad requests

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        progress_bar = tqdm(total=total_size_in_bytes,
                            unit='iB', unit_scale=True)

        with io.BytesIO() as file_stream:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file_stream.write(data)

            progress_bar.close()

            # Move the pointer to the start of the stream
            file_stream.seek(0)

            if folder_name is None:
                folder_name = os.path.basename(url).rsplit('.', 1)[0]
            # Extract the zip file
            with zipfile.ZipFile(file_stream) as the_zip:
                extract_path = f"{extract_to}/{folder_name}" if folder_name else extract_to
                the_zip.extractall(path=extract_path)

        print(
            f"Zip file from {url} has been downloaded and extracted to '{extract_path}'.")
        return extract_path

    except requests.RequestException as e:
        print(f"An error occurred while downloading the file: {e}")
    except zipfile.BadZipFile:
        print("The downloaded file is not a zip file or it is corrupted.")
