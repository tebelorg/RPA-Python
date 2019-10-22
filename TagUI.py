# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 21:25:07 2019

@author: avikr
"""

import tagui as t
import getpass
t.init(visual_automation = True, chrome_browser = True)
t.url('https://accounts.google.com/ServiceLogin/identifier?service=mail&passive=true&rm=false&continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&ss=1&scc=1&ltmpl=default&ltmplcache=2&emr=1&osid=1&flowName=GlifWebSignIn&flowEntry=ServiceLogin')
t.wait(10)
if t.present('//*[@id="identifierId"]')==True:
    t.keyboard('[alt][tab]')
    t.wait(4)
    emailid=t.ask("Enter Email ID")
    t.wait(10)
    t.keyboard('[alt][tab]')
    t.wait(2)
    t.type('//*[@id="identifierId"]',emailid)
    t.wait(3)
    
    t.click('//*[@id="identifierNext"]/span/span')
    t.wait(3)
    t.keyboard('[alt][tab]')
    t.wait(4)
    password = getpass.getpass("Enter Password")
    t.wait(10)
    t.keyboard('[alt][tab]')
    t.wait(2)
    t.type('//*[@id="password"]/div[1]/div/div[1]/input',password)
    t.wait(3)
    t.click('//*[@id="passwordNext"]/span/span')
t.wait(25)
t.keyboard('[tab]')
t.wait(3)
t.keyboard('[esc]')
t.wait(3)   
t.keyboard('[tab]')
t.wait(3)
t.keyboard('[esc]')
t.wait(3)   
if t.present('//*[text()="Compose"]')==False:
    t.close()
t.click('//*[text()="Compose"]')
t.wait(7)
t.type('//*[@name="to"]','avikrit10@gmail.com[enter]')
t.wait(2)
t.click('//*[text()="Cc"]')
t.wait(2)
t.keyboard('avikrit@hotmail.com')
t.wait(3)
t.type('//*[@name="subjectbox"]','TagUI[enter]')
t.wait(2)
if t.present('//div[@aria-label="Message Body"]')==False:
    t.close()
t.click('//div[@aria-label="Message Body"]')
t.wait(4)
message='''Enter your message

        '''
t.keyboard(message)
t.wait(10)

if t.present('//*[text()="Send"]')==False:
    t.close
t.click('//*[text()="Send"]')
t.wait(10)
t.close()