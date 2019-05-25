# INTEGRATION ENGINE FOR TAGUI PYTHON PACKAGE ~ TEBEL.ORG

import subprocess
import os
import sys
import time

# entry command to invoke tagui
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

def tagui_output():
# function to read tagui output text and initialise the file
    if os.path.isfile('tagui_python.txt'):
        tagui_output_file = open('tagui_python.txt', mode='r')
        tagui_output_text = tagui_output_file.read()
        tagui_output_file.close()
        tagui_output_file = open('tagui_python.txt', mode='w')
        tagui_output_file.close()
        return tagui_output_text

    else:
        return ''

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

def init():
# connect to tagui process by checking tagui live mode readiness

    global process, tagui_id

    try:
        # loop until tagui live mode is ready or tagui process has ended
        while True:

            # failsafe exit if tagui process gets killed for whatever reason
            if process.poll() is not None: return False

            # use readline instead of read, not expecting user input to tagui
            tagui_out = py23_decode(process.stdout.readline())

            # check that tagui live mode is ready then start listening for inputs
            if 'LIVE MODE - type done to quit' in tagui_out:
                # print new line to clear live mode backspace character before listening
                process.stdin.write(py23_encode('echo ""\n'))
                process.stdin.flush()
                process.stdin.write(py23_encode('echo "[TAGUI][STARTED]"\n'))
                process.stdin.flush()
                process.stdin.write(py23_encode('echo "[TAGUI][' + str(tagui_id) + '] - listening for inputs"\n'))
                process.stdin.flush()
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

        # use readline instead of read, not expecting user input to tagui
        tagui_out = py23_decode(process.stdout.readline())

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
        process.stdin.write(py23_encode('echo "[TAGUI][' + str(tagui_id) + '] - ' + safe_tagui_instruction + '"\n'))
        process.stdin.flush()

        # send live mode instruction to be executed
        process.stdin.write(py23_encode(tagui_instruction + '\n'))
        process.stdin.flush()

        # increment id and prepare for next instruction
        tagui_id = tagui_id + 1
        process.stdin.write(py23_encode('echo "[TAGUI][' + str(tagui_id) + '] - listening for inputs"\n'))
        process.stdin.flush()

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
        process.stdin.write(py23_encode('echo "[TAGUI][FINISHED]"\n'))
        process.stdin.flush()
        process.stdin.write(py23_encode('done\n'))
        process.stdin.flush()

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
        element_present = tagui_output()
        if element_present == 'true':
            return True

    return False
 
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

def ask(text_to_prompt = None):
    if text_to_prompt is None: text_to_prompt = ''
    if python2_env(): return raw_input(text_to_prompt + ' ')
    else: return input(text_to_prompt + ' ')

def wait(delay_in_seconds = None):
    if delay_in_seconds is None: delay_in_seconds = 5.0
    time.sleep(float(delay_in_seconds))
    return True
