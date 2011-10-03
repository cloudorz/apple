# coding: utf-8

import os.path, hashlib
from tornado.options import options

def save_images(http_files):

    for http_file in http_files:
        name, ext = http_file['filename'].rsplit('.')
        file_path = os.path.join(options.path, "i/%s.%s" % (hashlib.md5(name).hexdigest(), ext))
        with open(file_path, 'wb') as f:
            f.write(http_file['body'])

        if not os.path.exists(file_path):
            return False

    return True
