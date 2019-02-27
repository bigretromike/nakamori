import sys
import traceback
import zipfile
import zlib
from zipfile import ZipFile
import os


def get_all_file_paths(directory):
    # initializing empty file paths list
    file_paths = []

    # make hash.sfv
    if not os.path.exists(os.path.join(directory, 'resources')):
        os.mkdir(os.path.join(directory, 'resources'))
    check_file = os.path.join(directory, 'resources', 'hash.sfv')
    os.remove(check_file)
    with open(check_file, 'a') as the_file:

        # crawling through directory and subdirectories
        for root, directories, files in os.walk(directory):
            for filename in files:
                # join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                excluded_files = ['build.py', 'README', 'LICENSE', '.idea', '.git', 'xbmc.py', 'xbmcaddon.py', 'xbmcgui.py',
                         'xbmcplugin.py', 'xbmcvfs.py', 'hash.sfv']
                if any(x in filepath for x in excluded_files):
                    continue

                buf = open(filepath, 'rb').read()
                buf = format(zlib.crc32(buf) & 0xFFFFFFFF, 'x')
                the_file.write(filename + ' ' + buf + '\n')
                file_paths.append(filepath)

    # add hash file
    file_paths.append(check_file)
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
