import tagui as t

tagui_flow = [
    'https://ca.yahoo.com',
    'type search-box as github',
    'show search-box',
    'click search-button',
    'snap page',
    'snap logo',
    'https://duckduckgo.com',
    'type search_form_input_homepage as The search engine that doesnt track you.',
]

t.init()

t.send(tagui_flow[0])
t.send(tagui_flow[1])
t.send(tagui_flow[2])
t.click("search-button")

t.wait(5)

t.send(tagui_flow[4])
t.send(tagui_flow[5])
t.send(tagui_flow[6])
t.send(tagui_flow[7])

t.close()
