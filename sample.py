# Sample script to search on Yahoo, take screenshot of results and visit DuckDuckgo

# TagUI for Python's simple and powerful API makes digital process automation fun!
# pip install tagui to install, pip install tagui --upgrade for latest version

# to use in Jupyter notebook, Python script or interactive shell
import tagui as t

# use init() to start TagUI, it auto downloads TagUI on first run
# default init(visual_automation = False, chrome_browser = True)
t.init()

# use url('your_url') to go to web page, url() returns current URL
t.url('https://ca.yahoo.com')

# use type() to enter text into an UI element or x, y location
# '[enter]' = enter key, '[clear]' = clear field
t.type('search-box', 'github')

# use read() to fetch and return text from UI element
search_text = t.read('search-box')
print(search_text)

# use click() to click on an UI element or x, y location
# rclick() = right-click, dclick() = double-click
t.click('search-button')

# use wait() to wait for a number of seconds
# default wait() is 5 seconds
t.wait(6.6)

# use snap() to save screenshot of page or UI element
# page = web page, page.png = computer screen
t.snap('page', 'results.png')
t.snap('logo', 'logo.png')

# another example of interacting with a web page
# include http:// or https:// in URL parameter
t.url('https://duckduckgo.com')
t.type('search_form_input_homepage', 'The search engine that doesn\'t track you.')
t.snap('page', 'duckduckgo.png')
t.wait(4.4)

# use close() to close TagUI process and web browser
# if you forget to close, just close() next time
t.close()

# in above web automation example, web element identifier can be XPath selector, CSS selector or
# attributes id, name, class, title, aria-label, text(), href, in decreasing order of priority
# if you don't mind using ugly and less robust XPath, it can be copied from Chrome inspector
# otherwise recommend googling on writing XPath manually, or simply make use of attributes

# also supports visual element identifier using .png or .bmp image snapshot
# representing the UI element (can be on desktop applications or web browser)
# for eg t.click('start_menu.png'), t.type('username_box.png', 'Sonic')

# image transparency (0% opacity) is supported, ie images with empty sections
# t.read('image_preview_frame.png'), t.snap('application_window_frame.png')

# visual element identifiers can also be x, y coordinates of elements on the screen
# for eg t.click(600, 300), t.type(600, 300, 'Mario'), t.select(600, 300, 600, 400)

# another eg is boundary of area of interest x1, y1, x2, y2 for read() and snap()
# t.read(200, 200, 600, 400), t.snap(200, 200, 600, 400, 'results.png')
