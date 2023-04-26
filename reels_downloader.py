import os
import requests
import threading
import zipfile
import logging
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QTextEdit, QPushButton, QWidget, QMessageBox, QDialog, QDialogButtonBox, QTextBrowser
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import pyqtSignal
import qtmodern.styles
import qtmodern.windows
from PyQt5.QtGui import QIcon
from instaloader import Instaloader, Post
from PyQt5.QtGui import QPixmap
import re
import sys

logging.basicConfig(
    filename=os.path.join(os.path.expanduser('~'), 'Reels_Downloader.log'),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up window properties
        self.setWindowTitle("Instagram Reels Downloader")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowIcon(QIcon(resource_path("potatowatts.ico")))

        # Create layout
        layout = QVBoxLayout()

        # Create input box for links
        self.links_label = QLabel("Enter Instagram Reel video links (one per line):")
        layout.addWidget(self.links_label)
        self.links_box = QTextEdit()
        layout.addWidget(self.links_box)

        # Create download button
        self.download_button = QPushButton("Start Download")
        self.download_button.clicked.connect(self.download)
        layout.addWidget(self.download_button)

        # Create status label
        self.status_label = QLabel()
        self.status_label.setAutoFillBackground(True)
        layout.addWidget(self.status_label)

        # Add the agreement text
        self.agreement_label = QLabel("By using this tool, you agree to the following Disclaimer:")
        layout.addWidget(self.agreement_label)

        # Create "Made by PotatoWatts" button and connect it to the custom dialog
        self.made_by_button = QPushButton("View Disclaimer")
        self.made_by_button.clicked.connect(self.show_made_by_dialog)
        layout.addWidget(self.made_by_button)

        self.agreement_label = QLabel("Made by PotatoWatts (@PotatoWatts on Telegram)")
        layout.addWidget(self.agreement_label)

        image_text_layout = QHBoxLayout()
        image_text_layout.addStretch(1)

        # Add an image below the download button
        self.image_label = QLabel(self)
        pixmap = QPixmap(resource_path("image_1.png"))
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(67, 64)  # Set this to the original size of your image or an appropriate size maintaining aspect ratio
        image_text_layout.addWidget(self.image_label)

        # Add the "pW Software" text with a white color and larger font
        self.pw_software_label = QLabel("<p style='color: white; font-size: 18px;'>pW Software</p>")
        image_text_layout.addWidget(self.pw_software_label)

        image_text_layout.addStretch(1)
        layout.addLayout(image_text_layout)

        # Set layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def download(self):
        # Get the links from the input box
        links = self.links_box.toPlainText().strip().split("\n")

        # Check if the list of links is empty
        if not links or all(link.strip() == '' for link in links):
            QMessageBox.warning(self, "Error", "Please enter at least one valid Instagram Reel link.")
            return

        # Check if the links are valid
        for link in links:
            if not self.extract_shortcode(link):
                QMessageBox.warning(self, "Error", f"Invalid Instagram Reel link: {link}")
                return

        # Create a directory to store the videos
        if not os.path.exists(os.path.join(os.path.expanduser('~'), 'Reels')):
            os.mkdir("Reels")

        # Disable the download button
        self.download_button.setEnabled(False)

        # Start a new thread to download the videos
        threading.Thread(target=self.download_videos, args=(links,)).start()

    def download_videos(self, links):
        # Initialize Instaloader
        L = Instaloader(save_metadata=False, download_geotags=False, download_comments=False)

        # Download the videos
        for i, link in enumerate(links):
            try:
                shortcode = self.extract_shortcode(link)
                post = Post.from_shortcode(L.context, shortcode)
                if post.is_video:
                    L.download_post(post, os.path.join(os.path.expanduser('~'), 'Reels'))
                    self.status_label.setText(f"Downloading Video {i+1}: Completed")
                else:
                    self.status_label.setText(f"Error: Not a video URL")
            except Exception as e:
                error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
                logging.error(error_msg)
                self.status_label.setText("An error occurred. Please check the log file.")

        # Create a ZIP file of the videos
        with zipfile.ZipFile(os.path.join(os.path.expanduser('~'), "Reels.zip"), "w") as f:
            for filename in os.listdir("Reels"):
                if filename.endswith(".mp4"):
                    f.write(os.path.join("Reels", filename), filename)

        # Remove the directory with the videos
        reels_directory = os.path.join(os.path.expanduser('~'), 'Reels')
        for filename in os.listdir(reels_directory):
            os.remove(os.path.join(reels_directory, filename))
        os.rmdir(reels_directory)

        # Enable the download button
        self.download_button.setEnabled(True)

        # Update the status label
        self.status_label.setText("Done!")

        # Show a message box with download info
        QMessageBox.information(self, "Download Complete", "All videos have been downloaded and zipped.")

    def extract_shortcode(self, url):
        regex = r"(?<=instagram\.com/)(p|reel|tv)/([\w-]+)"
        matches = re.search(regex, url)
        if matches:
            return matches.group(2)
        return None

    def show_made_by_dialog(self):
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Disclaimer")

        # Create dialog layout
        dialog_layout = QVBoxLayout()

        # Create text browser for the custom dialog
        text_browser = QTextBrowser()
        text_browser.setText("This tool is provided 'as is' without any warranties or guarantees, either express or implied. The developer disclaims all liability for any direct, indirect, incidental, special, punitive, consequential, or other damages arising from the use of this tool. By using this tool, you agree to comply with Instagram's terms of service, any applicable laws, and assume full responsibility for your actions. You also acknowledge that the developer is not affiliated with, endorsed by, or in any way associated with Instagram.")
        dialog_layout.addWidget(text_browser)

        # Create close button for the custom dialog
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        dialog_layout.addWidget(close_button)

        # Set layout and execute the custom dialog
        dialog.setLayout(dialog_layout)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(resource_path("potatowatts.ico")))
    qtmodern.styles.dark(app)
    main_window = qtmodern.windows.ModernWindow(App())
    main_window.show()
    app.exec_()
