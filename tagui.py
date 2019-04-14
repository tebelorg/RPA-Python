# INTEGRATION ENGINE FOR TAGUI PYTHON PACKAGE ~ TEBEL.ORG

import subprocess
import sys
import time

tagui_flow = [
    'https://ca.yahoo.com',
    'type search-box as github',
    'show search-box',
    'click search-button',
    'snap page',
    'snap logo'
]

# entry command to invoke tagui
tagui_cmd = 'tagui tagui_python chrome'

# launch tagui using subprocess
process = subprocess.Popen(
    tagui_cmd, shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# flag to track that tagui is ready to receive instructions
tagui_ready = False

# id to track instruction count between tagui-python and tagui
tagui_id = 0

while True:
    # use readline instead of read, not expecting user input to tagui
    tagui_out = process.stdout.readline()

    # failsafe exit when tagui process gets killed, due to error etc
    if tagui_out == '' and process.poll() is not None:
        break

    # process output from tagui process
    if tagui_out != '':
        sys.stdout.write(tagui_out)
        sys.stdout.flush()

        # initial sync by checking that tagui live mode is ready and start listening
        if 'LIVE MODE - type done to quit' in tagui_out:
            # print new line before listening to clear live mode backspace character
            process.stdin.write('echo ""\n')
            #process.stdin.write('echo "[tagui][start]"\n')
            process.stdin.flush()
            process.stdin.write('echo "[tagui][' + str(tagui_id) + '] - listening for inputs"\n')
            process.stdin.flush()

        # subsequent sync by checking that tagui live mode is listening for inputs
        elif tagui_out.strip().startswith('[tagui][') and tagui_out.strip().endswith('] - listening for inputs'):
            tagui_ready = True

        # send next live mode instruction to tagui for processing if tagui is ready
        if tagui_ready:
            tagui_ready = False
            if tagui_id == 4: time.sleep(5)
            if tagui_id == 6:
                process.stdin.write('done\n')
                process.stdin.flush()
                break

            # echo live mode instruction to be executed
            process.stdin.write('echo "[tagui][' + str(tagui_id) + '] - ' + tagui_flow[tagui_id] + '"\n')
            process.stdin.flush()

            # send live mode instruction to be executed
            process.stdin.write(tagui_flow[tagui_id] + '\n')
            process.stdin.flush()

            # increment id and prepare for next instruction
            tagui_id = tagui_id + 1
            process.stdin.write('echo "[tagui][' + str(tagui_id) + '] - listening for inputs"\n')
            process.stdin.flush()

