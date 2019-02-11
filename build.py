import sys
import traceback
import zipfile
from zipfile import ZipFile
import os


def get_all_file_paths(directory):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            if 'build.py' in filepath:
                continue
            if 'README' in filepath:
                continue
            if 'LICENSE' in filepath:
                continue
            if '.idea' in filepath:
                continue
            if '.git' in filepath:
                continue
            if 'xbmc.py' in filepath:
                continue
            if 'xbmcaddon.py' in filepath:
                continue
            if 'xbmcgui.py' in filepath:
                continue
            if 'xbmcplugin.py' in filepath:
                continue
            if 'xbmcvfs.py' in filepath:
                continue
            file_paths.append(filepath)

    # returning all file paths
    return file_paths


nakamori_files = [
    'nakamori.resource',
    'plugin.video.nakamori',
    'script.module.nakamori',
    'script.module.nakamori-lib',
    'script.module.nakamoriplayer',
    'service.nakamori',
    'script.module.pydevd-pycharm'
]


def main():
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    for directory in nakamori_files:
        try:
            plugin_path = os.path.join(root_path, directory)
            file_paths = get_all_file_paths(plugin_path)

            # printing the list of all files to be zipped
            print('Following files will be zipped:')
            for file_name in file_paths:
                print(file_name)

            out = os.path.join(root_path, 'build')
            if not os.path.exists(out):
                os.mkdir(out)
            out = os.path.join(out, directory + '.zip')
            if os.path.exists(out):
                os.remove(out)

            # writing files to a zipfile
            with ZipFile(out, 'w') as zip_file:
                # writing each file one by one
                for file_path in file_paths:
                    rel_path = os.path.relpath(file_path, root_path)
                    zip_file.write(file_path, rel_path, zipfile.ZIP_DEFLATED)

            print('Zipped ' + directory + ' successfully!')
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if exc_type is not None and exc_obj is not None and exc_tb is not None:
                print(str(exc_type) + " at line " + str(exc_tb.tb_lineno) + " in file " + str(
                    os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]))
                traceback.print_exc()


if __name__ == '__main__':
    main()
