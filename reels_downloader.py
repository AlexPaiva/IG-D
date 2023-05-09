import os
import zipfile
import logging
import traceback
import re
import sys
from instaloader import Instaloader, Post
from instaloader.exceptions import ConnectionException
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, PhotoImage
import tkinter.messagebox as msgbox

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
    failed_indices = []

    try:
        # Download the videos
        for i, link in enumerate(links):
            try:
                shortcode = extract_shortcode(link)
                post = Post.from_shortcode(L.context, shortcode)
                if post.is_video:
                    L.download_post(post, 'Reels')
                    logging.info(f"Downloading Video {i+1}: Completed!")
                    progress_var.set(f"Downloading Video {i+1}: Completed!")
                    root.update_idletasks()
                else:
                    logging.error(f"Error: Not a video URL")
                    failed_indices.append(i)
                
            except:
                try:
                    shortcode = extract_shortcode(link)
                    post = Post.from_shortcode(L.context, shortcode)
                    if post.is_video:
                        L.download_post(post, 'Reels')
                        logging.info(f"Downloading Video {i+1}: Completed!")
                        progress_var.set(f"Downloading Video {i+1}: Completed!")
                        root.update_idletasks()
                    else:
                        logging.error(f"Error: Not a video URL")
                        failed_indices.append(i)
                except ConnectionException as e:
                    logging.error(f"An error occurred 7: {e}")
                    failed_indices.append(i)
                except Exception as e:
                    logging.error(f"An error occurred 9: {e}")
                    failed_indices.append(i)
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

        logging.info("Done! Videos have been downloaded and zipped. Links that failed: "+str(failed_indices))
        progress_var.set("Done! Videos have been downloaded and zipped. Links that failed: "+str(failed_indices))
        root.update_idletasks()

def extract_shortcode(url):
    regex = r"(?<=instagram\.com/)(p|reel|tv|reels)/([\w-]+)"
    matches = re.search(regex, url)
    if matches:
        return matches.group(2)
    return None

def start_download():
    links = links_text.get(1.0, tk.END).strip().split("\n")
    if not links:
        messagebox.showwarning("Warning", "Please enter at least one valid Instagram Reel link.")
        return
    
    if links[0] == "":
        messagebox.showwarning("Warning", "Please enter at least one valid Instagram Reel link.")
        return

    for link in links:
        if not extract_shortcode(link):
            messagebox.showwarning("Warning", f"Invalid Instagram Reel link: {link}")
            return

    reels_directory = os.path.join(os.path.expanduser('~'), 'Reels')
    if not os.path.exists(reels_directory):
        os.makedirs(reels_directory)

    download_videos(links)

root = tk.Tk()
root.title("Instagram Reels Downloader")
root.resizable(False, False)  # Make the interface non-resizable
root.iconbitmap(resource_path('potatowatts.ico'))

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create widgets
links_label = ttk.Label(frame, text="Enter Instagram Reel links (one per line):")
links_text = tk.Text(frame, wrap=tk.WORD, width=40, height=10)
download_button = tk.Button(frame, text="Download", command=start_download)
progress_var = tk.StringVar()

# Place widgets
links_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
links_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
download_button.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

# Load the image file
image_path = resource_path("image_1.png")  # Replace this with the path to your image file
photo = PhotoImage(file=image_path)

# Create a Label widget to display the image
image_label = ttk.Label(frame, image=photo)

# Create a Label widget for the "pW Software" text
pw_software_label = ttk.Label(frame, text="pW Software", font=("Arial", 16))

# Create a Canvas widget for the background rectangle
information_canvas = tk.Canvas(frame, width=360, height=100, highlightthickness=0, bd=0)
information_canvas.grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.SW)

# Create a rectangle on the canvas
information_canvas.create_rectangle(0, 0, 360, 100, fill='lightgray', outline='')

# Create a Label widget for the "Information:" text
information_label = ttk.Label(frame, text="Information:")

# Create a Label widget to display the messages (information) and place it on the canvas
information_text = ttk.Label(frame, textvariable=progress_var, wraplength=360, justify=tk.LEFT)
information_text_window = information_canvas.create_window(0, 0, window=information_text, anchor=tk.NW)

# Position the widgets using the grid() method
information_label.grid(row=3, column=0, pady=5, sticky=tk.W)
image_label.grid(row=5, column=0, pady=(30, 10), sticky=tk.E)
pw_software_label.grid(row=5, column=1, pady=(30, 10), sticky=tk.W)

disclaimer_label = ttk.Label(frame, text="By using this tool you agree to the following disclaimer:")

def show_disclaimer():
    msgbox.showinfo("Disclaimer", "This tool is provided 'as is' without any warranties or guarantees, either express or implied. The developer disclaims all liability for any direct, indirect, incidental, special, punitive, consequential, or other damages arising from the use of this tool. By using this tool, you agree to comply with Instagram's terms of service, any applicable laws, and assume full responsibility for your actions. You also acknowledge that the developer is not affiliated with, endorsed by, or in any way associated with Instagram.")
    
view_disclaimer_button = tk.Button(frame, text="View disclaimer", command=show_disclaimer)

disclaimer_label.grid(row=5, column=0, columnspan=2, pady=(0, 5), sticky=tk.NW)

view_disclaimer_button.grid(row=5, column=0, pady=(0, 5), sticky=tk.W)

# Run the interface
root.mainloop()
