# use pip install tagui to install TagUI for Python
import tagui as t

# use init() to start TagUI, it autoruns setup() to download TagUI
# default init(visual_automation = False, chrome_browser = True)
t.init()

# use url() to go to a webpage, url() returns the current URL
t.url('https://ca.yahoo.com')

# use type() to enter text into an UI element or x,y location
# [enter] = enter key, [clear] = clear field
t.type('search-box','github')

# use show() to print UI element text of an UI element
t.show('search-box')

# use read() to fetch UI element text to variable
search_text = t.read('search-box')

# use click() to click on an UI element or x,y location
# rclick() / dclick() = right / double-click
t.click('search-button')

# use wait() to wait for a number of seconds
t.wait(6.6)

# use snap() to save screenshot of page or UI element
# page = webpage, page.png = computer screen
t.snap('page','results.png')
t.snap('logo','logo.png')

# URL must start with http:// or https://
t.url('https://duckduckgo.com')
t.type('search_form_input_homepage','The search engine that doesn\'t track you.')
t.snap('page','duckduckgo.png')
t.wait(4.4)

# use close() to close TagUI process and web browser
# if you forget to close(), just close() next time
t.close()
