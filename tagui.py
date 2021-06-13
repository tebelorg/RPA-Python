"""INTEGRATION ENGINE OF RPA FOR PYTHON PACKAGE ~ TEBEL.ORG"""
# Apache License 2.0, Copyright 2019 Tebel.Automation Private Limited
# https://github.com/tebelorg/RPA-Python/blob/master/LICENSE.txt
__author__ = 'Ken Soh <opensource@tebel.org>'
__version__ = '1.39.0'

import subprocess
import os
import sys
import time
import platform

# required for python 2 usage of io.open
if sys.version_info[0] < 3: import io

# default timeout in seconds for UI element
_tagui_timeout = 10.0

# default delay in seconds in while loops
_tagui_delay = 0.1

# default debug flag to print debug output
_tagui_debug = False

# flag to track if tagui session is started
_tagui_started = False

# flag to track visual automation connected
_tagui_visual = False

# flag to track chrome browser connected
_tagui_chrome = False

# id to track instruction count from rpa python to tagui
_tagui_id = 0

# to track the original directory when init() was called
_tagui_init_directory = ''

# to track location of TagUI (default user home folder)
if platform.system() == 'Windows':
    _tagui_location = os.environ['APPDATA']
else:
    _tagui_location = os.path.expanduser('~')
 
# delete tagui temp output text file to avoid reading old data 
if os.path.isfile('rpa_python.txt'): os.remove('rpa_python.txt')

# define local custom javascript functions for use in tagui
_tagui_local_js = \
"""// local custom helper function to check if UI element exists
// keep checking until timeout is reached before return result
// effect is interacting with element as soon as it appears

function exist(element_identifier) {

    var exist_timeout = Date.now() + casper.options.waitTimeout;

    while (Date.now() < exist_timeout) {
        if (present(element_identifier))
            return true;
        else
           sleep(100);
    }

    return false;

}

// function to replace add_concat() in tagui_header.js
// gain - echoing string with single and double quotes
// loss - no text-like variables usage since Python env

function add_concat(source_string) {

    return source_string;

}
"""

def _python2_env():
    """function to check python version for compatibility handling"""
    if sys.version_info[0] < 3: return True
    else: return False

def _python3_env():
    """function to check python version for compatibility handling"""
    return not _python2_env()

def _py23_decode(input_variable = None):
    """function for python 2 and 3 str-byte compatibility handling"""
    if input_variable is None: return None
    elif _python2_env(): return input_variable
    else: return input_variable.decode('utf-8')

def _py23_encode(input_variable = None):
    """function for python 2 and 3 str-byte compatibility handling"""
    if input_variable is None: return None
    elif _python2_env(): return input_variable
    else: return input_variable.encode('utf-8')

def _py23_open(target_filename, target_mode = 'r'):
    """function for python 2 and 3 open utf-8 compatibility handling"""
    if _python2_env():
        return io.open(target_filename, target_mode, encoding = 'utf-8')
    else:
        return open(target_filename, target_mode, encoding = 'utf-8') 

def _py23_read(input_text = None):
    """function for python 2 and 3 read utf-8 compatibility handling"""
    if input_text is None: return None
    if _python2_env(): return input_text.encode('utf-8')
    else: return input_text

def _py23_write(input_text = None):
    """function for python 2 and 3 write utf-8 compatibility handling"""
    if input_text is None: return None
    if _python2_env(): return input_text.decode('utf-8')
    else: return input_text

def _tagui_read():
    """function to read from tagui process live mode interface"""
    # readline instead of read, not expecting user input to tagui
    global _process; return _py23_decode(_process.stdout.readline())

def _tagui_write(input_text = ''):
    """function to write to tagui process live mode interface"""
    global _process; _process.stdin.write(_py23_encode(input_text))
    _process.stdin.flush(); # flush to ensure immediate delivery

def _tagui_output():
    """function to wait for tagui output file to read and delete it"""
    global _tagui_delay, _tagui_init_directory

    # to handle user changing current directory after init() is called
    init_directory_output_file = os.path.join(_tagui_init_directory, 'rpa_python.txt')

    # sleep to not splurge cpu cycles in while loop
    while not os.path.isfile('rpa_python.txt'):
        if os.path.isfile(init_directory_output_file): break
        time.sleep(_tagui_delay) 

    # roundabout implementation to ensure backward compatibility
    if os.path.isfile('rpa_python.txt'):
        tagui_output_file = _py23_open('rpa_python.txt', 'r')
        tagui_output_text = _py23_read(tagui_output_file.read())
        tagui_output_file.close()
        os.remove('rpa_python.txt')
    else:
        tagui_output_file = _py23_open(init_directory_output_file, 'r')
        tagui_output_text = _py23_read(tagui_output_file.read())
        tagui_output_file.close()
        os.remove(init_directory_output_file)

    return tagui_output_text

def _esq(input_text = ''):
    """function for selective escape of single quote ' for tagui"""
    # [BACKSLASH_QUOTE] marker to work together with send()
    return input_text.replace("'",'[BACKSLASH_QUOTE]')

def _sdq(input_text = ''):
    """function to escape ' in xpath for tagui live mode"""
    # change identifier single quote ' to double quote "
    return input_text.replace("'",'"')

def _started():
    global _tagui_started; return _tagui_started

def _visual():
    global _tagui_visual; return _tagui_visual

def _chrome():
    global _tagui_chrome; return _tagui_chrome

def _python_flow():
    """function to create entry tagui flow without visual automation"""
    flow_text = '// NORMAL ENTRY FLOW FOR RPA FOR PYTHON ~ TEBEL.ORG\r\n\r\nlive'
    flow_file = _py23_open('rpa_python', 'w')
    flow_file.write(_py23_write(flow_text))
    flow_file.close()

def _visual_flow():
    """function to create entry tagui flow with visual automation"""
    flow_text = '// VISUAL ENTRY FLOW FOR RPA FOR PYTHON ~ TEBEL.ORG\r\n' + \
                '// mouse_xy() - dummy trigger for SikuliX integration\r\n\r\nlive'
    flow_file = _py23_open('rpa_python', 'w')
    flow_file.write(_py23_write(flow_text))
    flow_file.close()

def _tagui_local():
    """function to create tagui_local.js for custom local functions"""
    global _tagui_local_js
    javascript_file = _py23_open('tagui_local.js', 'w')
    javascript_file.write(_py23_write(_tagui_local_js))
    javascript_file.close()

def _tagui_delta(base_directory = None):
    """function to download stable delta files from tagui cutting edge version"""
    global __version__
    if base_directory is None or base_directory == '': return False
    # skip downloading if it is already done before for current release
    if os.path.isfile(base_directory + '/' + 'rpa_python_' + __version__): return True

    # define list of key tagui files to be downloaded and synced locally
    delta_list = ['tagui', 'tagui.cmd', 'end_processes', 'end_processes.cmd', 
                    'tagui_header.js', 'tagui_parse.php', 'tagui.sikuli/tagui.py']

    for delta_file in delta_list:
        tagui_delta_url = 'https://raw.githubusercontent.com/tebelorg/Tump/master/TagUI-Python/' + delta_file
        tagui_delta_file = base_directory + '/' + 'src' + '/' + delta_file
        if not download(tagui_delta_url, tagui_delta_file): return False

    # make sure execute permission is there for .tagui/src/tagui and end_processes
    if platform.system() in ['Linux', 'Darwin']:
        os.system('chmod -R 755 "' + base_directory + '/' + 'src' + '/' + 'tagui" > /dev/null 2>&1')
        os.system('chmod -R 755 "' + base_directory + '/' + 'src' + '/' + 'end_processes" > /dev/null 2>&1')

    # create marker file to skip syncing delta files next time for current release
    delta_done_file = _py23_open(base_directory + '/' + 'rpa_python_' + __version__, 'w')
    delta_done_file.write(_py23_write('TagUI installation files used by RPA for Python'))
    delta_done_file.close()
    return True

def _patch_macos_pjs():
    """patch PhantomJS to latest v2.1.1 that plays well with new macOS versions"""
    if platform.system() == 'Darwin' and not os.path.isdir(tagui_location() + '/.tagui/src/phantomjs_old'):
        original_directory = os.getcwd(); os.chdir(tagui_location() + '/.tagui/src')
        print('[RPA][INFO] - downloading latest PhantomJS to fix OpenSSL issue')
        download('https://github.com/tebelorg/Tump/releases/download/v1.0.0/phantomjs-2.1.1-macosx.zip', 'phantomjs.zip')
        if not os.path.isfile('phantomjs.zip'):
            print('[RPA][ERROR] - unable to download latest PhantomJS v2.1.1')
            os.chdir(original_directory); return False
        unzip('phantomjs.zip'); os.rename('phantomjs', 'phantomjs_old'); os.rename('phantomjs-2.1.1-macosx', 'phantomjs')
        if os.path.isfile('phantomjs.zip'): os.remove('phantomjs.zip')
        os.system('chmod -R 755 phantomjs > /dev/null 2>&1')
        os.chdir(original_directory); return True
    else:
        return True

def coord(x_coordinate = 0, y_coordinate = 0):
    """function to form a coordinate string from x and y integers"""
    return '(' + str(x_coordinate) + ',' + str(y_coordinate) + ')'

def debug(on_off = None):
    """function to set debug mode, eg print debug info"""
    global _tagui_debug
    if on_off is not None: _tagui_debug = on_off
    return _tagui_debug

def tagui_location(location = None):
    """function to set location of TagUI installation"""
    global _tagui_location
    if location is not None: _tagui_location = location
    return _tagui_location

def unzip(file_to_unzip = None, unzip_location = None):
    """function to unzip zip file to specified location"""
    import zipfile

    if file_to_unzip is None or file_to_unzip == '':
        print('[RPA][ERROR] - filename missing for unzip()')
        return False
    elif not os.path.isfile(file_to_unzip):
        print('[RPA][ERROR] - file specified missing for unzip()')
        return False

    zip_file = zipfile.ZipFile(file_to_unzip, 'r')

    if unzip_location is None or unzip_location == '':
        zip_file.extractall()
    else:
        zip_file.extractall(unzip_location)

    zip_file.close()
    return True

def setup():
    """function to setup TagUI to user home folder on Linux / macOS / Windows"""

    # get user home folder location to setup tagui
    home_directory = tagui_location()

    print('[RPA][INFO] - setting up TagUI for use in your Python environment')

    # special check for macOS - download() will fail due to no SSL certs for Python 3
    if platform.system() == 'Darwin' and _python3_env():
        if os.system('/Applications/Python\ 3.9/Install\ Certificates.command > /dev/null 2>&1') != 0:
            if os.system('/Applications/Python\ 3.8/Install\ Certificates.command > /dev/null 2>&1') != 0:
                if os.system('/Applications/Python\ 3.7/Install\ Certificates.command > /dev/null 2>&1') != 0:
                    os.system('/Applications/Python\ 3.6/Install\ Certificates.command > /dev/null 2>&1')

    # set tagui zip filename for respective operating systems
    if platform.system() == 'Linux': tagui_zip_file = 'TagUI_Linux.zip'
    elif platform.system() == 'Darwin': tagui_zip_file = 'TagUI_macOS.zip'
    elif platform.system() == 'Windows': tagui_zip_file = 'TagUI_Windows.zip'
    else:
        print('[RPA][ERROR] - unknown ' + platform.system() + ' operating system to setup TagUI')
        return False
    
    if not os.path.isfile('rpa_python.zip'):
        # primary installation pathway by downloading from internet, requiring internet access
        print('[RPA][INFO] - downloading TagUI (~200MB) and unzipping to below folder...')
        print('[RPA][INFO] - ' + home_directory)

        # set tagui zip download url and download zip for respective operating systems
        tagui_zip_url = 'https://github.com/tebelorg/Tump/releases/download/v1.0.0/' + tagui_zip_file 
        if not download(tagui_zip_url, home_directory + '/' + tagui_zip_file):
            # error message is shown by download(), no need for message here 
            return False

        # unzip downloaded zip file to user home folder
        unzip(home_directory + '/' + tagui_zip_file, home_directory)
        if not os.path.isfile(home_directory + '/' + 'tagui' + '/' + 'src' + '/' + 'tagui'):
            print('[RPA][ERROR] - unable to unzip TagUI to ' + home_directory)
            return False

    else:
        # secondary installation pathway by using the rpa_python.zip generated from pack()
        print('[RPA][INFO] - unzipping TagUI (~200MB) from rpa_python.zip to below folder...')
        print('[RPA][INFO] - ' + home_directory)

        import shutil
        shutil.move('rpa_python.zip', home_directory + '/' + tagui_zip_file)

        if not os.path.isdir(home_directory + '/tagui'): os.mkdir(home_directory + '/tagui')
        unzip(home_directory + '/' + tagui_zip_file, home_directory + '/tagui')
        if not os.path.isfile(home_directory + '/' + 'tagui' + '/' + 'src' + '/' + 'tagui'):
            print('[RPA][ERROR] - unable to unzip TagUI to ' + home_directory)
            return False

    # set correct tagui folder for different operating systems
    if platform.system() == 'Windows':
        tagui_directory = home_directory + '/' + 'tagui'
    else:
        tagui_directory = home_directory + '/' + '.tagui'

        # overwrite tagui to .tagui folder for Linux / macOS

        # first rename existing .tagui folder to .tagui_previous 
        if os.path.isdir(tagui_directory):
            os.rename(tagui_directory, tagui_directory + '_previous')

        # next rename extracted tagui folder (verified earlier) to .tagui
        os.rename(home_directory + '/' + 'tagui', tagui_directory)

        # finally remove .tagui_previous folder if it exists
        if os.path.isdir(tagui_directory + '_previous'):
            import shutil
            shutil.rmtree(tagui_directory + '_previous')

    # after unzip, remove downloaded zip file to save disk space 
    if os.path.isfile(home_directory + '/' + tagui_zip_file):
        os.remove(home_directory + '/' + tagui_zip_file)

    # download stable delta files from tagui cutting edge version
    print('[RPA][INFO] - done. syncing TagUI with stable cutting edge version')
    if not _tagui_delta(tagui_directory): return False

    # perform Linux specific setup actions
    if platform.system() == 'Linux':
        # zipfile extractall does not preserve execute permissions
        # invoking chmod to set all files with execute permissions
        # and update delta tagui/src/tagui with execute permission
        if os.system('chmod -R 755 "' + tagui_directory + '" > /dev/null 2>&1') != 0:
            print('[RPA][ERROR] - unable to set permissions for .tagui folder')
            return False 

        # check that php, a dependency for tagui, is installed and working
        if os.system('php --version > /dev/null 2>&1') != 0:
            print('[RPA][INFO] - PHP is not installed by default on your Linux distribution')
            print('[RPA][INFO] - google how to install PHP (eg for Ubuntu, apt-get install php)')
            print('[RPA][INFO] - after that, TagUI ready for use in your Python environment')
            print('[RPA][INFO] - visual automation (optional) requires special setup on Linux,')
            print('[RPA][INFO] - see the link below to install OpenCV and Tesseract libraries')
            print('[RPA][INFO] - https://sikulix-2014.readthedocs.io/en/latest/newslinux.html')
            return False

        else:
            print('[RPA][INFO] - TagUI now ready for use in your Python environment')
            print('[RPA][INFO] - visual automation (optional) requires special setup on Linux,')
            print('[RPA][INFO] - see the link below to install OpenCV and Tesseract libraries')
            print('[RPA][INFO] - https://sikulix-2014.readthedocs.io/en/latest/newslinux.html')

    # perform macOS specific setup actions
    if platform.system() == 'Darwin':
        # zipfile extractall does not preserve execute permissions
        # invoking chmod to set all files with execute permissions
        # and update delta tagui/src/tagui with execute permission
        if os.system('chmod -R 755 "' + tagui_directory + '" > /dev/null 2>&1') != 0:
            print('[RPA][ERROR] - unable to set permissions for .tagui folder')
            return False

        # patch PhantomJS to solve OpenSSL issue
        if not _patch_macos_pjs(): return False
        print('[RPA][INFO] - TagUI now ready for use in your Python environment')

    # perform Windows specific setup actions
    if platform.system() == 'Windows':
        # check that tagui packaged php is working, it has dependency on MSVCR110.dll
        if os.system('"' + tagui_directory + '/' + 'src' + '/' + 'php/php.exe" -v > nul 2>&1') != 0:
            print('[RPA][INFO] - now installing missing Visual C++ Redistributable dependency')

            # download from hosted setup file, if not already present when deployed using pack()
            if not os.path.isfile(tagui_directory + '/vcredist_x86.exe'):
                vcredist_x86_url = 'https://raw.githubusercontent.com/tebelorg/Tump/master/vcredist_x86.exe'
                if not download(vcredist_x86_url, tagui_directory + '/vcredist_x86.exe'):
                    return False

            # run setup to install the MSVCR110.dll dependency (user action required)
            os.system('"' + tagui_directory + '/vcredist_x86.exe"')
                
            # check again if tagui packaged php is working, after installing vcredist_x86.exe
            if os.system('"' + tagui_directory + '/' + 'src' + '/' + 'php/php.exe" -v > nul 2>&1') != 0:
                print('[RPA][INFO] - MSVCR110.dll is still missing, install vcredist_x86.exe from')
                print('[RPA][INFO] - the vcredist_x86.exe file in ' + home_directory + '\\tagui or from')
                print('[RPA][INFO] - https://www.microsoft.com/en-us/download/details.aspx?id=30679')
                print('[RPA][INFO] - after that, TagUI ready for use in your Python environment')
                return False

            else:
                print('[RPA][INFO] - TagUI now ready for use in your Python environment')

        else:
            print('[RPA][INFO] - TagUI now ready for use in your Python environment')

    return True

def init(visual_automation = False, chrome_browser = True, headless_mode = False):
    """start and connect to tagui process by checking tagui live mode readiness"""

    global _process, _tagui_started, _tagui_id, _tagui_visual, _tagui_chrome, _tagui_init_directory

    if _tagui_started:
        print('[RPA][ERROR] - use close() before using init() again')
        return False

    # reset id to track instruction count from rpa python to tagui
    _tagui_id = 0

    # reset variable to track original directory when init() was called
    _tagui_init_directory = ''

    # get user home folder location to locate tagui executable
    if platform.system() == 'Windows':
        tagui_directory = tagui_location() + '/' + 'tagui'
    else:
        tagui_directory = tagui_location() + '/' + '.tagui'

    tagui_executable = tagui_directory + '/' + 'src' + '/' + 'tagui'
    end_processes_executable = tagui_directory + '/' + 'src' + '/' + 'end_processes'

    # if tagui executable is not found, initiate setup() to install tagui
    if not os.path.isfile(tagui_executable):
        if not setup():
            # error message is shown by setup(), no need for message here
            return False

    # sync tagui delta files for current release if needed
    if not _tagui_delta(tagui_directory): return False

    # on macOS, patch PhantomJS to latest v2.1.1 to solve OpenSSL issue
    if platform.system() == 'Darwin' and not _patch_macos_pjs(): return False

    # create entry flow to launch SikuliX accordingly
    if visual_automation:
        # check for working java jdk for visual automation mode
        if platform.system() == 'Windows':
            shell_silencer = '> nul 2>&1'
        else:
            shell_silencer = '> /dev/null 2>&1'

        # check whether java is installed on the computer
        if os.system('java -version ' + shell_silencer) != 0:
            print('[RPA][INFO] - to use visual automation mode, OpenJDK v8 (64-bit) or later is required')
            print('[RPA][INFO] - download from Amazon Corretto\'s website - https://aws.amazon.com/corretto')
            print('[RPA][INFO] - OpenJDK is preferred over Java JDK which is free for non-commercial use only')
            return False
        else:
            # then check whether it is 64-bit required by sikulix
            os.system('java -version > java_version.txt 2>&1')
            java_version_info = load('java_version.txt').lower()
            os.remove('java_version.txt')
            if '64 bit' not in java_version_info and '64-bit' not in java_version_info:
                print('[RPA][INFO] - to use visual automation mode, OpenJDK v8 (64-bit) or later is required')
                print('[RPA][INFO] - download from Amazon Corretto\'s website - https://aws.amazon.com/corretto')
                print('[RPA][INFO] - OpenJDK is preferred over Java JDK which is free for non-commercial use only')
                return False
            else:
                # start a dummy first run if never run before, to let sikulix integrate jython 
                sikulix_folder = tagui_directory + '/' + 'src' + '/' + 'sikulix'
                if os.path.isfile(sikulix_folder + '/' + 'jython-standalone-2.7.1.jar'):
                    os.system('java -jar "' + sikulix_folder + '/' + 'sikulix.jar" -h ' + shell_silencer)
                _visual_flow()
    else:
        _python_flow()

    # create tagui_local.js for custom functions
    _tagui_local()

    # invoke web browser accordingly with tagui option
    browser_option = ''
    if chrome_browser:
        browser_option = 'chrome'
    if headless_mode:
        browser_option = 'headless'
    
    # entry shell command to invoke tagui process
    tagui_cmd = tagui_executable + ' rpa_python ' + browser_option

    # run tagui end processes script to flush dead processes
    # for eg execution ended with ctrl+c or forget to close()
    os.system('"' + end_processes_executable + '"')

    try:
        # launch tagui using subprocess
        _process = subprocess.Popen(
            tagui_cmd, shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # loop until tagui live mode is ready or tagui process has ended
        while True:

            # failsafe exit if tagui process gets killed for whatever reason
            if _process.poll() is not None:
                print('[RPA][ERROR] - following happens when starting TagUI...')
                print('')
                os.system('"' + tagui_cmd + '"')
                print('')
                _tagui_visual = False
                _tagui_chrome = False
                _tagui_started = False
                return False

            # read next line of output from tagui process live mode interface
            tagui_out = _tagui_read()

            # check that tagui live mode is ready then start listening for inputs
            if 'LIVE MODE - type done to quit' in tagui_out:
                # dummy + start line to clear live mode backspace char before listening
                _tagui_write('echo "[RPA][STARTED]"\n')
                _tagui_write('echo "[RPA][' + str(_tagui_id) + '] - listening for inputs"\n')
                _tagui_visual = visual_automation
                _tagui_chrome = chrome_browser
                _tagui_started = True

                # loop until tagui live mode is ready and listening for inputs
                # also check _tagui_started to handle unexpected termination
                while _tagui_started and not _ready(): pass
                if not _tagui_started:
                    print('[RPA][ERROR] - TagUI process ended unexpectedly')
                    return False

                # remove generated tagui flow, js code and custom functions files
                if os.path.isfile('rpa_python'): os.remove('rpa_python')
                if os.path.isfile('rpa_python.js'): os.remove('rpa_python.js')
                if os.path.isfile('rpa_python.raw'): os.remove('rpa_python.raw')
                if os.path.isfile('tagui_local.js'): os.remove('tagui_local.js')

                # increment id and prepare for next instruction
                _tagui_id = _tagui_id + 1

                # set variable to track original directory when init() was called
                _tagui_init_directory = os.getcwd() 

                return True

    except Exception as e:
        print('[RPA][ERROR] - ' + str(e))
        _tagui_visual = False
        _tagui_chrome = False
        _tagui_started = False
        return False

def pack():
    """function to pack TagUI files for installation on an air-gapped computer without internet"""

    print('[RPA][INFO] - pack() is to deploy RPA for Python to a computer without internet')
    print('[RPA][INFO] - update() is to update an existing installation deployed from pack()')
    print('[RPA][INFO] - detecting and zipping your TagUI installation to rpa_python.zip ...')

    # first make sure TagUI files have been downloaded and synced to latest stable delta files
    global _tagui_started
    if _tagui_started:
        if not close():
            return False
    if not init(False, False):
        return False
    if not close():
        return False

    # next download jython to tagui/src/sikulix folder (after init() it can be moved away)
    if platform.system() == 'Windows':
        tagui_directory = tagui_location() + '/' + 'tagui'
        # pack in Visual C++ MSVCR110.dll dependency from PHP for offline installation 
        vcredist_x86_url = 'https://raw.githubusercontent.com/tebelorg/Tump/master/vcredist_x86.exe'
        if not download(vcredist_x86_url, tagui_directory + '/vcredist_x86.exe'):
            return False
    else:
        tagui_directory = tagui_location() + '/' + '.tagui'
    sikulix_directory = tagui_directory + '/' + 'src' + '/' + 'sikulix'
    sikulix_jython_url = 'https://github.com/tebelorg/Tump/releases/download/v1.0.0/jython-standalone-2.7.1.jar'
    if not download(sikulix_jython_url, sikulix_directory + '/' + 'jython-standalone-2.7.1.jar'):
        return False

    # finally zip entire TagUI installation and save a copy of tagui.py to current folder
    import shutil
    shutil.make_archive('rpa_python', 'zip', tagui_directory)
    shutil.copyfile(os.path.dirname(__file__) + '/tagui.py', 'rpa.py')

    print('[RPA][INFO] - done. copy rpa_python.zip and rpa.py to your target computer.')
    print('[RPA][INFO] - then install and use with import rpa as r followed by r.init()')
    return True

def update():
    """function to update package and TagUI files on an air-gapped computer without internet"""

    print('[RPA][INFO] - pack() is to deploy RPA for Python to a computer without internet')
    print('[RPA][INFO] - update() is to update an existing installation deployed from pack()')
    print('[RPA][INFO] - downloading latest RPA for Python and TagUI files...')

    # first download updated files to rpa_update folder and zip them to rpa_update.zip
    if not os.path.isdir('rpa_update'): os.mkdir('rpa_update')
    if not os.path.isdir('rpa_update/tagui.sikuli'): os.mkdir('rpa_update/tagui.sikuli')

    rpa_python_url = 'https://raw.githubusercontent.com/tebelorg/RPA-Python/master/tagui.py'
    if not download(rpa_python_url, 'rpa_update' + '/' + 'rpa.py'): return False

    # get version number of latest release for the package to use in generated update.py
    rpa_python_py = load('rpa_update' + '/' + 'rpa.py')
    v_front_marker = "__version__ = '"; v_back_marker = "'"
    rpa_python_py = rpa_python_py[rpa_python_py.find(v_front_marker) + len(v_front_marker):]
    rpa_python_py = rpa_python_py[:rpa_python_py.find(v_back_marker)]

    delta_list = ['tagui', 'tagui.cmd', 'end_processes', 'end_processes.cmd',
                    'tagui_header.js', 'tagui_parse.php', 'tagui.sikuli/tagui.py']

    for delta_file in delta_list:
        tagui_delta_url = 'https://raw.githubusercontent.com/tebelorg/Tump/master/TagUI-Python/' + delta_file
        tagui_delta_file = 'rpa_update' + '/' + delta_file
        if not download(tagui_delta_url, tagui_delta_file): return False

    import shutil
    shutil.make_archive('rpa_update', 'zip', 'rpa_update')

    # next define string variables for update.py header and footer to be used in next section
    # indentation formatting has to be removed below, else unwanted indentation added to file
    update_py_header = \
"""import rpa as r
import platform
import base64
import shutil
import os

rpa_update_zip = \\
"""

    update_py_footer = \
"""

# create update.zip from base64 data embedded in update.py
update_zip_file = open('update.zip','wb')
update_zip_file.write(base64.b64decode(rpa_update_zip))
update_zip_file.close()

# unzip update.zip to tagui folder in user home directory
if platform.system() == 'Windows':
    base_directory = os.environ['APPDATA'] + '/tagui'
else:
    base_directory = os.path.expanduser('~') + '/.tagui'

# uncomment below to define and use custom TagUI folder
#base_directory = 'your_full_path'

r.unzip('update.zip', base_directory + '/src')
if os.path.isfile('update.zip'): os.remove('update.zip')

# make sure execute permission is there for Linux / macOS
if platform.system() in ['Linux', 'Darwin']:
    os.system('chmod -R 755 "' + base_directory + '/src/tagui" > /dev/null 2>&1')
    os.system('chmod -R 755 "' + base_directory + '/src/end_processes" > /dev/null 2>&1')

# create marker file to skip syncing for current release
delta_done_file = r._py23_open(base_directory + '/' + 'rpa_python_' + __version__, 'w')
delta_done_file.write(r._py23_write('TagUI installation files used by RPA for Python'))
delta_done_file.close()

# move updated package file rpa.py to package folder
shutil.move(base_directory + '/src/rpa.py', os.path.dirname(r.__file__) + '/rpa.py')
print('[RPA][INFO] - done. RPA for Python updated to version ' + __version__)
"""

    # finally create update.py containing python code and zipped data of update in base64
    try:
        import base64
        dump("__version__ = '" + rpa_python_py + "'\n\n", 'update.py')
        write(update_py_header, 'update.py')
        update_zip_file = open('rpa_update.zip','rb')
        zip_base64_data = (base64.b64encode(update_zip_file.read())).decode('utf-8')
        update_zip_file.close()
        write('"""' + zip_base64_data + '"""', 'update.py')
        write(update_py_footer, 'update.py')

        # remove temporary folder and downloaded files, show result and usage message
        if os.path.isdir('rpa_update'): shutil.rmtree('rpa_update')
        if os.path.isfile('rpa_update.zip'): os.remove('rpa_update.zip')
        print('[RPA][INFO] - done. copy or email update.py to your target computer and run')
        print('[RPA][INFO] - python update.py to update RPA for Python to version ' + rpa_python_py)
        print('[RPA][INFO] - to use custom TagUI folder, set base_directory in update.py')
        return True

    except Exception as e:
        print('[RPA][ERROR] - ' + str(e))
        return False

def _ready():
    """internal function to check if tagui is ready to receive instructions after init() is called"""

    global _process, _tagui_started, _tagui_id, _tagui_visual, _tagui_chrome

    if not _tagui_started:
        # print output error in calling parent function instead
        return False

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if _process.poll() is not None:
            # print output error in calling parent function instead
            _tagui_visual = False
            _tagui_chrome = False
            _tagui_started = False
            return False

        # read next line of output from tagui process live mode interface
        tagui_out = _tagui_read()

        # print to screen debug output that is saved to rpa_python.log
        if debug():
            sys.stdout.write(tagui_out); sys.stdout.flush()

        # check if tagui live mode is listening for inputs and return result
        if tagui_out.strip().startswith('[RPA][') and tagui_out.strip().endswith('] - listening for inputs'):
            return True
        else:
            return False

    except Exception as e:
        print('[RPA][ERROR] - ' + str(e))
        return False

def send(tagui_instruction = None):
    """send next live mode instruction to tagui for processing if tagui is ready"""

    global _process, _tagui_started, _tagui_id, _tagui_visual, _tagui_chrome

    if not _tagui_started:
        print('[RPA][ERROR] - use init() before using send()')
        return False

    if tagui_instruction is None or tagui_instruction == '': return True

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if _process.poll() is not None:
            print('[RPA][ERROR] - no active TagUI process to send()')
            _tagui_visual = False
            _tagui_chrome = False
            _tagui_started = False
            return False

        # escape special characters for them to reach tagui correctly
        tagui_instruction = tagui_instruction.replace('\\','\\\\')
        tagui_instruction = tagui_instruction.replace('\n','\\n')
        tagui_instruction = tagui_instruction.replace('\r','\\r')
        tagui_instruction = tagui_instruction.replace('\t','\\t')
        tagui_instruction = tagui_instruction.replace('\a','\\a')
        tagui_instruction = tagui_instruction.replace('\b','\\b')
        tagui_instruction = tagui_instruction.replace('\f','\\f')

        # special handling for single quote to work with _esq() for tagui
        tagui_instruction = tagui_instruction.replace('[BACKSLASH_QUOTE]','\\\'')

        # escape backslash to display source string correctly after echoing
        echo_safe_instruction = tagui_instruction.replace('\\','\\\\')

        # escape double quote because echo step below uses double quotes 
        echo_safe_instruction = echo_safe_instruction.replace('"','\\"')

        # echo live mode instruction, after preparing string to be echo-safe
        _tagui_write('echo "[RPA][' + str(_tagui_id) + '] - ' + echo_safe_instruction + '"\n')

        # send live mode instruction to be executed
        _tagui_write(tagui_instruction + '\n')

        # echo marker text to prepare for next instruction
        _tagui_write('echo "[RPA][' + str(_tagui_id) + '] - listening for inputs"\n')

        # loop until tagui live mode is ready and listening for inputs
        # also check _tagui_started to handle unexpected termination
        while _tagui_started and not _ready(): pass
        if not _tagui_started:
            print('[RPA][ERROR] - TagUI process ended unexpectedly')
            return False

        # increment id and prepare for next instruction
        _tagui_id = _tagui_id + 1

        return True

    except Exception as e:
        print('[RPA][ERROR] - ' + str(e))
        return False

def close():
    """disconnect from tagui process by sending 'done' trigger instruction"""

    global _process, _tagui_started, _tagui_id, _tagui_visual, _tagui_chrome, _tagui_init_directory

    if not _tagui_started:
        print('[RPA][ERROR] - use init() before using close()')
        return False

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if _process.poll() is not None:
            print('[RPA][ERROR] - no active TagUI process to close()')
            _tagui_visual = False
            _tagui_chrome = False
            _tagui_started = False
            return False

        # send 'done' instruction to terminate live mode and exit tagui
        _tagui_write('echo "[RPA][FINISHED]"\n')
        _tagui_write('done\n')

        # loop until tagui process has closed before returning control
        while _process.poll() is None: pass

        # remove again generated tagui flow, js code and custom functions files
        if os.path.isfile('rpa_python'): os.remove('rpa_python')
        if os.path.isfile('rpa_python.js'): os.remove('rpa_python.js')
        if os.path.isfile('rpa_python.raw'): os.remove('rpa_python.raw')
        if os.path.isfile('tagui_local.js'): os.remove('tagui_local.js')

        # to handle user changing current directory after init() is called
        if os.path.isfile(os.path.join(_tagui_init_directory, 'rpa_python')):
            os.remove(os.path.join(_tagui_init_directory, 'rpa_python'))
        if os.path.isfile(os.path.join(_tagui_init_directory, 'rpa_python.js')):
            os.remove(os.path.join(_tagui_init_directory, 'rpa_python.js'))
        if os.path.isfile(os.path.join(_tagui_init_directory, 'rpa_python.raw')):
            os.remove(os.path.join(_tagui_init_directory, 'rpa_python.raw'))
        if os.path.isfile(os.path.join(_tagui_init_directory, 'tagui_local.js')):
            os.remove(os.path.join(_tagui_init_directory, 'tagui_local.js'))   

        # remove generated tagui log and data files if not in debug mode
        if not debug():
            if os.path.isfile('rpa_python.log'): os.remove('rpa_python.log')
            if os.path.isfile('rpa_python.txt'): os.remove('rpa_python.txt')
        
            # to handle user changing current directory after init() is called
            if os.path.isfile(os.path.join(_tagui_init_directory, 'rpa_python.log')):
                os.remove(os.path.join(_tagui_init_directory, 'rpa_python.log'))
            if os.path.isfile(os.path.join(_tagui_init_directory, 'rpa_python.txt')):
                os.remove(os.path.join(_tagui_init_directory, 'rpa_python.txt'))

        _tagui_visual = False
        _tagui_chrome = False
        _tagui_started = False
        return True

    except Exception as e:
        print('[RPA][ERROR] - ' + str(e))
        _tagui_visual = False
        _tagui_chrome = False
        _tagui_started = False
        return False

def exist(element_identifier = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using exist()')
        return False

    if element_identifier is None or element_identifier == '':
        return False

    # return True for keywords as the computer screen always exists
    if element_identifier.lower() in ['page.png', 'page.bmp']:
        if _visual():
            return True
        else:
            print('[RPA][ERROR] - page.png / page.bmp requires init(visual_automation = True)')
            return False

    # pre-emptive checks if image files are specified for visual automation
    if element_identifier.lower().endswith('.png') or element_identifier.lower().endswith('.bmp'):
        if not _visual():
            print('[RPA][ERROR] - ' + element_identifier + ' identifier requires init(visual_automation = True)')
            return False

    # assume that (x,y) coordinates for visual automation always exist
    if element_identifier.startswith('(') and element_identifier.endswith(')'):
        if len(element_identifier.split(',')) in [2, 3]:
            if not any(c.isalpha() for c in element_identifier):
                if _visual():
                    return True
                else:
                    print('[RPA][ERROR] - x, y coordinates require init(visual_automation = True)')
                    return False

    send('exist_result = exist(\'' + _sdq(element_identifier) + '\').toString()')
    send('dump exist_result to rpa_python.txt')
    if _tagui_output() == 'true':
        return True
    else:
        return False

def url(webpage_url = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using url()')
        return False

    if not _chrome():
        print('[RPA][ERROR] - url() requires init(chrome_browser = True)')
        return False

    if webpage_url is not None and webpage_url != '':
        if webpage_url.lower().startswith('www.'): webpage_url = 'https://' + webpage_url 
        if webpage_url.startswith('http://') or webpage_url.startswith('https://'):
            if not send(_esq(webpage_url)):
                return False
            else:
                return True
        else:
            print('[RPA][ERROR] - URL does not begin with http:// or https:// ')
            return False

    else:
        send('dump url() to rpa_python.txt')
        url_result = _tagui_output()
        return url_result

def click(element_identifier = None, test_coordinate = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using click()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for click()')
        return False

    if test_coordinate is not None and isinstance(test_coordinate, int):
        element_identifier = coord(element_identifier, test_coordinate)

    if not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('click ' + _sdq(element_identifier)):
        return False

    else:
        return True

def rclick(element_identifier = None, test_coordinate = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using rclick()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for rclick()')
        return False

    if test_coordinate is not None and isinstance(test_coordinate, int):
        element_identifier = coord(element_identifier, test_coordinate)

    if not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('rclick ' + _sdq(element_identifier)):
        return False

    else:
        return True

def dclick(element_identifier = None, test_coordinate = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using dclick()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for dclick()')
        return False

    if test_coordinate is not None and isinstance(test_coordinate, int):
        element_identifier = coord(element_identifier, test_coordinate)

    if not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('dclick ' + _sdq(element_identifier)):
        return False

    else:
        return True

def hover(element_identifier = None, test_coordinate = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using hover()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for hover()')
        return False

    if test_coordinate is not None and isinstance(test_coordinate, int):
        element_identifier = coord(element_identifier, test_coordinate)

    if not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('hover ' + _sdq(element_identifier)):
        return False

    else:
        return True

def type(element_identifier = None, text_to_type = None, test_coordinate = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using type()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for type()')
        return False

    if text_to_type is None or text_to_type == '':
        print('[RPA][ERROR] - text missing for type()')
        return False

    if test_coordinate is not None and isinstance(text_to_type, int):
        element_identifier = coord(element_identifier, text_to_type)
        text_to_type = test_coordinate

    if not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('type ' + _sdq(element_identifier) + ' as ' + _esq(text_to_type)):
        return False

    else:
        return True

def select(element_identifier = None, option_value = None, test_coordinate1 = None, test_coordinate2 = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using select()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for select()')
        return False

    if option_value is None or option_value == '':
        print('[RPA][ERROR] - option value missing for select()')
        return False

    if element_identifier.lower() in ['page.png', 'page.bmp'] or option_value.lower() in ['page.png', 'page.bmp']:
        print('[RPA][ERROR] - page.png / page.bmp identifiers invalid for select()')
        return False

    if test_coordinate1 is not None and test_coordinate2 is not None and \
    isinstance(option_value, int) and isinstance(test_coordinate2, int):
        element_identifier = coord(element_identifier, option_value)
        option_value = coord(test_coordinate1, test_coordinate2) 

    # pre-emptive checks if image files are specified for visual automation
    if element_identifier.lower().endswith('.png') or element_identifier.lower().endswith('.bmp'):
        if not _visual():
            print('[RPA][ERROR] - ' + element_identifier + ' identifier requires init(visual_automation = True)')
            return False

    if option_value.lower().endswith('.png') or option_value.lower().endswith('.bmp'):
        if not _visual():
            print('[RPA][ERROR] - ' + option_value + ' identifier requires init(visual_automation = True)')
            return False

    if not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('select ' + _sdq(element_identifier) + ' as ' + _esq(option_value)):
        return False

    else:
        return True

def read(element_identifier = None, test_coordinate1 = None, test_coordinate2 = None, test_coordinate3 = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using read()')
        return ''

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for read()')
        return ''

    if test_coordinate1 is not None and isinstance(test_coordinate1, int):
        if test_coordinate2 is not None and isinstance(test_coordinate2, int):
            if test_coordinate3 is not None and isinstance(test_coordinate3, int):
                element_identifier = coord(element_identifier, test_coordinate1) + '-'
                element_identifier = element_identifier + coord(test_coordinate2, test_coordinate3)

    if element_identifier.lower() != 'page' and not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return ''

    else:
        send('read ' + _sdq(element_identifier) + ' to read_result')
        send('dump read_result to rpa_python.txt')
        read_result = _tagui_output()
        return read_result

def snap(element_identifier = None, filename_to_save = None, test_coord1 = None, test_coord2 = None, test_coord3 = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using snap()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for snap()')
        return False

    if filename_to_save is None or filename_to_save == '':
        print('[RPA][ERROR] - filename missing for snap()')
        return False

    if test_coord2 is not None and test_coord3 is None:
        print('[RPA][ERROR] - filename missing for snap()')
        return False

    if isinstance(element_identifier, int) and isinstance(filename_to_save, int):
        if test_coord1 is not None and isinstance(test_coord1, int):
            if test_coord2 is not None and isinstance(test_coord2, int):
                if test_coord3 is not None and test_coord3 != '':
                    element_identifier = coord(element_identifier, filename_to_save) + '-'
                    element_identifier = element_identifier + coord(test_coord1, test_coord2)
                    filename_to_save = test_coord3

    if element_identifier.lower() != 'page' and not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('snap ' + _sdq(element_identifier) + ' to ' + _esq(filename_to_save)):
        return False

    else:
        return True

def load(filename_to_load = None):
    if filename_to_load is None or filename_to_load == '':
        print('[RPA][ERROR] - filename missing for load()')
        return ''

    elif not os.path.isfile(filename_to_load):
        print('[RPA][ERROR] - cannot load file ' + filename_to_load)
        return ''

    else:
        load_input_file = _py23_open(filename_to_load, 'r')
        load_input_file_text = _py23_read(load_input_file.read())
        load_input_file.close()
        return load_input_file_text

def echo(text_to_echo = ''):
    print(text_to_echo)
    return True

def dump(text_to_dump = None, filename_to_save = None):
    if text_to_dump is None:
        print('[RPA][ERROR] - text missing for dump()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[RPA][ERROR] - filename missing for dump()')
        return False

    else:
        dump_output_file = _py23_open(filename_to_save, 'w')
        dump_output_file.write(_py23_write(text_to_dump))
        dump_output_file.close()
        return True

def write(text_to_write = None, filename_to_save = None):
    if text_to_write is None:
        print('[RPA][ERROR] - text missing for write()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[RPA][ERROR] - filename missing for write()')
        return False

    else:
        write_output_file = _py23_open(filename_to_save, 'a')
        write_output_file.write(_py23_write(text_to_write))
        write_output_file.close()
        return True

def ask(text_to_prompt = ''):
    if _chrome():
        return dom("return prompt('" + _esq(text_to_prompt) + "')")

    else:
        if text_to_prompt == '':
            space_padding = ''
        else:
            space_padding = ' '

        if _python2_env():
            return raw_input(text_to_prompt + space_padding)
        else:
            return input(text_to_prompt + space_padding)

def keyboard(keys_and_modifiers = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using keyboard()')
        return False

    if keys_and_modifiers is None or keys_and_modifiers == '':
        print('[RPA][ERROR] - keys to type missing for keyboard()')
        return False

    if not _visual():
        print('[RPA][ERROR] - keyboard() requires init(visual_automation = True)')
        return False

    elif not send('keyboard ' + _esq(keys_and_modifiers)):
        return False

    else:
        return True

def mouse(mouse_action = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using mouse()')
        return False

    if mouse_action is None or mouse_action == '':
        print('[RPA][ERROR] - \'down\' / \'up\' missing for mouse()')
        return False

    if not _visual():
        print('[RPA][ERROR] - mouse() requires init(visual_automation = True)')
        return False

    elif mouse_action.lower() != 'down' and mouse_action.lower() != 'up':
        print('[RPA][ERROR] - \'down\' / \'up\' missing for mouse()')
        return False

    elif not send('mouse ' + mouse_action):
        return False

    else:
        return True

def table(element_identifier = None, filename_to_save = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using table()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for table()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[RPA][ERROR] - filename missing for table()')
        return False

    elif not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('table ' + _sdq(element_identifier) + ' to ' + _esq(filename_to_save)):
        return False

    else:
        return True

def wait(delay_in_seconds = 5.0):
    time.sleep(float(delay_in_seconds)); return True

def check(condition_to_check = None, text_if_true = '', text_if_false = ''):
    if condition_to_check is None:
        print('[RPA][ERROR] - condition missing for check()')
        return False

    if condition_to_check:
        print(text_if_true)

    else:
        print(text_if_false)

    return True

def upload(element_identifier = None, filename_to_upload = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using upload()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[RPA][ERROR] - target missing for upload()')
        return False

    elif filename_to_upload is None or filename_to_upload == '':
        print('[RPA][ERROR] - filename missing for upload()')
        return False

    elif not exist(element_identifier):
        print('[RPA][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('upload ' + _sdq(element_identifier) + ' as ' + _esq(filename_to_upload)):
        return False

    else:
        return True

def download(download_url = None, filename_to_save = None):
    """function for python 2/3 compatible file download from url"""

    if download_url is None or download_url == '':
        print('[RPA][ERROR] - download URL missing for download()')
        return False

    # if not given, use last part of url as filename to save
    if filename_to_save is None or filename_to_save == '':
        download_url_tokens = download_url.split('/')
        filename_to_save = download_url_tokens[-1]

    # delete existing file if exist to ensure freshness
    if os.path.isfile(filename_to_save):
        os.remove(filename_to_save)

    # handle case where url is invalid or has no content
    try:
        if _python2_env():
            import urllib; urllib.urlretrieve(download_url, filename_to_save)
        else:
            import urllib.request; urllib.request.urlretrieve(download_url, filename_to_save)

    except Exception as e:
        print('[RPA][ERROR] - failed downloading from ' + download_url + '...')
        print(str(e))
        return False

    # take the existence of downloaded file as success
    if os.path.isfile(filename_to_save):
        return True

    else:
        print('[RPA][ERROR] - failed downloading to ' + filename_to_save)
        return False

def frame(main_frame = None, sub_frame = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using frame()')
        return False

    if not _chrome():
        print('[RPA][ERROR] - frame() requires init(chrome_browser = True)')
        return False

    # reset webpage context to document root, by sending custom tagui javascript code
    send('js chrome_step("Runtime.evaluate", {expression: "mainframe_context = null"})')
    send('js chrome_step("Runtime.evaluate", {expression: "subframe_context = null"})')
    send('js chrome_context = "document"; frame_step_offset_x = 0; frame_step_offset_y = 0;')

    # return True if no parameter, after resetting webpage context above
    if main_frame is None or main_frame == '':
        return True

    # set webpage context to main frame specified, by sending custom tagui javascript code
    frame_identifier = '(//frame|//iframe)[@name="' + main_frame + '" or @id="' + main_frame + '"]'
    if not exist(frame_identifier):
        print('[RPA][ERROR] - cannot find frame with @name or @id as \'' + main_frame + '\'')
        return False

    send('js new_context = "mainframe_context"')
    send('js frame_xpath = \'(//frame|//iframe)[@name="' + main_frame + '" or @id="' + main_frame + '"]\'')
    send('js frame_rect = chrome.getRect(xps666(frame_xpath))')
    send('js frame_step_offset_x = frame_rect.left; frame_step_offset_y = frame_rect.top;')
    send('js chrome_step("Runtime.evaluate", {expression: new_context + " = document.evaluate(\'" + frame_xpath + "\'," + chrome_context + ",null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null).snapshotItem(0).contentDocument"})')
    send('js chrome_context = new_context')

    # set webpage context to sub frame if specified, by sending custom tagui javascript code
    if sub_frame is not None and sub_frame != '':
        frame_identifier = '(//frame|//iframe)[@name="' + sub_frame + '" or @id="' + sub_frame + '"]'
        if not exist(frame_identifier):
            print('[RPA][ERROR] - cannot find sub frame with @name or @id as \'' + sub_frame + '\'')
            return False

        send('js new_context = "subframe_context"')
        send('js frame_xpath = \'(//frame|//iframe)[@name="' + sub_frame + '" or @id="' + sub_frame + '"]\'')
        send('js frame_rect = chrome.getRect(xps666(frame_xpath))')
        send('js frame_step_offset_x = frame_rect.left; frame_step_offset_y = frame_rect.top;')
        send('js chrome_step("Runtime.evaluate", {expression: new_context + " = document.evaluate(\'" + frame_xpath + "\'," + chrome_context + ",null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null).snapshotItem(0).contentDocument"})')
        send('js chrome_context = new_context')

    return True

def popup(string_in_url = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using popup()')
        return False

    if not _chrome():
        print('[RPA][ERROR] - popup() requires init(chrome_browser = True)')
        return False

    # reset webpage context to main page, by sending custom tagui javascript code
    send('js if (chrome_targetid !== "") {found_targetid = chrome_targetid; chrome_targetid = ""; chrome_step("Target.detachFromTarget", {sessionId: found_targetid});}')

    # return True if no parameter, after resetting webpage context above
    if string_in_url is None or string_in_url == '':
        return True

    # set webpage context to the popup tab specified, by sending custom tagui javascript code 
    send('js found_targetid = ""; chrome_targets = []; ws_message = chrome_step("Target.getTargets", {});')
    send('js try {ws_json = JSON.parse(ws_message); if (ws_json.result.targetInfos) chrome_targets = ws_json.result.targetInfos; else chrome_targets = [];} catch (e) {chrome_targets = [];}')
    send('js chrome_targets.forEach(function(target) {if (target.url.indexOf("' + string_in_url + '") !== -1) found_targetid = target.targetId;})')
    send('js if (found_targetid !== "") {ws_message = chrome_step("Target.attachToTarget", {targetId: found_targetid}); try {ws_json = JSON.parse(ws_message); if (ws_json.result.sessionId !== "") found_targetid = ws_json.result.sessionId; else found_targetid = "";} catch (e) {found_targetid = "";}}')
    send('js chrome_targetid = found_targetid')

    # check if chrome_targetid is successfully set to sessionid of popup tab
    send('dump chrome_targetid to rpa_python.txt')
    popup_result = _tagui_output()
    if popup_result != '':
        return True
    else:
        print('[RPA][ERROR] - cannot find popup tab containing URL string \'' + string_in_url + '\'')
        return False

def api(url_to_query = None):
    print('[RPA][INFO] - although TagUI supports calling APIs with headers and body,')
    print('[RPA][INFO] - recommend using requests package with lots of online docs')
    return True

def run(command_to_run = None):
    if command_to_run is None or command_to_run == '':
        print('[RPA][ERROR] - command(s) missing for run()')
        return ''

    else:
        if platform.system() == 'Windows':
            command_delimiter = ' & '
        else:
            command_delimiter = '; '
        return _py23_decode(subprocess.check_output(
            command_to_run + command_delimiter + 'exit 0',
            stderr=subprocess.STDOUT,
            shell=True))

def dom(statement_to_run = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using dom()')
        return ''

    if statement_to_run is None or statement_to_run == '':
        print('[RPA][ERROR] - statement(s) missing for dom()')
        return ''

    if not _chrome():
        print('[RPA][ERROR] - dom() requires init(chrome_browser = True)')
        return ''

    else:
        send('dom ' + statement_to_run)
        send('dump dom_result to rpa_python.txt')
        dom_result = _tagui_output()
        return dom_result

def vision(command_to_run = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using vision()')
        return False

    if command_to_run is None or command_to_run == '':
        print('[RPA][ERROR] - command(s) missing for vision()')
        return False

    if not _visual():
        print('[RPA][ERROR] - vision() requires init(visual_automation = True)')
        return False

    elif not send('vision ' + command_to_run):
        return False

    else:
        return True  

def timeout(timeout_in_seconds = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using timeout()')
        return False

    global _tagui_timeout

    if timeout_in_seconds is None:
        return float(_tagui_timeout)

    else:
        _tagui_timeout = float(timeout_in_seconds)

    if not send('timeout ' + str(timeout_in_seconds)):
        return False

    else:
        return True

def present(element_identifier = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using present()')
        return False

    if element_identifier is None or element_identifier == '':
        return False

    # return True for keywords as the computer screen is always present
    if element_identifier.lower() in ['page.png', 'page.bmp']:
        if _visual():
            return True
        else:
            print('[RPA][ERROR] - page.png / page.bmp requires init(visual_automation = True)')
            return False

    # pre-emptive checks if image files are specified for visual automation
    if element_identifier.lower().endswith('.png') or element_identifier.lower().endswith('.bmp'):
        if not _visual():
            print('[RPA][ERROR] - ' + element_identifier + ' identifier requires init(visual_automation = True)')
            return False

    # assume that (x,y) coordinates for visual automation always exist
    if element_identifier.startswith('(') and element_identifier.endswith(')'):
        if len(element_identifier.split(',')) in [2, 3]:
            if not any(c.isalpha() for c in element_identifier):
                if _visual():
                    return True
                else:
                    print('[RPA][ERROR] - x, y coordinates require init(visual_automation = True)')
                    return False

    send('present_result = present(\'' + _sdq(element_identifier) + '\').toString()')
    send('dump present_result to rpa_python.txt')
    if _tagui_output() == 'true':
        return True
    else:
        return False

def count(element_identifier = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using count()')
        return int(0)

    if element_identifier is None or element_identifier == '':
        return int(0)

    if not _chrome():
        print('[RPA][ERROR] - count() requires init(chrome_browser = True)')
        return int(0)

    send('count_result = count(\'' + _sdq(element_identifier) + '\').toString()')
    send('dump count_result to rpa_python.txt')
    return int(_tagui_output())

def title():
    if not _started():
        print('[RPA][ERROR] - use init() before using title()')
        return ''

    if not _chrome():
        print('[RPA][ERROR] - title() requires init(chrome_browser = True)')
        return ''

    send('dump title() to rpa_python.txt')
    title_result = _tagui_output()
    return title_result

def text():
    if not _started():
        print('[RPA][ERROR] - use init() before using text()')
        return ''

    if not _chrome():
        print('[RPA][ERROR] - text() requires init(chrome_browser = True)')
        return ''

    send('dump text() to rpa_python.txt')
    text_result = _tagui_output()
    return text_result

def timer():
    if not _started():
        print('[RPA][ERROR] - use init() before using timer()')
        return float(0)

    send('dump timer() to rpa_python.txt')
    timer_result = _tagui_output()
    return float(timer_result)

def mouse_xy():
    if not _started():
        print('[RPA][ERROR] - use init() before using mouse_xy()')
        return ''

    if not _visual():
        print('[RPA][ERROR] - mouse_xy() requires init(visual_automation = True)')
        return ''

    send('dump mouse_xy() to rpa_python.txt')
    mouse_xy_result = _tagui_output()
    return mouse_xy_result

def mouse_x():
    if not _started():
        print('[RPA][ERROR] - use init() before using mouse_x()')
        return int(0)

    if not _visual():
        print('[RPA][ERROR] - mouse_x() requires init(visual_automation = True)')
        return int(0)

    send('dump mouse_x() to rpa_python.txt')
    mouse_x_result = _tagui_output()
    return int(mouse_x_result)

def mouse_y():
    if not _started():
        print('[RPA][ERROR] - use init() before using mouse_y()')
        return int(0)

    if not _visual():
        print('[RPA][ERROR] - mouse_y() requires init(visual_automation = True)')
        return int(0)

    send('dump mouse_y() to rpa_python.txt')
    mouse_y_result = _tagui_output()
    return int(mouse_y_result)

def clipboard(text_to_put = None):
    if not _started():
        print('[RPA][ERROR] - use init() before using clipboard()')
        return False

    if not _visual():
        print('[RPA][ERROR] - clipboard() requires init(visual_automation = True)')
        return False

    if text_to_put is None:
        send('dump clipboard() to rpa_python.txt')
        clipboard_result = _tagui_output()
        return clipboard_result

    elif not send("js clipboard('" + text_to_put.replace("'",'[BACKSLASH_QUOTE]') + "')"):
        return False

    else:
        return True
