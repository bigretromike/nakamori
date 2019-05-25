import sys
import traceback
import zipfile
import zlib
from collections import defaultdict
from distutils.version import LooseVersion
from shutil import copy2
from zipfile import ZipFile
import os


def calculate_file_crc(check_file, filepath, file_with_dir):
    if not file_with_dir.endswith('hash.sfv'):
        with open(check_file, 'a') as the_file:
            buf = open(filepath, 'rb').read()
            buf = format(zlib.crc32(buf) & 0xFFFFFFFF, 'x')
            the_file.write(file_with_dir + ' ' + buf + '\n')


def add_file(list_of_processed_files, hash_path, full_path, filename):
    if full_path not in list_of_processed_files:
        # excluded from adding to list
        excluded_files = ['build.py', '.idea', '.git', 'xbmc.py', 'xbmcaddon.py',
                          'xbmcgui.py', 'xbmcplugin.py', 'xbmcvfs.py', 'sh.exe.stackdump']

        if os.path.basename(filename) not in excluded_files:
            list_of_processed_files.append(full_path)
            calculate_file_crc(hash_path, full_path, filename)


def look_inside(origin_path, path, list_of_files, file_paths):
    for files in os.listdir(path):
        y = os.path.join(path, files)
        if os.path.isfile(y):
            file_path = str(y).replace(origin_path, '..')
            add_file(list_of_files, file_paths, y, file_path)
        elif os.path.isdir(y):
            look_inside(origin_path, y, list_of_files, file_paths)


def get_all_file_paths(directory):
    # initializing empty file paths list
    file_paths = []

    # make hash.sfv
    if not os.path.exists(os.path.join(directory, 'resources')):
        os.mkdir(os.path.join(directory, 'resources'))

    # check hash file (wipe)
    check_file = os.path.join(directory, 'resources', 'hash.sfv')
    if os.path.exists(check_file):
        os.remove(check_file)

    # iterate over ALL files make list of those for zip and calculate hash
    # crawling through directory and subdirectories
    look_inside(directory, directory, file_paths, check_file)

    # returning all file paths
    return file_paths


nakamori_double_folder = [
    os.path.join('nakamori.contextmenu', 'context.nakamori.calendar'),
    os.path.join('nakamori.contextmenu', 'context.nakamori.vote'),
]

nakamori_files = [
    'plugin.video.nakamori',
    'nakamori.resource',
    'context.nakamori.calendar',
    'context.nakamori.vote',
    'script.module.nakamori',
    'script.module.nakamori-lib',
    'script.module.nakamoriplayer',
    'service.nakamori',
    'script.module.pydevd-pycharm',
    'kodi-plugin-routing'
]


def get_news():
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    changelog_txt_path = os.path.join(root_path, nakamori_files[0], 'changelog.txt')
    fstream = open(changelog_txt_path, 'r')
    changelog = defaultdict(list)
    current_version = None
    for line in fstream.readlines():
        try:
            line = line.strip()
            if line == '':
                continue
            if line.startswith('#'):
                continue
            if line.startswith('!--'):
                try:
                    current_version = LooseVersion(line.replace('!--', '').strip())
                    # current line is version so go to next line
                    continue
                except:
                    pass
            if current_version is None:
                continue
            changelog[current_version.vstring].append(line)
        except:
            pass
    changelog.default_factory = None

    # build the text based on previous version.
    # This is important, as someone might open kodi for the first time in a while and skip several versions
    max_version = (LooseVersion('0'), [])
    for k, v in changelog.items():
        if LooseVersion(k) > max_version[0]:
            max_version = (LooseVersion(k), v)

    changelog_text = 'Version ' + max_version[0].vstring
    for line in max_version[1]:
        changelog_text += '[CR]- ' + line

    return changelog_text


def replace_news():
    replace_me = '{NEWS REPLACE ME}'
    news = get_news()
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    addon_xml_path = os.path.join(root_path, nakamori_files[0], 'addon.xml')

    copy2(addon_xml_path, root_path)

    with open(addon_xml_path) as f:
        s = f.read()
        if replace_me not in s:
            return

    with open(addon_xml_path, 'w') as f:
        print('Adding news to ')
        s = s.replace(replace_me, news)
        f.write(s)


def restore_backup():
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    addon_xml_path = os.path.join(root_path, nakamori_files[0])
    addon_xml_path_temp = os.path.join(root_path, 'addon.xml')

    copy2(addon_xml_path_temp, addon_xml_path)
    os.remove(addon_xml_path_temp)


def move_folders_out_folder():
    from distutils.dir_util import copy_tree
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

    for directory in nakamori_double_folder:
        try:
            source = os.path.join(root_path, directory)
            destination = os.path.join(root_path, os.path.basename(os.path.normpath(source)))
            if not os.path.exists(destination):
                os.makedirs(destination)
            copy_tree(source, destination)
        except Exception as ex:
            print(str(ex))
            pass


def main():
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    try:
        replace_news()
    except:
        pass

    move_folders_out_folder()

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

        try:
            restore_backup()
        except:
            pass


if __name__ == '__main__':
    main()
