import tagui as t

t.init()

t.url('https://ca.yahoo.com')
t.type('search-box','github')
t.show('search-box')
t.click("search-button")
t.wait()
t.snap('page','/tmp/page.png')
t.snap('logo','/tmp/logo.png')
t.url('https://duckduckgo.com')
t.type('search_form_input_homepage','The search engine that doesnt track you.')

t.close()
