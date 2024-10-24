import os
import csv
import requests
from tkinter import Tk, filedialog
from urllib.parse import urlparse
from os.path import splitext
import mimetypes

# Function to download images and update CSV
def download_image(image_url, image_name, save_folder, row):
    # Parse the URL to get the original file extension
    #parsed_url = urlparse(image_url)
    #original_extension = splitext(parsed_url.path)[1]  # Get file extension (e.g., .jpg)

    # Ensure the file extension is lower case
    #original_extension = original_extension.lower()

    try:
        # Send a GET request to download the image
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type')
            if content_type:
                # Use mimetypes to determine the file extension
                file_extension = mimetypes.guess_extension(content_type)
            else:
                # Fallback if no Content-Type header is present
                file_extension = ".jpg"

            # Remove any file extension from image_name if it exists
            image_name_without_ext, _ = splitext(image_name)

            # If the image URL doesn't have a filename, generate one
            if not image_name_without_ext:
                parsed_url = urlparse(image_url)
                # Use the last part of the URL path or a fallback name
                image_name_without_ext = parsed_url.path.strip('/').split('/')[-1] or "image"

            # Build the full path for saving the image
            file_path = os.path.join(save_folder, image_name_without_ext + file_extension)

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded {image_name_without_ext}{file_extension}")

            # Update the row with the downloaded file name (including correct extension)
            row.append(image_name_without_ext + file_extension)
        else:
            error_msg = f"Failed to download: Status code {response.status_code}"
            print(error_msg)

            # Update the row with the error message
            row.append(error_msg)
    except Exception as e:
        error_msg = f"Error downloading: {e}"
        print(error_msg)

        # Update the row with the error message
        row.append(error_msg)

    return row

# Function to process the CSV and download images
def process_csv(file_path):
    # Get the current user's desktop folder
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

    # Create the pics folder on the desktop
    save_folder = os.path.join(desktop, 'pics')
    os.makedirs(save_folder, exist_ok=True)

    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.png')

    # Read the CSV file
    updated_rows = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';')
        for row in csv_reader:
            # Check if the row has at least two columns: URL and filename
            if len(row) >= 2:
                url = row[0]  # First column is the URL
                image_name = row[1]  # Second column is the file name

                # If the URL looks like it doesn't have an extension or name, handle it
                if not any(url.lower().endswith(ext) for ext in image_extensions):
                    # Call download_image and get the updated row
                    updated_row = download_image(url, image_name, save_folder, row)
                    updated_rows.append(updated_row)
                else:
                    # If it's a regular image URL, also process it
                    updated_row = download_image(url, image_name, save_folder, row)
                    updated_rows.append(updated_row)
            else:
                # If the row doesn't have enough columns, leave it unchanged
                updated_rows.append(row)

    # Write the updated rows back to the CSV file
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';')
        csv_writer.writerows(updated_rows)

# Function to open a file dialog and select a CSV file
def open_file_dialog():
    # Hide the root Tk window
    root = Tk()
    root.withdraw()

    # Open the file dialog
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )

    # If a file was selected, process it
    if file_path:
        process_csv(file_path)
    else:
        print("No file selected.")

# Run the file dialog to start the process
if __name__ == "__main__":
    open_file_dialog()
