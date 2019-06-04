# INTEGRATION ENGINE FOR TAGUI PYTHON PACKAGE ~ TEBEL.ORG

import subprocess
import os
import sys
import time

# default timeout in seconds for UI element
_tagui_timeout = 10.0

# default delay in seconds in while loops
_tagui_delay = 0.1

# flag to track if tagui session started
_tagui_started = False

# flag to track and print debug info
_tagui_debug = False

# id to track instruction count between tagui-python and tagui
_tagui_id = 0

# delete tagui temp output text file to avoid reading old data 
if os.path.isfile('tagui_python.txt'): os.remove('tagui_python.txt')

def _python2_env():
# function to check python version for compatibility handling
    if sys.version_info[0] < 3: return True
    else: return False

def _python3_env():
# function to check python version for compatibility handling
    return not _python2_env()

def _py23_decode(input_variable = None):
# function for python 2 and 3 str-byte compatibility handling
    if input_variable is None: return None
    elif _python2_env(): return input_variable
    else: return input_variable.decode('utf-8')

def _py23_encode(input_variable = None):
# function for python 2 and 3 str-byte compatibility handling
    if input_variable is None: return None
    elif _python2_env(): return input_variable
    else: return input_variable.encode('utf-8')

def _tagui_read():
# function to read from tagui process live mode interface
    # readline instead of read, not expecting user input to tagui
    global _process; return _py23_decode(_process.stdout.readline())

def _tagui_write(input_text = ''):
# function to write to tagui process live mode interface
    global _process; _process.stdin.write(_py23_encode(input_text))
    _process.stdin.flush(); # flush to ensure immediate delivery

def _tagui_output():
# function to wait for tagui output file to read and delete it
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
# function to escape single quote ' for tagui live mode
# change ' to be `"\'"` which becomes '+"\'"+' in tagui
    return input_text.replace("'",'`"\\\'"`')

def _sdq(input_text = ''):
# function to escape ' in xpath for tagui live mode
# change identifier single quote ' to double quote "
    return input_text.replace("'",'"')

def coord(x_coordinate = None, y_coordinate = None):
# function to form a coordinate string from x and y integers
    return '(' + str(x_coordinate) + ',' + str(y_coordinate) + ')'

def _started():
    global _tagui_started; return _tagui_started

def debug(on_off = None):
# function to set debug mode, eg print debug info
    global _tagui_debug
    if on_off is not None: _tagui_debug = on_off
    return _tagui_debug

def init(debug_mode = False, visual_automation = False):
# connect to tagui process by checking tagui live mode readiness

    global _process, _tagui_started, _tagui_id

    if _tagui_started:
        print('[TAGUI][ERROR] - use close() before using init() again')
        return False

    # set debug mode, eg print debug info to output
    debug(debug_mode)

    # set entry flow to launch SikuliX accordingly
    if visual_automation:
        tagui_flow = 'tagui_visual'
    else:
        tagui_flow = 'tagui_python'

    # entry command to invoke tagui process
    tagui_cmd = 'tagui ' + tagui_flow + ' chrome'
    
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
                _tagui_started = False
                return False

            # read next line of output from tagui process live mode interface
            tagui_out = _tagui_read()

            # check that tagui live mode is ready then start listening for inputs
            if 'LIVE MODE - type done to quit' in tagui_out:
                # print new line to clear live mode backspace character before listening
                _tagui_write('echo ""\n')
                _tagui_write('echo "[TAGUI][STARTED]"\n')
                _tagui_write('echo "[TAGUI][' + str(_tagui_id) + '] - listening for inputs"\n')
                _tagui_started = True
                return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        _tagui_started = False
        return False

def _ready():
# check whether tagui is ready to receive instructions

    global _process, _tagui_started, _tagui_id

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if _process.poll() is not None:
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
# send next live mode instruction to tagui for processing if tagui is ready

    global _process, _tagui_started, _tagui_id

    if not _tagui_started:
        print('[TAGUI][ERROR] - use init() before using send()')
        return False

    if tagui_instruction is None or tagui_instruction == '': return True

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if _process.poll() is not None:
            _tagui_started = False
            return False

        # loop until tagui live mode is ready and listening for inputs
        while not _ready(): pass

        # echo live mode instruction, first escape double quotes to be echo-safe
        safe_tagui_instruction = tagui_instruction.replace('"','\\"')
        _tagui_write('echo "[TAGUI][' + str(_tagui_id) + '] - ' + safe_tagui_instruction + '"\n')

        # send live mode instruction to be executed
        _tagui_write(tagui_instruction + '\n')

        # increment id and prepare for next instruction
        _tagui_id = _tagui_id + 1
        _tagui_write('echo "[TAGUI][' + str(_tagui_id) + '] - listening for inputs"\n')

        return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        return False

def close():
# disconnect from tagui process by sending done instruction

    global _process, _tagui_started, _tagui_id

    if not _tagui_started:
        print('[TAGUI][ERROR] - use init() before using close()')
        _tagui_started = False
        return False

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if _process.poll() is not None:
            _tagui_started = False
            return False

        # loop until tagui live mode is ready and listening for inputs
        while not _ready(): pass

        # send done instruction to terminate live mode and exit tagui
        _tagui_write('echo "[TAGUI][FINISHED]"\n')
        _tagui_write('done\n')

        # loop until tagui process has closed before returning control
        while _process.poll() is None: pass

        _tagui_started = False
        return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        _tagui_started = False
        return False

def exist(element_identifier = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using exist()')
        return False

    if element_identifier is None or element_identifier == '':
        return False

    # check for existence of specified image file for visual automation
    if element_identifier.lower().endswith('.png') or element_identifier.lower().endswith('.bmp'):
        if not os.path.isfile(element_identifier):
            print('[TAGUI][ERROR] - missing image file ' + element_identifier)
            return False

    # assume that (x,y) coordinates for visual automation always exist
    if element_identifier.startswith('(') and element_identifier.endswith(')'):
        if len(element_identifier.split(',')) == 2:
            if not any(c.isalpha() for c in element_identifier):
                return True

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

def select(element_identifier = None, option_value = None, test_coordinate = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using select()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for select()')
        return False

    if option_value is None or option_value == '':
        print('[TAGUI][ERROR] - option missing for select()')
        return False

    if test_coordinate is not None and isinstance(option_value, int):
        element_identifier = coord(element_identifier, option_value)
        option_value = test_coordinate

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
        print('[TAGUI][ERROR] - cannot find ' + filename_to_load)
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
    if _python2_env(): return raw_input(text_to_prompt + ' ')
    else: return input(text_to_prompt + ' ')

def keyboard(keys_and_modifiers = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using keyboard()')
        return False

    if keys_and_modifiers is None or keys_and_modifiers == '':
        print('[TAGUI][ERROR] - keys to type missing for keyboard()')
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
        print('[TAGUI][ERROR] - down / up missing for mouse()')
        return False

    elif mouse_action.lower() != 'down' and mouse_action.lower() != 'up':
        print('[TAGUI][ERROR] - down / up missing for mouse()')
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

def download(element_identifier = None, filename_to_save = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using download()')
        return False

    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for download()')
        return False
    
    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for download()')
        return False

    elif not exist(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('download ' + _sdq(element_identifier) + ' to ' + _esq(filename_to_save)):
        return False

    else:
        return True

def api(url_to_query = None):
    if not _started():
        print('[TAGUI][ERROR] - use init() before using api()')
        return ''

    if url_to_query is None or url_to_query == '':
        print('[TAGUI][ERROR] - API URL missing for api()')
        return ''

    else:
        send('api ' + _esq(url_to_query))
        send('dump api_result to tagui_python.txt')
        api_result = _tagui_output()
        return api_result

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

    else:
        send('dom ' + _esq(statement_to_run))
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

    elif not send('vision ' + _esq(command_to_run)):
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

    if not _started():
        print('[TAGUI][ERROR] - use init() before using timeout()')
        return False

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

    send('count_result = count(\'' + _sdq(element_identifier) + '\').toString()')
    send('dump count_result to tagui_python.txt')
    return int(_tagui_output())

def title():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using title()')
        return ''

    send('dump title() to tagui_python.txt')
    title_result = _tagui_output()
    return title_result

def text():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using text()')
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

    send('dump mouse_xy() to tagui_python.txt')
    mouse_xy_result = _tagui_output()
    return mouse_xy_result

def mouse_x():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using mouse_x()')
        return int(0)

    send('dump mouse_x() to tagui_python.txt')
    mouse_x_result = _tagui_output()
    return int(mouse_x_result)

def mouse_y():
    if not _started():
        print('[TAGUI][ERROR] - use init() before using mouse_y()')
        return int(0)

    send('dump mouse_y() to tagui_python.txt')
    mouse_y_result = _tagui_output()
    return int(mouse_y_result)
