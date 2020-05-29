# RPA for Python :snake:

[**Use Cases**](#use-cases)&ensp;|&ensp;[**API Reference**](#api-reference)&ensp;|&ensp;[**About & Credits**](#about--credits)&ensp;|&ensp;[**PyCon Video**](https://www.youtube.com/watch?v=F2aQKWx_EAE)&ensp;|&ensp;[**v1.27**](https://github.com/tebelorg/RPA-Python/releases)

>_This tool was previously known as TagUI for Python. [More details](https://github.com/tebelorg/RPA-Python/issues/100) on the name change, which is backward compatible so existing scripts written with `import tagui as t` and `t.function()` will continue to work._

![RPA for Python demo in Jupyter notebook](https://raw.githubusercontent.com/tebelorg/Tump/master/tagui_python.gif)

To install this Python package for RPA (robotic process automation) -
```
pip install rpa
```

To use it in Jupyter notebook, Python script or interactive shell -
```python
import rpa as r
```

Notes on different operating systems and optional visual automation mode -
- :rainbow_flag: **Windows -** if visual automation is cranky, try setting your display zoom level to recommended % or 100%
- :apple: **macOS -** Catalina update introduces tighter app security, see solutions for [PhantomJS](https://github.com/tebelorg/RPA-Python/issues/79) and [Java popups](https://github.com/tebelorg/RPA-Python/issues/78)
- :penguin: **Linux -** visual automation mode requires special setup on Linux, see how to [install OpenCV and Tesseract](https://sikulix-2014.readthedocs.io/en/latest/newslinux.html)

# Use Cases

RPA for Python's simple and powerful API makes robotic process automation fun! You can use it to quickly automate repetitive time-consuming tasks, whether the tasks involve websites, desktop applications, or the command line.

#### WEB AUTOMATION&ensp;:spider_web:
```python
r.init()
r.url('https://www.google.com')
r.type('//*[@name="q"]', 'decentralization[enter]')
print(r.read('result-stats'))
r.snap('page', 'results.png')
r.close()
```

#### VISUAL AUTOMATION&ensp;:see_no_evil:
```python
r.init(visual_automation = True)
r.dclick('outlook_icon.png')
r.click('new_mail.png')
...
r.type('message_box.png', 'message')
r.click('send_button.png')
r.close()
```

#### OCR AUTOMATION&ensp;🧿
```python
r.init(visual_automation = True, chrome_browser = False)
print(r.read('pdf_window.png'))
print(r.read('image_preview.png'))
r.hover('anchor_element.png')
print(r.read(r.mouse_x(), r.mouse_y(), r.mouse_x() + 400, r.mouse_y() + 200))
r.close()
```

#### KEYBOARD AUTOMATION&ensp;:musical_keyboard:
```python
r.init(visual_automation = True, chrome_browser = False)
r.keyboard('[cmd][space]')
r.keyboard('safari[enter]')
r.keyboard('[cmd]t')
r.keyboard('joker[enter]')
r.wait(2.5)
r.snap('page.png', 'results.png')
r.close()
```

#### MOUSE AUTOMATION&ensp;:mouse:
```python
r.init(visual_automation = True)
r.type(600, 300, 'open source')
r.click(900, 300)
r.snap('page.bmp', 'results.bmp')
r.hover('button_to_drag.bmp')
r.mouse('down')
r.hover(r.mouse_x() + 300, r.mouse_y())
r.mouse('up')
r.close()
```

# API Reference

Check out [sample Python script](https://github.com/tebelorg/RPA-Python/blob/master/sample.py), [RPA Challenge solution](https://github.com/tebelorg/RPA-Python/issues/120#issuecomment-610518196), and [RedMart groceries example](https://github.com/tebelorg/RPA-Python/issues/24). To automate Chrome browser invisibly, see this [simple hack](https://github.com/tebelorg/RPA-Python/issues/133#issuecomment-634113838). To run 20-30X faster, without normal UI interaction delays, [see this advanced hack](https://github.com/tebelorg/RPA-Python/issues/120#issuecomment-610532082).

#### ELEMENT IDENTIFIERS
An element identifier helps to tell RPA for Python exactly which element on the user interface you want to interact with. For example, //\*[@id="email"] is an XPath pointing to the webpage element having the id attribute "email".

- :globe_with_meridians: For web automation, the web element identifier can be XPath selector, CSS selector, or the following attributes - id, name, class, title, aria-label, text(), href, in decreasing order of priority. Recommend writing XPath manually or simply using attributes. There is automatic waiting for an element to appear before timeout happens, and error is returned that the element cannot be found. To change the default timeout of 10 seconds, use timeout() function.

- :camera_flash: An element identifier can also be a .png or .bmp image snapshot representing the UI element (can be on desktop applications, terminal window or web browser). If the image file specified does not exist, OCR will be used to search for that text on the screen to act on the UI element containing the text, eg r.click('Submit Form.png'). Transparency (0% opacity) is supported in .png images. x, y coordinates of elements on the screen can be used as well.

- :page_facing_up: A further image identifier example is an image of the window (PDF viewer, MS Word, textbox etc) with the center content of the image set as transparent. This allows using read() and snap() to perform OCR and save snapshots of application windows, containers, frames, textboxes with varying content. Also for read() and snap(), x1, y1, x2, y2 coordinates pair can be used to define the region of interest on the screen to perform OCR or capture snapshot.

#### CORE FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
init()|visual_automation = False, chrome_browser = True|start TagUI, auto-setup on first run
close()||close TagUI, Chrome browser, SikuliX
pack()||for deploying package without internet
update()||for updating package without internet

>_to print and log debug info to rpa_python.log use debug(True), to switch off use debug(False)_

#### BASIC FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
url()|webpage_url (no parameter to return current URL)|go to web URL
click()|element_identifier (or x, y using visual automation)| left-click on element
rclick()|element_identifier (or x, y using visual automation)|right-click on element
dclick()|element_identifier (or x, y using visual automation)|double-click on element
hover()|element_identifier (or x, y using visual automation)|move mouse to element
type()|element_identifier (or x, y), text_to_type ('[enter]', '[clear]')|enter text at element
select()|element_identifier (or x, y), option_value (or x, y)|choose dropdown option
read()|element_identifier (page = web page) (or x1, y1, x2, y2)|fetch & return element text
snap()|element_identifier (page = web page), filename_to_save|save screenshot to file
load()|filename_to_load|load & return file content
dump()|text_to_dump, filename_to_save|save text to file
write()|text_to_write, filename_to_save|append text to file
ask()|text_to_prompt|ask & return user input

>_to wait for an element to appear until timeout() value, use hover(). to drag-and-drop, [you can do this](https://github.com/tebelorg/RPA-Python/issues/58#issuecomment-570778431)_

#### PRO FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
keyboard()|keys_and_modifiers (using visual automation)|send keystrokes to screen
mouse()|'down' or 'up' (using visual automation)|send mouse event to screen
wait()|delay_in_seconds (default 5 seconds)|explicitly wait for some time
table()|element_identifier (XPath only), filename_to_save|save basic HTML table to CSV
upload()|element_identifier (CSS only), filename_to_upload|upload file to web element
download()|download_url, filename_to_save(optional)|download from URL to file
unzip()|file_to_unzip, unzip_location (optional)|unzip zip file to specified location
frame()|main_frame id or name, sub_frame (optional)|set web frame, frame() to reset
popup()|string_in_url (no parameter to reset to main page)|set context to web popup tab
run()|command_to_run (use ; between commands)|run OS command & return output
dom()|statement_to_run (JS code to run in browser)|run code in DOM & return output
vision()|command_to_run (Python code for SikuliX)|run custom SikuliX commands
timeout()|timeout_in_seconds (blank returns current timeout)|change wait timeout (default 10s)

keyboard() modifiers and special keys -
>_[shift] [ctrl] [alt] [cmd] [win] [meta] [clear] [space] [enter] [backspace] [tab] [esc] [up] [down] [left] [right] [pageup] [pagedown] [delete] [home] [end] [insert] [f1] .. [f15] [printscreen] [scrolllock] [pause] [capslock] [numlock]_

#### HELPER FUNCTIONS
Function|Parameters|Purpose
:-------|:---------|:------
exist()|element_identifier|return True or False if element exists before timeout
present()|element_identifier|return True or False if element is present now
count()|element_identifier|return number of web elements as integer
clipboard()|text_to_put or no parameter|put text or return clipboard text as string
mouse_xy()||return '(x,y)' coordinates of mouse as string
mouse_x()||return x coordinate of mouse as integer
mouse_y()||return y coordinate of mouse as integer
title()||return page title of current web page as string
text()||return text content of current web page as string
timer()||return time elapsed in sec between calls as float

>_to type large amount of text quickly, use clipboard() and keyboard() to paste instead of type()_

# About & Credits

TagUI is the leading open-source RPA software :robot: with thousands of active users. It was created in 2016-2017 when I left DBS Bank as a test automation engineer, to embark on a one-year sabbatical to Eastern Europe. Most of its code base was written in Novi Sad Serbia. My wife and I also spent a couple of months in Budapest Hungary, as well as Chiang Mai Thailand for visa runs. In 2018, I joined AI Singapore to continue development of TagUI.

Over the past few months I take on a daddy role full-time, taking care of my newborn baby girl and wife :cowboy_hat_face:🤱. In between the nannying, I use my time pockets to create this Python package that's built on TagUI. I hope that RPA for Python and ML frameworks would be good friends, and `pip install rpa` would make life easier for Python users.

Lastly, at only ~1k lines of code, it would make my day to see developers of other languages port this project over to their favourite programming language. See ample comments in this [single-file package](https://github.com/tebelorg/RPA-Python/blob/master/tagui.py), and its intuitive architecture -

![RPA for Python architecture](https://raw.githubusercontent.com/tebelorg/Tump/master/TagUI-Python/architecture.png)

I would like to credit and express my appreciation below :bowing_man:, and you are invited to [connect on LinkedIn](https://www.linkedin.com/in/kensoh) -

- [TagUI](https://github.com/kelaberetiv/TagUI/tree/pre_v6) - AI Singapore from Singapore / [@aisingapore](https://www.aisingapore.org)
- [SikuliX](https://github.com/RaiMan/SikuliX1) - Raimund Hocke from Germany / [@RaiMan](https://github.com/RaiMan)
- [CasperJS](https://github.com/casperjs/casperjs) - Nicolas Perriault from France / [@n1k0](https://github.com/n1k0)
- [PhantomJS](https://github.com/ariya/phantomjs) - Ariya Hidayat from Indonesia / [@ariya](https://github.com/ariya)
- [SlimerJS](https://github.com/laurentj/slimerjs) - Laurent Jouanneau from France / [@laurentj](https://github.com/laurentj)

# License
RPA for Python is open-source software released under Apache 2.0 license
