### A class that keeps track of where files are and what files are, also ensures that the files are in the correct format and exist
'''

Input: 
    - A file path to a directory
    - A zip file

    optional:
    - A file path to a file of raw data
    - A file path to a file of processed data
    - A file path to a image
    - A file path to a video file
    - A file path to a file of audio data
'''
import os
import zipfile
import pandas as pd
import numpy as np

class Data_collection_object:
    # Constructor
    def __init__(self, directory = None, zip_file = None, raw_data = None, processed_data = None, image = None, video = None, audio = None):
        self.directory = directory
        self.zip_file = zip_file
        self.raw_data = [raw_data] if not isinstance(raw_data, list) else raw_data
        self.processed_data = [processed_data] if not isinstance(processed_data, list) else processed_data
        self.image = image
        self.video = video
        self.audio = audio