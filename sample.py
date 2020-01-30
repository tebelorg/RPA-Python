# Sample script to search on Yahoo, take screenshot of results and visit DuckDuckgo

# RPA for Python's simple and powerful API makes robotic process automation fun!
# pip install rpa to install, pip install rpa --upgrade to get latest version

# to use in Jupyter notebook, Python script or interactive shell
import rpa as r

# use init() to start TagUI, it auto downloads TagUI on first run
# default init(visual_automation = False, chrome_browser = True)
r.init()

# use url('your_url') to go to web page, url() returns current URL
r.url('https://ca.yahoo.com')

# use type() to enter text into an UI element or x, y location
# '[enter]' = enter key, '[clear]' = clear field
r.type('search-box', 'github')

# use read() to fetch and return text from UI element
search_text = r.read('search-box')
print(search_text)

# use click() to click on an UI element or x, y location
# rclick() = right-click, dclick() = double-click
r.click('search-button')

# use wait() to wait for a number of seconds
# default wait() is 5 seconds
r.wait(6.6)

# use snap() to save screenshot of page or UI element
# page = web page, page.png = computer screen
r.snap('page', 'results.png')
r.snap('logo', 'logo.png')

# another example of interacting with a web page
# include http:// or https:// in URL parameter
r.url('https://duckduckgo.com')
r.type('search_form_input_homepage', 'The search engine that doesn\'t track you.')
r.snap('page', 'duckduckgo.png')
r.wait(4.4)

# use close() to close TagUI process and web browser
# if you forget to close, just close() next time
r.close()

# in above web automation example, web element identifier can be XPath selector, CSS selector or
# attributes id, name, class, title, aria-label, text(), href, in decreasing order of priority
# if you don't mind using ugly and less robust XPath, it can be copied from Chrome inspector
# otherwise recommend googling on writing XPath manually, or simply make use of attributes

# also supports visual element identifier using .png or .bmp image snapshot
# representing the UI element (can be on desktop applications or web browser)
# for eg r.click('start_menu.png'), r.type('username_box.png', 'Sonic')

# if the image file specified does not exist, OCR will be used to search for
# that text on the screen to interact with the UI element containing that text
# for eg r.click('Submit Form.png') clicks on a button with text 'Submit Form'
# this trick also works for hover(), type(), select(), read(), snap() functions

# visual element identifiers can also be x, y coordinates of elements on the screen
# for eg r.click(600, 300), r.type(600, 300, 'Mario'), r.select(600, 300, 600, 400)
# another eg is boundary of area of interest x1, y1, x2, y2 for read() and snap()
# for eg r.read(200, 200, 600, 400), r.snap(200, 200, 600, 400, 'results.png')

# image transparency (0% opacity) is supported, ie images with empty sections
# eg r.read('image_preview_frame.png'), r.snap('application_window_frame.png')
# or an element with transparent background to work with varying backgrounds
# r.click('icon_transparent_background.png'), r.click('button_no_bkgnd.png')
