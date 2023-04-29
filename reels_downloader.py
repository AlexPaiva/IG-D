import os
import zipfile
import logging
import traceback
import re
import sys
from instaloader import Instaloader, Post
from instaloader.exceptions import ConnectionException

logging.basicConfig(
    filename=os.path.join(os.path.expanduser('~'), 'Reels_Downloader.log'),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def download_videos(links):
    # Initialize Instaloader
    L = Instaloader(save_metadata=False, download_geotags=False, download_comments=False)
    reels_directory = 'Reels'

    try:
        # Download the videos
        for i, link in enumerate(links):
            try:
                shortcode = extract_shortcode(link)
                post = Post.from_shortcode(L.context, shortcode)
                if post.is_video:
                    L.download_post(post, 'Reels')
                    logging.info(f"Downloading Video {i+1}: Completed!")
                else:
                    logging.error(f"Error: Not a video URL")
            except ConnectionException as e:
                logging.error(f"An error occurred 7: {e}")
            except Exception as e:
                logging.error(f"An error occurred 9: {e}")
    finally:
        # Create a ZIP file of the videos
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        with zipfile.ZipFile(os.path.join(desktop_path, "Reels.zip"), "w") as f:
            for filename in os.listdir(reels_directory):
                if filename.endswith(".mp4"):
                    f.write(os.path.join(reels_directory, filename), filename)

        # Remove the directory with the videos
        for filename in os.listdir(reels_directory):
            os.remove(os.path.join(reels_directory, filename))
        os.rmdir(reels_directory)

        logging.info("Done! All videos have been downloaded and zipped.")

def extract_shortcode(url):
    regex = r"(?<=instagram\.com/)(p|reel|tv)/([\w-]+)"
    matches = re.search(regex, url)
    if matches:
        return matches.group(2)
    return None


def main():
    home_directory = os.path.expanduser("~")
    links_path = os.path.join(os.path.expanduser("~"), "Desktop", "Links.txt")
    
    if not os.path.exists(links_path):
        logging.error(f"Error: The 'Links.txt' file is not found in the home directory: {home_directory}")
        return

    with open(links_path, "r") as f:
        links = f.readlines()

    if not links:
        logging.warning("Please enter at least one valid Instagram Reel link in the 'Links.txt' file.")
        return

    for link in links:
        if not extract_shortcode(link):
            logging.warning(f"Invalid Instagram Reel link: {link}")
            return

    reels_directory = os.path.join(os.path.expanduser('~'), 'Reels')
    if not os.path.exists(reels_directory):
        os.makedirs(reels_directory)

    download_videos(links)

if __name__ == "__main__":
    main()
