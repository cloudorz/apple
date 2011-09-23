# coding: utf-8

import os.path
from tornado.options import options

def save_images(http_files):

    for http_file in http_files:
        file_path = os.path.join(options.path, http_file['filename'])
        with open(file_path, 'wb') as f:
            f.write(http_file['body'])

        if not os.path.exists(file_path):
            return False

    return True
