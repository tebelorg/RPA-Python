# INTEGRATION ENGINE FOR TAGUI PYTHON PACKAGE ~ TEBEL.ORG

import subprocess
import os
import sys
import time

# default delay in seconds in while loops
tagui_delay = 0.1

# entry command to invoke tagui process
tagui_cmd = 'tagui tagui_python chrome'

# launch tagui using subprocess
process = subprocess.Popen(
    tagui_cmd, shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# id to track instruction count between tagui-python and tagui
tagui_id = 0

# delete tagui temp output text file to avoid reading old data 
if os.path.isfile('tagui_python.txt'): os.remove('tagui_python.txt')

def python2_env():
# function to check python version for compatibility handling
    if sys.version_info[0] < 3: return True
    else: return False

def python3_env():
# function to check python version for compatibility handling
    return not python2_env()

def py23_decode(input_variable = None):
# function for python 2 and 3 str-byte compatibility handling
    if input_variable is None: return None
    elif python2_env(): return input_variable
    else: return input_variable.decode('utf-8')

def py23_encode(input_variable = None):
# function for python 2 and 3 str-byte compatibility handling
    if input_variable is None: return None
    elif python2_env(): return input_variable
    else: return input_variable.encode('utf-8')

def tagui_read():
# function to read from tagui process live mode interface
    # readline instead of read, not expecting user input to tagui
    global process; return py23_decode(process.stdout.readline())

def tagui_write(input_text = ''):
# function to write to tagui process live mode interface
    global process; process.stdin.write(py23_encode(input_text))
    process.stdin.flush(); # flush to ensure immediate delivery

def tagui_output():
# function to wait for tagui output file to read and delete it
    while not os.path.isfile('tagui_python.txt'):
        # don't splurge cpu cycles in while loop
        global tagui_delay; time.sleep(tagui_delay) 

    tagui_output_file = open('tagui_python.txt', 'r')
    tagui_output_text = tagui_output_file.read()
    tagui_output_file.close()
    os.remove('tagui_python.txt')
    return tagui_output_text

def init():
# connect to tagui process by checking tagui live mode readiness

    global process, tagui_id

    try:
        # loop until tagui live mode is ready or tagui process has ended
        while True:

            # failsafe exit if tagui process gets killed for whatever reason
            if process.poll() is not None: return False

            # read next line of output from tagui process live mode interface
            tagui_out = tagui_read()

            # check that tagui live mode is ready then start listening for inputs
            if 'LIVE MODE - type done to quit' in tagui_out:
                # print new line to clear live mode backspace character before listening
                tagui_write('echo ""\n')
                tagui_write('echo "[TAGUI][STARTED]"\n')
                tagui_write('echo "[TAGUI][' + str(tagui_id) + '] - listening for inputs"\n')
                return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        return False

def ready():
# check whether tagui is ready to receive instructions

    global process, tagui_id

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if process.poll() is not None: return False

        # read next line of output from tagui process live mode interface
        tagui_out = tagui_read()

        # output for use in development
        sys.stdout.write(tagui_out)
        sys.stdout.flush()

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

    global process, tagui_id

    if tagui_instruction is None or tagui_instruction == '': return True

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if process.poll() is not None: return False

        # loop until tagui live mode is ready and listening for inputs
        while not ready(): pass

        # echo live mode instruction, first remove quotes to be echo-safe
        safe_tagui_instruction = tagui_instruction.replace("'", "").replace('"','')
        tagui_write('echo "[TAGUI][' + str(tagui_id) + '] - ' + safe_tagui_instruction + '"\n')

        # send live mode instruction to be executed
        tagui_write(tagui_instruction + '\n')

        # increment id and prepare for next instruction
        tagui_id = tagui_id + 1
        tagui_write('echo "[TAGUI][' + str(tagui_id) + '] - listening for inputs"\n')

        return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        return False

def close():
# disconnect from tagui process by sending done instruction

    global process, tagui_id

    try:
        # failsafe exit if tagui process gets killed for whatever reason
        if process.poll() is not None: return False

        # loop until tagui live mode is ready and listening for inputs
        while not ready(): pass

        # send done instruction to terminate live mode and exit tagui
        tagui_write('echo "[TAGUI][FINISHED]"\n')
        tagui_write('done\n')

        # loop until tagui process has closed before returning control
        while process.poll() is None: pass

        return True

    except Exception as e:
        print('[TAGUI][ERROR] - ' + str(e))
        return False

def present(element_identifier = None):
    if element_identifier is None or element_identifier == '':
        return False

    tagui_timeout = time.time() + 10
    while time.time() < tagui_timeout:
        send('present_result = present(\'' + element_identifier + '\')')
        send('dump present_result.toString() to tagui_python.txt')
        if tagui_output() == 'true': return True
        # don't splurge cpu cycles in while loop
        global tagui_delay; time.sleep(tagui_delay)

    return False

def url(webpage_url = None):
    if webpage_url is not None and webpage_url != '':
        if webpage_url.startswith('http://') or webpage_url.startswith('https://'):
            if not send(webpage_url):
                return False
            else:
                return True
        else:
            print('[TAGUI][ERROR] - URL does not begin with http:// or https:// ')
            return False

    else:
        send('dump url() to tagui_python.txt')
        url_result = tagui_output()
        return url_result

def click(element_identifier = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for click()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('click ' + element_identifier):
        return False

    else:
        return True

def rclick(element_identifier = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for rclick()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('rclick ' + element_identifier):
        return False

    else:
        return True

def dclick(element_identifier = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for dclick()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('dclick ' + element_identifier):
        return False

    else:
        return True

def hover(element_identifier = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for hover()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('hover ' + element_identifier):
        return False

    else:
        return True

def type(element_identifier = None, text_to_type = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for type()')
        return False

    elif text_to_type is None or text_to_type == '':
        print('[TAGUI][ERROR] - text missing for type()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('type ' + element_identifier + ' as ' + text_to_type):
        return False

    else:
        return True

def select(element_identifier = None, option_value = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for select()')
        return False

    elif option_value is None or option_value == '':
        print('[TAGUI][ERROR] - option missing for select()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('select ' + element_identifier + ' as ' + option_value):
        return False

    else:
        return True

def read(element_identifier = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for read()')
        return ''

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return ''

    else:
        send('read ' + element_identifier + ' to read_result')
        send('dump read_result to tagui_python.txt')
        read_result = tagui_output()
        return read_result

def show(element_identifier = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for show()')
        return ''

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return ''

    else:
        send('read ' + element_identifier + ' to show_result')
        send('dump show_result to tagui_python.txt')
        show_result = tagui_output()
        print(show_result)
        return show_result

def save(element_identifier = None, filename_to_save = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for save()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for save()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('save ' + element_identifier + ' to ' + filename_to_save):
        return False

    else:
        return True

def snap(element_identifier = None, filename_to_save = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for snap()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for snap()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('snap ' + element_identifier + ' to ' + filename_to_save):
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
    if python2_env(): return raw_input(text_to_prompt + ' ')
    else: return input(text_to_prompt + ' ')

def keyboard(keys_and_modifiers = None):
    if keys_and_modifiers is None or keys_and_modifiers == '':
        print('[TAGUI][ERROR] - keys to type missing for keyboard()')
        return False

    elif not send('keyboard ' + keys_and_modifiers):
        return False

    else:
        return True

def mouse(mouse_action = None):
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
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for table()')
        return False

    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for table()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('table ' + element_identifier + ' to ' + filename_to_save):
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
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for upload()')
        return False

    elif filename_to_upload is None or filename_to_upload == '':
        print('[TAGUI][ERROR] - filename missing for upload()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('upload ' + element_identifier + ' as ' + filename_to_upload):
        return False

    else:
        return True

def download(element_identifier = None, filename_to_save = None):
    if element_identifier is None or element_identifier == '':
        print('[TAGUI][ERROR] - target missing for download()')
        return False
    
    elif filename_to_save is None or filename_to_save == '':
        print('[TAGUI][ERROR] - filename missing for download()')
        return False

    elif not present(element_identifier):
        print('[TAGUI][ERROR] - cannot find ' + element_identifier)
        return False

    elif not send('download ' + element_identifier + ' to ' + filename_to_save):
        return False

    else:
        return True

def run(command_to_run = None):
    if command_to_run is None or command_to_run == '':
        print('[TAGUI][ERROR] - command to run missing for run()')
        return ''

    else:
        run_result = ''
        return run_result

def vision(command_to_run = None):
    if command_to_run is None or command_to_run == '':
        print('[TAGUI][ERROR] - command to run missing for vision()')
        return ''

    elif not send('vision ' + command_to_run):
        return False

    else:
        return True  

def timeout(timeout_in_seconds = None):
    if timeout_in_seconds is None:
        print('[TAGUI][ERROR] - time in seconds missing for timeout()')
        return False

    elif not send('timeout ' + str(timeout_in_seconds)):
        return False

    else:
        return True

def title():
    send('dump title() to tagui_python.txt')
    title_result = tagui_output()
    return title_result

def text():
    send('dump text() to tagui_python.txt')
    text_result = tagui_output()
    return text_result

def timer():
    send('dump timer() to tagui_python.txt')
    timer_result = tagui_output()
    return float(timer_result)

def mouse_xy():
    send('dump mouse_xy() to tagui_python.txt')
    mouse_xy_result = tagui_output()
    return mouse_xy_result

def mouse_x():
    send('dump mouse_x() to tagui_python.txt')
    mouse_x_result = tagui_output()
    return int(mouse_x_result)

def mouse_y():
    send('dump mouse_y() to tagui_python.txt')
    mouse_y_result = tagui_output()
    return int(mouse_y_result)
