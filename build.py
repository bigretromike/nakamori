import sys
import traceback
import zipfile
import zlib
from collections import defaultdict
from distutils.version import LooseVersion
from zipfile import ZipFile
import os


def get_all_file_paths(directory):
    # initializing empty file paths list
    file_paths = []

    # make hash.sfv
    if not os.path.exists(os.path.join(directory, 'resources')):
        os.mkdir(os.path.join(directory, 'resources'))
    check_file = os.path.join(directory, 'resources', 'hash.sfv')
    if os.path.exists(check_file):
        os.remove(check_file)
    with open(check_file, 'a') as the_file:

        # crawling through directory and subdirectories
        for root, directories, files in os.walk(directory):
            for filename in files:
                # join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                excluded_files = ['build.py', 'README', 'LICENSE', '.idea', '.git', 'xbmc.py', 'xbmcaddon.py',
                                  'xbmcgui.py', 'xbmcplugin.py', 'xbmcvfs.py', 'hash.sfv']
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
    'plugin.video.nakamori',
    'nakamori.resource',
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

    with open(addon_xml_path) as f:
        s = f.read()
        if replace_me not in s:
            return

    with open(addon_xml_path, 'w') as f:
        print('Adding news to ')
        s = s.replace(replace_me, news)
        f.write(s)


def main():
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    try:
        replace_news()
    except:
        pass

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
