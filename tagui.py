"""INTEGRATION ENGINE FOR TAGUI PYTHON PACKAGE ~ TEBEL.ORG"""
__author__ = 'Ken Soh <opensource@tebel.org>'
__version__ = '1.1.0'

import subprocess
import os
import sys
import time
import platform

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

# id to track instruction count from tagui python to tagui
_tagui_id = 0

# delete tagui temp output text file to avoid reading old data 
if os.path.isfile('tagui_python.txt'): os.remove('tagui_python.txt')

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
    global _tagui_delay
    # sleep to not splurge cpu cycles in while loop
    while not os.path.isfile('tagui_python.txt'):
        time.sleep(_tagui_delay) 

    tagui_output_file = open('tagui_python.txt', 'r')
    tagui_output_text = tagui_output_file.read()
    tagui_output_file.close()
    os.remove('tagui_python.txt')
    return tagui_output_text

def _esq(input_text = ''):
    """function to escape single quote ' for tagui live mode"""
    # ie change ' to be `"\'"` which becomes '+"\'"+' in tagui
    # "[BACKSLASH_QUOTE]" used in interim to work with send()
    return input_text.replace("'",'`"[BACKSLASH_QUOTE]"`')

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
    flow_text = '// NORMAL ENTRY FLOW FOR TAGUI PYTHON PACKAGE ~ TEBEL.ORG\r\n\r\nlive'
    flow_file = open('tagui_python', 'w')
    flow_file.write(flow_text)
    flow_file.close()

def _visual_flow():
    """function to create entry tagui flow with visual automation"""
    flow_text = '// VISUAL ENTRY FLOW FOR TAGUI PYTHON PACKAGE ~ TEBEL.ORG\r\n' + \
                '// mouse_xy() - dummy trigger for SikuliX integration\r\n\r\nlive'
    flow_file = open('tagui_python', 'w')
    flow_file.write(flow_text)
    flow_file.close()

def _tagui_local():
    """function to create tagui_local.js for custom local functions"""
    global _tagui_local_js
    javascript_file = open('tagui_local.js', 'w')
    javascript_file.write(_tagui_local_js)
    javascript_file.close()

def coord(x_coordinate = 0, y_coordinate = 0):
    """function to form a coordinate string from x and y integers"""
    return '(' + str(x_coordinate) + ',' + str(y_coordinate) + ')'

def debug(on_off = None):
    """function to set debug mode, eg print debug info"""
    global _tagui_debug
    if on_off is not None: _tagui_debug = on_off
    return _tagui_debug

def unzip(file_to_unzip = None, unzip_location = None):
    """function to unzip zip file to specified location"""
    import zipfile

    if file_to_unzip is None or file_to_unzip == '':
        print('[TAGUI][ERROR] - filename missing for unzip()')
        return False
    elif not os.path.isfile(file_to_unzip):
        print('[TAGUI][ERROR] - file specified missing for unzip()')
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
    if platform.system() == 'Windows':
        home_directory = os.environ['APPDATA']
    else:
        home_directory = os.path.expanduser('~')

    print('[TAGUI][INFO] - setting up TagUI for use in your Python environment')

    # set tagui zip filename for respective operating systems
    if platform.system() == 'Linux': tagui_zip_file = 'TagUI_Linux.zip'
    elif platform.system() == 'Darwin': tagui_zip_file = 'TagUI_macOS.zip'
    elif platform.system() == 'Windows': tagui_zip_file = 'TagUI_Windows.zip'
    else:
        print('[TAGUI][ERROR] - unknown ' + platform.system() + ' operating system to setup TagUI')
        return False

    print('[TAGUI][INFO] - downloading TagUI (~200MB) and unzipping to below folder...')
    print('[TAGUI][INFO] - ' + home_directory)

    # set tagui zip download url and download zip for respective operating systems
    tagui_zip_url = 'https://github.com/tebelorg/Tump/releases/download/v1.0.0/' + tagui_zip_file 
    if not download(tagui_zip_url, home_directory + '/' + tagui_zip_file):
        # error message is shown by download(), no need for message here 
        return False

    # unzip downloaded zip file to user home folder
    unzip(home_directory + '/' + tagui_zip_file, home_directory)
    if not os.path.isfile(home_directory + '/' + 'tagui' + '/' + 'src' + '/' + 'tagui'):
        print('[TAGUI][ERROR] - unable to unzip TagUI to ' + home_directory)
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
    print('[TAGUI][INFO] - done. syncing TagUI with stable cutting edge version')
    delta_list = ['tagui', 'tagui.cmd', 'tagui_header.js', 'tagui_parse.php']
    for delta_file in delta_list:
        tagui_delta_url = 'https://raw.githubusercontent.com/tebelorg/Tump/master/TagUI-Python/' + delta_file
        tagui_delta_file = tagui_directory + '/' + 'src' + '/' + delta_file
        if not download(tagui_delta_url, tagui_delta_file): return False

    # perform Linux specific setup actions
    if platform.system() == 'Linux':
        # zipfile extractall does not preserve execute permissions
        # invoking chmod to set all files with execute permissions
        # and update delta tagui/src/tagui with execute permission
        if os.system('chmod -R 755 ' + tagui_directory + ' > /dev/null 2>&1') != 0:
            print('[TAGUI][ERROR] - unable to set permissions for .tagui folder')
            return False 

        # check that php, a dependency for tagui, is installed and working
        if os.system('php --version > /dev/null 2>&1') != 0:
            print('[TAGUI][INFO] - PHP is not installed by default on your Linux distribution')
            print('[TAGUI][INFO] - google how to install PHP (eg for Ubuntu, apt-get install php)')
            print('[TAGUI][INFO] - after that, TagUI ready for use in your Python environment')
            return False

        else:
            print('[TAGUI][INFO] - TagUI now ready for use in your Python environment')

    # perform macOS specific setup actions
    if platform.system() == 'Darwin':
        # zipfile extractall does not preserve execute permissions
        # invoking chmod to set all files with execute permissions
        # and update delta tagui/src/tagui with execute permission
        if os.system('chmod -R 755 ' + tagui_directory + ' > /dev/null 2>&1') != 0:
            print('[TAGUI][ERROR] - unable to set permissions for .tagui folder')
            return False

        # check for openssl, a dependency of phantomjs removed in newer macOS
        if not os.path.isfile('/usr/local/opt/openssl/lib/libssl.1.0.0.dylib'):

            # if openssl is missing, first attempt to install using homebrew
            os.system('brew install openssl > /dev/null 2>&1')

            # if it is still missing, attempt again by first installing homebrew
            if not os.path.isfile('/usr/local/opt/openssl/lib/libssl.1.0.0.dylib'):
                print('')
                print('[TAGUI][INFO] - now installing OpenSSL dependency using Homebrew')
                print('[TAGUI][INFO] - you may be prompted for login password to continue')
                print('')
                os.system('echo | /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"')
                os.system('brew install openssl')

                # if it is still missing, prompt user to install homebrew and openssl
                if not os.path.isfile('/usr/local/opt/openssl/lib/libssl.1.0.0.dylib'):
                    print('[TAGUI][INFO] - OpenSSL was not able to be installed automatically')
                    print('[TAGUI][INFO] - run below 2 commands in your terminal to install manually')
                    print('[TAGUI][INFO] - after that, TagUI ready for use in your Python environment')
                    print('')
                    print('/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"')
                    print('brew install openssl')
                    print('')
                    return False

                else:
                    print('[TAGUI][INFO] - TagUI now ready for use in your Python environment')

            else:
                print('[TAGUI][INFO] - TagUI now ready for use in your Python environment')

        else:
            print('[TAGUI][INFO] - TagUI now ready for use in your Python environment')

    # perform Windows specific setup actions
    if platform.system() == 'Windows':
        # check that tagui packaged php is working, it has dependency on MSVCR110.dll
        if os.system(tagui_directory + '/' + 'src' + '/' + 'php/php.exe -v > nul 2>&1') != 0:
            print('[TAGUI][INFO] - now installing missing Visual C++ Redistributable dependency')
            vcredist_x86_url = 'https://raw.githubusercontent.com/tebelorg/Tump/master/vcredist_x86.exe'
            if download(vcredist_x86_url, tagui_directory + '/vcredist_x86.exe'):
                os.system(tagui_directory + '/vcredist_x86.exe')

            # check again if tagui packaged php is working, after installing vcredist_x86.exe
            if os.system(tagui_directory + '/' + 'src' + '/' + 'php/php.exe -v > nul 2>&1') != 0:
                print('[TAGUI][INFO] - MSVCR110.dll is still missing, install vcredist_x86.exe from')
                print('[TAGUI][INFO] - https://www.microsoft.com/en-us/download/details.aspx?id=30679')
                print('[TAGUI][INFO] - after that, TagUI ready for use in your Python environment')
                return False

            else:
                print('[TAGUI][INFO] - TagUI now ready for use in your Python environment')

        else:
            print('[TAGUI][INFO] - TagUI now ready for use in your Python environment')

    return True

def init(visual_automation = False, chrome_browser = True):
    """start and connect to tagui process by checking tagui live mode readiness"""

    global _process, _tagui_started, _tagui_id, _tagui_visual, _tagui_chrome

    if _tagui_started:
        print('[TAGUI][ERROR] - use close() before using init() again')
        return False

    # reset id to track instruction count from tagui python to tagui
    _tagui_id = 0

    # get user home folder location to locate tagui executable
    if platform.system() == 'Windows':
        tagui_directory = os.environ['APPDATA'] + '/' + 'tagui'
    else:
        tagui_directory = os.path.expanduser('~') + '/' + '.tagui'

    tagui_executable = tagui_directory + '/' + 'src' + '/' + 'tagui'

    # if tagui executable is not found, initiate setup() to install tagui
    if not os.path.isfile(tagui_executable):
        if not setup():
            # error message is shown by setup(), no need for message here
            return False

    # create entry flow to launch SikuliX accordingly
    if visual_automation:
        # check for working java jdk for visual automation mode
        if platform.system() == 'Windows':
            shell_silencer = '> nul 2>&1'
        else:
            shell_silencer = '> /dev/null 2>&1'

        if os.system('java -version ' + shell_silencer) != 0:
            print('[TAGUI][INFO] - for visual automation mode, Java JDK v8 (64-bit) or later is required')
            print('[TAGUI][INFO] - to use visual automation feature, download Java JDK v8 (64-bit) from below')
            print('[TAGUI][INFO] - https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html')
            return False
        else:
            # start a dummy first run if never run before, to let sikulix integrate jython 
            sikulix_folder = tagui_directory + '/' + 'src' + '/' + 'sikulix'
            if os.path.isfile(sikulix_folder + '/' + 'jython-standalone-2.7.1.jar'):
                os.system('java -jar ' + sikulix_folder + '/' + 'sikulix.jar -h ' + shell_silencer)
            _visual_flow()
    else:
        _python_flow()

    # create tagui_local.js for custom functions
    _tagui_local()

    # invoke web browser accordingly with tagui option
    browser_option = ''
    if chrome_browser:
        browser_option = 'chrome'
    
    # entry shell command to invoke tagui process
    tagui_cmd = tagui_executable + ' tagui_python ' + browser_option
    
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
                print('[TAGUI][ERROR] - following happens when starting TagUI...')
                print('')
                os.system(tagui_cmd)
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
                _tagui_write('echo "[TAGUI][STARTED]"\n')
                _tagui_write('echo "[TAGUI][' + str(_tagui_id) + '] - listening for inputs"\n')
                _tagui_visual = visual_automation
                _tagui_chrome = chrome_browser
                _tagui_started = True

                # loop until tagui live mode is ready and listening for inputs
                # also check _tagui_started to handle unexpected termination
                while _tagui_started and not _ready(): pass
                if not _tagui_started:
                    print('[TAGUI][ERROR] - TagUI process ended unexpectedly')
                    return False

                # increment id and prepare for next instruction
                _tagui_id = _tagui_id + 1

                return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        _tagui_visual = False
        _tagui_chrome = False
        _tagui_started = False
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

        # print to screen debug output that is saved to tagui_python.log
        if debug():
            sys.stdout.write(tagui_out); sys.stdout.flush()

        # check if tagui live mode is listening for inputs and return result
        if tagui_out.strip().startswith('[TAGUI][') and tagui_out.strip().endswith('] - listening for inputs'):
            return True
        else:
            return False

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        return False

def send(tagui_instruction = None):
    """send next live mode instruction to tagui for processing if tagui is ready"""

    global _process, _tagui_started, _tagui_id, _tagui_visual, _tagui_chrome

    if not _tagui_started:
        print('[TAGUI][ERROR] - use init() before using send()')
        return False

    if tagui_instruction is None or tagui_instruction == '': return True

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if _process.poll() is not None:
            print('[TAGUI][ERROR] - no active TagUI process to send()')
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
        tagui_instruction = tagui_instruction.replace('"[BACKSLASH_QUOTE]"','"\\\'"')

        # escape backslash to display source string correctly after echoing
        echo_safe_instruction = tagui_instruction.replace('\\','\\\\')

        # escape double quote because echo step below uses double quotes 
        echo_safe_instruction = echo_safe_instruction.replace('"','\\"')

        # echo live mode instruction, after preparing string to be echo-safe
        _tagui_write('echo "[TAGUI][' + str(_tagui_id) + '] - ' + echo_safe_instruction + '"\n')

        # send live mode instruction to be executed
        _tagui_write(tagui_instruction + '\n')

        # echo marker text to prepare for next instruction
        _tagui_write('echo "[TAGUI][' + str(_tagui_id) + '] - listening for inputs"\n')

        # loop until tagui live mode is ready and listening for inputs
        # also check _tagui_started to handle unexpected termination
        while _tagui_started and not _ready(): pass
        if not _tagui_started:
            print('[TAGUI][ERROR] - TagUI process ended unexpectedly')
            return False

        # increment id and prepare for next instruction
        _tagui_id = _tagui_id + 1

        return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        return False

def close():
    """disconnect from tagui process by sending 'done' trigger instruction"""

    global _process, _tagui_started, _tagui_id, _tagui_visual, _tagui_chrome

    if not _tagui_started:
        print('[TAGUI][ERROR] - use init() before using close()')
        return False

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if _process.poll() is not None:
            print('[TAGUI][ERROR] - no active TagUI process to close()')
            _tagui_visual = False
            _tagui_chrome = False
            _tagui_started = False
            return False

        # send 'done' instruction to terminate live mode and exit tagui
        _tagui_write('echo "[TAGUI][FINISHED]"\n')
        _tagui_write('done\n')

        # loop until tagui process has closed before returning control
        while _process.poll() is None: pass

        # remove generated tagui flow, js code and custom functions files
        if os.path.isfile('tagui_python'): os.remove('tagui_python')
        if os.path.isfile('tagui_python.js'): os.remove('tagui_python.js')
        if os.path.isfile('tagui_python.raw'): os.remove('tagui_python.raw')
        if os.path.isfile('tagui_local.js'): os.remove('tagui_local.js')

        # remove generated tagui log and data files if not in debug mode
        if not debug():
            if os.path.isfile('tagui_python.log'): os.remove('tagui_python.log')
            if os.path.isfile('tagui_python.txt'): os.remove('tagui_python.txt')

        _tagui_visual = False
        _tagui_chrome = False
        _tagui_started = False
        return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        _tagui_visual = False
        _tagui_chrome = False
        _tagui_started = False
        return False

def exist(element_identifier = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using exist()')
        return False

    if element_identifier is None or element_identifier == '':
        return False

    # return True for keywords as the computer screen always exists
    if element_identifier.lower() in ['page.png', 'page.bmp']: return True

    # pre-emptive check for existence of specified image file for visual automation
    if element_identifier.lower().endswith('.png') or element_identifier.lower().endswith('.bmp'):
        if not os.path.isfile(element_identifier):
            print('[TAGUI][ERROR] - missing image file ' + element_identifier)
            return False
        elif not _visual():
            print('[TAGUI][ERROR] - ' + element_identifier + ' identifier requires init(visual_automation = True)')
            return False

    # assume that (x,y) coordinates for visual automation always exist
    if element_identifier.startswith('(') and element_identifier.endswith(')'):
        if len(element_identifier.split(',')) == 2:
            if not any(c.isalpha() for c in element_identifier):
                if _visual():
                    return True
                else:
                    print('[TAGUI][ERROR] - x, y coordinates require init(visual_automation = True)')
                    return False

    send('exist_result = exist(\'' + _sdq(element_identifier) + '\').toString()')
    send('dump exist_result to tagui_python.txt')
    if _tagui_output() == 'true':
        return True
    else:
        return False

def url(webpage_url = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using url()')
        return False

    if not _chrome():
        print('[TAGUI][ERROR] - url() requires init(chrome_browser = True)')
        return False

    if webpage_url is not None and webpage_url != '':
        if webpage_url.startswith('http://') or webpage_url.startswith('https://'):
            if not send(_esq(webpage_url)):
                return False
            else:
                return True
        else:
            print('[TAGUI][ERROR] - URL does not begin with http:// or https:// ')
            return False

    else:
        send('dump url() to tagui_python.txt')
        url_result = _tagui_output()
        return url_result

def click(element_identifier = None, test_coordinate = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using click()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for click()')
        return False

    if test_coordinate is not None and isinstance(test_coordinate, int):
        element_identifier = coord(element_identifier, test_coordinate)

    if not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('click ' + _sdq(element_identifier)):
        return False

    else:
        return True

def rclick(element_identifier = None, test_coordinate = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using rclick()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for rclick()')
        return False

    if test_coordinate is not None and isinstance(test_coordinate, int):
        element_identifier = coord(element_identifier, test_coordinate)

    if not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('rclick ' + _sdq(element_identifier)):
        return False

    else:
        return True

def dclick(element_identifier = None, test_coordinate = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using dclick()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for dclick()')
        return False

    if test_coordinate is not None and isinstance(test_coordinate, int):
        element_identifier = coord(element_identifier, test_coordinate)

    if not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('dclick ' + _sdq(element_identifier)):
        return False

    else:
        return True

def hover(element_identifier = None, test_coordinate = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using hover()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for hover()')
        return False

    if test_coordinate is not None and isinstance(test_coordinate, int):
        element_identifier = coord(element_identifier, test_coordinate)

    if not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('hover ' + _sdq(element_identifier)):
        return False

    else:
        return True

def type(element_identifier = None, text_to_type = None, test_coordinate = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using type()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for type()')
        return False

    if text_to_type is None or text_to_type == '':
        print('[TAGUI][ERROR] - text missing for type()')
        return False

    if test_coordinate is not None and isinstance(text_to_type, int):
        element_identifier = coord(element_identifier, text_to_type)
        text_to_type = test_coordinate

    if not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('type ' + _sdq(element_identifier) + ' as ' + _esq(text_to_type)):
        return False

    else:
        return True

def select(element_identifier = None, option_value = None, test_coordinate1 = None, test_coordinate2 = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using select()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for select()')
        return False

    if option_value is None or option_value == '':
        print('[TAGUI][ERROR] - option value missing for select()')
        return False

    if element_identifier.lower() in ['page.png', 'page.bmp'] or option_value.lower() in ['page.png', 'page.bmp']:
        print('[TAGUI][ERROR] - page.png and page.bmp invalid for select()')
        return False

    if test_coordinate1 is not None and test_coordinate2 is not None and \
    isinstance(option_value, int) and isinstance(test_coordinate2, int):
        element_identifier = coord(element_identifier, option_value)
        option_value = coord(test_coordinate1, test_coordinate2) 

    # pre-emptive checks if image files are specified for visual automation
    # eg without below checks, a missing image file for option will crash
    if element_identifier.lower().endswith('.png') or element_identifier.lower().endswith('.bmp'):
        if not os.path.isfile(element_identifier):
            print('[TAGUI][ERROR] - missing image file ' + element_identifier)
            return False
        elif not _visual():
            print('[TAGUI][ERROR] - ' + element_identifier + ' identifier requires init(visual_automation = True)')
            return False

    if option_value.lower().endswith('.png') or option_value.lower().endswith('.bmp'):
        if not os.path.isfile(option_value):
            print('[TAGUI][ERROR] - missing image file ' + option_value)
            return False
        elif not _visual():
            print('[TAGUI][ERROR] - ' + option_value + ' identifier requires init(visual_automation = True)')
            return False

    if not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('select ' + _sdq(element_identifier) + ' as ' + _esq(option_value)):
        return False

    else:
        return True

def read(element_identifier = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using read()')
        return ''

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for read()')
        return ''

    elif not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return ''

    else:
        send('read ' + _sdq(element_identifier) + ' to read_result')
        send('dump read_result to tagui_python.txt')
        read_result = _tagui_output()
        return read_result

def show(element_identifier = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using show()')
        return ''

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for show()')
        return ''

    elif not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return ''

    else:
        send('read ' + _sdq(element_identifier) + ' to show_result')
        send('dump show_result to tagui_python.txt')
        show_result = _tagui_output()
        print(show_result)
        return show_result

def save(element_identifier = None, filename_to_save = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using save()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for save()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for save()')
        return False

    elif not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('save ' + _sdq(element_identifier) + ' to ' + _esq(filename_to_save)):
        return False

    else:
        return True

def snap(element_identifier = None, filename_to_save = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using snap()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for snap()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for snap()')
        return False

    elif not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('snap ' + _sdq(element_identifier) + ' to ' + _esq(filename_to_save)):
        return False

    else:
        return True

def load(filename_to_load = None):
    if filename_to_load is None or filename_to_load == '':
        print('[TAGUI][ERROR] - filename missing for load()')
        return ''

    elif not os.path.isfile(filename_to_load):
        print('[TAGUI][ERROR] - cannot load file ' + filename_to_load)
        return ''

    else:
        load_input_file = open(filename_to_load, 'r')
        load_input_file_text = load_input_file.read()
        load_input_file.close()
        return load_input_file_text

def echo(text_to_echo = ''):
    print(text_to_echo)
    return True

def dump(text_to_dump = None, filename_to_save = None):
    if text_to_dump is None:
        print('[TAGUI][ERROR] - text missing for dump()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for dump()')
        return False

    else:
        dump_output_file = open(filename_to_save, 'w')
        dump_output_file.write(text_to_dump)
        dump_output_file.close()
        return True

def write(text_to_write = None, filename_to_save = None):
    if text_to_write is None:
        print('[TAGUI][ERROR] - text missing for write()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for write()')
        return False

    else:
        write_output_file = open(filename_to_save, 'a')
        write_output_file.write(text_to_write)
        write_output_file.close()
        return True

def ask(text_to_prompt = ''):
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
        print('[TAGUI][ERROR] - use init() before using keyboard()')
        return False

    if keys_and_modifiers is None or keys_and_modifiers == '':
        print('[TAGUI][ERROR] - keys to type missing for keyboard()')
        return False

    if not _visual():
        print('[TAGUI][ERROR] - keyboard() requires init(visual_automation = True)')
        return False

    elif not send('keyboard ' + _esq(keys_and_modifiers)):
        return False

    else:
        return True

def mouse(mouse_action = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using mouse()')
        return False

    if mouse_action is None or mouse_action == '':
        print('[TAGUI][ERROR] - \'down\' / \'up\' missing for mouse()')
        return False

    if not _visual():
        print('[TAGUI][ERROR] - mouse() requires init(visual_automation = True)')
        return False

    elif mouse_action.lower() != 'down' and mouse_action.lower() != 'up':
        print('[TAGUI][ERROR] - \'down\' / \'up\' missing for mouse()')
        return False

    elif not send('mouse ' + mouse_action):
        return False

    else:
        return True

def table(element_identifier = None, filename_to_save = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using table()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for table()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for table()')
        return False

    elif not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('table ' + _sdq(element_identifier) + ' to ' + _esq(filename_to_save)):
        return False

    else:
        return True

def wait(delay_in_seconds = 5.0):
    time.sleep(float(delay_in_seconds)); return True

def check(condition_to_check = None, text_if_true = '', text_if_false = ''):
    if condition_to_check is None:
        print('[TAGUI][ERROR] - condition missing for check()')
        return False

    if condition_to_check:
        print(text_if_true)

    else:
        print(text_if_false)

    return True

def upload(element_identifier = None, filename_to_upload = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using upload()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for upload()')
        return False

    elif filename_to_upload is None or filename_to_upload == '':
        print('[TAGUI][ERROR] - filename missing for upload()')
        return False

    elif not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('upload ' + _sdq(element_identifier) + ' as ' + _esq(filename_to_upload)):
        return False

    else:
        return True

def download(download_url = None, filename_to_save = None):
    """function for python 2/3 compatible file download from url"""

    if download_url is None or download_url == '':
        print('[TAGUI][ERROR] - download URL missing for download()')
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
        print('[TAGUI][ERROR] - failed downloading from ' + download_url)
        return False

    # take the existence of downloaded file as success
    if os.path.isfile(filename_to_save):
        return True

    else:
        print('[TAGUI][ERROR] - failed downloading to ' + filename_to_save)
        return False

def api(url_to_query = None):
    print('[TAGUI][INFO] - although TagUI supports calling APIs with headers and body,')
    print('[TAGUI][INFO] - recommend using requests package with lots of online docs')
    return True

def run(command_to_run = None):
    if command_to_run is None or command_to_run == '':
        print('[TAGUI][ERROR] - command(s) missing for run()')
        return ''

    else:
        return _py23_decode(subprocess.check_output(
            command_to_run + '; exit 0',
            stderr=subprocess.STDOUT,
            shell=True))

def dom(statement_to_run = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using dom()')
        return ''

    if statement_to_run is None or statement_to_run == '':
        print('[TAGUI][ERROR] - statement(s) missing for dom()')
        return ''

    if not _chrome():
        print('[TAGUI][ERROR] - dom() requires init(chrome_browser = True)')
        return ''

    else:
        send('dom ' + statement_to_run)
        send('dump dom_result to tagui_python.txt')
        dom_result = _tagui_output()
        return dom_result

def vision(command_to_run = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using vision()')
        return False

    if command_to_run is None or command_to_run == '':
        print('[TAGUI][ERROR] - command(s) missing for vision()')
        return False

    if not _visual():
        print('[TAGUI][ERROR] - vision() requires init(visual_automation = True)')
        return False

    elif not send('vision ' + command_to_run):
        return False

    else:
        return True  

def timeout(timeout_in_seconds = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using timeout()')
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
        print('[TAGUI][ERROR] - use init() before using present()')
        return False

    if element_identifier is None or element_identifier == '':
        return False

    # return True for keywords as the computer screen is always present
    if element_identifier.lower() in ['page.png', 'page.bmp']: return True

    # check for existence of specified image file for visual automation
    if element_identifier.lower().endswith('.png') or element_identifier.lower().endswith('.bmp'):
        if not os.path.isfile(element_identifier):
            print('[TAGUI][ERROR] - missing image file ' + element_identifier)
            return False
        elif not _visual():
            print('[TAGUI][ERROR] - ' + element_identifier + ' identifier requires init(visual_automation = True)')
            return False

    # assume that (x,y) coordinates for visual automation always exist
    if element_identifier.startswith('(') and element_identifier.endswith(')'):
        if len(element_identifier.split(',')) == 2:
            if not any(c.isalpha() for c in element_identifier):
                if _visual():
                    return True
                else:
                    print('[TAGUI][ERROR] - x, y coordinates require init(visual_automation = True)')
                    return False

    send('present_result = present(\'' + _sdq(element_identifier) + '\').toString()')
    send('dump present_result to tagui_python.txt')
    if _tagui_output() == 'true':
        return True
    else:
        return False

def visible(element_identifier = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using visible()')
        return False

    if element_identifier is None or element_identifier == '':
        return False

    # return True for keywords as the computer screen is always visible
    if element_identifier.lower() in ['page.png', 'page.bmp']: return True

    # check for existence of specified image file for visual automation
    if element_identifier.lower().endswith('.png') or element_identifier.lower().endswith('.bmp'):
        if not os.path.isfile(element_identifier):
            print('[TAGUI][ERROR] - missing image file ' + element_identifier)
            return False
        elif not _visual():
            print('[TAGUI][ERROR] - ' + element_identifier + ' identifier requires init(visual_automation = True)')
            return False

    # assume that (x,y) coordinates for visual automation always exist
    if element_identifier.startswith('(') and element_identifier.endswith(')'):
        if len(element_identifier.split(',')) == 2:
            if not any(c.isalpha() for c in element_identifier):
                if _visual():
                    return True
                else:
                    print('[TAGUI][ERROR] - x, y coordinates require init(visual_automation = True)')
                    return False

    send('visible_result = visible(\'' + _sdq(element_identifier) + '\').toString()')
    send('dump visible_result to tagui_python.txt')
    if _tagui_output() == 'true':
        return True
    else:
        return False

def count(element_identifier = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using count()')
        return int(0)

    if element_identifier is None or element_identifier == '':
        return int(0)

    if not _chrome():
        print('[TAGUI][ERROR] - count() requires init(chrome_browser = True)')
        return int(0)

    send('count_result = count(\'' + _sdq(element_identifier) + '\').toString()')
    send('dump count_result to tagui_python.txt')
    return int(_tagui_output())

def title():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using title()')
        return ''

    if not _chrome():
        print('[TAGUI][ERROR] - title() requires init(chrome_browser = True)')
        return ''

    send('dump title() to tagui_python.txt')
    title_result = _tagui_output()
    return title_result

def text():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using text()')
        return ''

    if not _chrome():
        print('[TAGUI][ERROR] - text() requires init(chrome_browser = True)')
        return ''

    send('dump text() to tagui_python.txt')
    text_result = _tagui_output()
    return text_result

def timer():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using timer()')
        return float(0)

    send('dump timer() to tagui_python.txt')
    timer_result = _tagui_output()
    return float(timer_result)

def mouse_xy():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using mouse_xy()')
        return ''

    if not _visual():
        print('[TAGUI][ERROR] - mouse_xy() requires init(visual_automation = True)')
        return ''

    send('dump mouse_xy() to tagui_python.txt')
    mouse_xy_result = _tagui_output()
    return mouse_xy_result

def mouse_x():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using mouse_x()')
        return int(0)

    if not _visual():
        print('[TAGUI][ERROR] - mouse_x() requires init(visual_automation = True)')
        return int(0)

    send('dump mouse_x() to tagui_python.txt')
    mouse_x_result = _tagui_output()
    return int(mouse_x_result)

def mouse_y():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using mouse_y()')
        return int(0)

    if not _visual():
        print('[TAGUI][ERROR] - mouse_y() requires init(visual_automation = True)')
        return int(0)

    send('dump mouse_y() to tagui_python.txt')
    mouse_y_result = _tagui_output()
    return int(mouse_y_result)
