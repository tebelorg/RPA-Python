<img src="https://raw.githubusercontent.com/tebelorg/Tump/master/TagUI-Python/tebel_logo.png" height="111" align="right">

# TagUI for Python

[**Use Cases**](#use-cases) | [**API Reference**](#api-reference) | [**About**](#about)

TagUI for Python's simple, expressive and powerful API makes digital process automation fun and easy!

![TagUI for Python demo in Jupyter notebook](https://raw.githubusercontent.com/tebelorg/Tump/master/tagui_python.gif)

To install this Python package for digital process automation (also known as RPA) -
```
pip install tagui
```

To use TagUI for Python in Jupyter notebook, Python script or interactive shell -
```
import tagui as t
```

# Use Cases

#### WEB AUTOMATION
```
t.init()
t.url('https://www.google.com')
t.type('q', 'decentralization[enter]')
t.snap('page', 'results.png')
t.close()
```

#### VISUAL AUTOMATION
```
t.init(visual_automation = True)
t.dclick('outlook_icon.png')
t.click('new_mail.png')
...
t.type('message_box.png', 'message')
t.click('send_button.png')
t.close()
```

#### KEYBOARD AUTOMATION
```
t.init(visual_automation = True, chrome_browser = False)
t.keyboard('[cmd][space]')
t.keyboard('safari[enter]')
t.keyboard('[cmd]t')
t.keyboard('avengers[enter]')
t.wait(2.5)
t.snap('page.png', 'results.png')
t.close()
```

#### MOUSE AUTOMATION
```
t.init(visual_automation = True)
t.type(600, 300, 'open source')
t.click(900, 300)
t.snap('page.bmp', 'results.bmp')
t.hover('button_to_drag.bmp')
t.mouse('down')
t.hover(t.mouse_x() + 300, t.mouse_y())
t.mouse('up')
t.close()
```

# API Reference

[See sample Python script](https://github.com/tebelorg/TagUI-Python/blob/master/sample.py). For web automation, web element identifier can be XPath selector, CSS selector or attributes - id, name, class, title, aria-label, text(), href (in decreasing order of priority). It also supports visual element identifier using .png or .bmp image snapshot representing the UI element (can be on desktop applications or web browser). Visual element identifiers can also be x, y coordinates of elements on the screen.

#### CORE FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
init()|visual_automation = False, chrome_browser = True|start TagUI, auto-call setup() on first run
close()||close TagUI, Chrome browser, SikuliX
setup()||setup TagUI to user temporary folder

#### DEBUG FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
debug()|True or False|toggle debug mode, eg print and log debug info
send()|tagui_instruction|send TagUI instruction to TagUI for execution

#### BASIC FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
url()|webpage_url (blank to return current URL)|go to web URL
click()|element_identifier (or x, y using visual automation)| left-click on element
rclick()|element_identifier (or x, y using visual automation)|right-click on element
dclick()|element_identifier (or x, y using visual automation)|double-click on element
hover()|element_identifier (or x, y using visual automation)|move mouse to element
type()|element_identifier (or x, y), text_to_type ('[enter]', '[clear]')|enter text at element
select()|element_identifier (or x, y), option_value (or x, y)|choose dropdown option
read()|element_identifier (page = web page)|fetch & return element text
show()|element_identifier (page = web page)|print element text to output
save()|element_identifier (page = web page), filename_to_save|save element text to file
snap()|element_identifier (page = web page), filename_to_save|save screenshot to file
load()|filename_to_load|load & return file content
echo()|text_to_echo|print text to output
dump()|text_to_dump, filename_to_save|save text to file
write()|text_to_write, filename_to_save|append text to file
ask()|text_to_prompt|ask & return user input

#### PRO FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
keyboard()|keys_and_modifiers (using visual automation)|send keystrokes to screen
mouse()|'down' or 'up' (using visual automation)|send mouse event to screen
wait()|delay_in_seconds (default 5 seconds)|explicitly wait for some time
check()|condition_to_check, text_if_true, text_if_false|check condition & print result
table()|element_identifier (XPath only), filename_to_save|save basic HTML table to CSV
upload()|element_identifier (CSS only), filename_to_upload|upload file to web element
download()|download_url, filename_to_save(optional)|download from URL to file
unzip()|file_to_unzip, unzip_location (optional)|unzip zip file to specified location
run()|command_to_run (; between commands)|run OS command & return output
dom()|statement_to_run (JavaScript code)|run code in DOM & return output
vision()|command_to_run (Python code)|run custom SikuliX commands
timeout()|timeout_in_seconds (blank to return current timeout)|change wait timeout (default 10s)

**keyboard() modifiers and special keys**
- [shift] [ctrl] [alt] [cmd] [win] [meta] [clear] [space] [enter] [backspace] [tab] [esc] [up] [down] [left] [right] [pageup] [pagedown] [delete] [home] [end] [insert] [f1] .. [f15] [printscreen] [scrolllock] [pause] [capslock] [numlock]

#### HELPER FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
exist()|element_identifier|return True or False if element exists before timeout
present()|element_identifier|return True or False if element is present now
visible()|element_identifier|return True or False if element is visible now
count()|element_identifier|return number of matching elements as integer
coord()|x_coordinate, y_coordinate|return string '(x,y)' from integers x and y
mouse_xy()||return '(x,y)' coordinates of mouse as string
mouse_x()||return x coordinate of mouse as integer
mouse_y()||return y coordinate of mouse as integer
title()||return page title of current web page as string
text()||return text content of current web page as string
timer()||return time elapsed in sec between calls as float

# About

TagUI is the number 1 open-source RPA software with thousands of users globally. It was created in 2016-2017 when I left DBS Bank as a test automation engineer, to embark on a one-year sabbatical to Eastern Europe. Most of its code base was written in Novi Sad Serbia. My wife and I also spent a couple of months in Budapest Hungary, as well as Chiang Mai Thailand for visa runs. In 2018, I joined AI Singapore to continue development of TagUI.

Over the past 2 months I took on a daddy role full-time, taking care of my newborn baby girl and wife. In between nannying and caregiving duties, I decided to use my time pockets to create a Python package for TagUI. I want to bring RPA directly into the heart of machine learning - the Python ecosystem. I hope that TagUI for Python and ML frameworks would be a match made in heaven, and that `pip install tagui` would make lives easier for Python users.

Lastly, at a mere 1000 lines of code, it would make my day to see developers of other languages porting this project over to their favourite programming language. It would be an interesting exercise and should not be difficult, given the ample comments I sprinkled all over this single-file package in tagui.py, and its intuitive architecture.

You are invited to [connect with me](https://www.linkedin.com/in/kensoh) on LinkedIn, and I would like to credit and express my appreciation below -

- [TagUI](https://github.com/kelaberetiv/TagUI) - AI Singapore from Singapore / [@kelaberetiv](https://github.com/kelaberetiv)
- [SikuliX](http://sikulix.com) - Raimund Hocke from Germany / [@RaiMan](https://github.com/RaiMan)
- [CasperJS](http://casperjs.org) - Nicolas Perriault from France / [@n1k0](https://github.com/n1k0)
- [PhantomJS](http://phantomjs.org) - Ariya Hidayat from Indonesia / [@ariya](https://github.com/ariya)
- [SlimerJS](https://slimerjs.org) - Laurent Jouanneau from France / [@laurentj](https://github.com/laurentj)

# License
TagUI for Python is open-source software released under Apache 2.0 license
