import tagui as t

t.init()

t.url('https://ca.yahoo.com')
t.type('search-box','github')
t.show('search-box')
t.click('search-button')
t.wait(6.6)
t.snap('page','results.png')
t.snap('logo','logo.png')

t.url('https://duckduckgo.com')
t.type('search_form_input_homepage','The search engine that doesn\'t track you.')
t.snap('page','duckduckgo.png')
t.wait(4.4)

t.close()
