# ripper.py - zoom.rip - maxtheaxe
# Happy April Fool's Day!
# code taken in part from my host-client built for Zoom Education Suite (https://github.com/maxtheaxe/zoom-education-suite)
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
# from bs4 import BeautifulSoup as bs
import sys
import re
import time
import random
import signal

# launch() - launch sequence to get driver started, logged in, and prepared to work
def launch(room_link, headless = True, bot_name = "Matt Smith", verbose = False):
	# print("\tLaunching a bot...\n")
	driver = start_driver(headless) # start the driver and store it (will be returned)
	login(driver, room_link, bot_name, verbose) # log into the room with the room link and name
	open_participants(driver) # open participants panel so data can be collected
	# open_chat(driver) # open chat for some fun later
	# print("\t", bot_name, "successfully launched.\n")
	return driver # return driver so it can be stored and used later

# multi_launch() - launch sequence to get driver started, logged in, and prepared to work
# flood mode removes chat opening and other stuff, maximizes speed
def multi_launch(room_link, num_clients = 1, headless = True, flood = True):
	# print("\n\t--- zoom.rip | making remote learning fun ---\n")
	driver_list = [] # a spot to store multiple drivers (for multiple clients)
	for i in range(num_clients):
		driver = start_driver(headless) # start the driver and store it (will be returned)
		login(driver, room_link) # log into the room with the room link
		# open_participants(driver) # open participants panel so data can be collected
		open_chat(driver) # open chat for some fun later
		driver_list.append(driver) # store each driver in the list of drivers
	return driver_list # return drivers so they can be stored and worked on within GUI program

# start_driver() - starts the webdriver and returns it
# reference: https://stackoverflow.com/questions/12698843/how-do-i-pass-options-to-the-selenium-chrome-driver-using-python
# reference: https://groups.google.com/forum/?hl=en-GB#!topic/selenium-users/ZANuzTA2VYQ
def start_driver(headless = True):
	# setup webdriver settings
	options = webdriver.ChromeOptions() # hiding startup info that pollutes terminal
	options.headless = headless # headless or not, passed as arg
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	# add support for fake webcam and audio
	# options.add_argument("--load-extension=C:\\Users\\max\\Documents\\CS\\other\\zoom.rip project\\zoom.rip\\client\\dynamic-getUserMedia-master") # mess with getUserMedia at runtime
	options.add_argument("--allow-file-access-from-files")
	options.add_argument("--use-fake-ui-for-media-stream")
	options.add_argument("--allow-file-access")
	options.add_argument("--enable-features=WebRTC-H264WithOpenH264FFmpeg")
	options.add_argument("--use-file-for-fake-audio-capture=monsters-inc.wav") # audio
	# options.add_argument("--use-file-for-fake-video-capture=C:\\Users\\max\\Documents\\CS\\other\\zoom.rip project\\zoom.rip\\media\\1.y4m") # video
	options.add_argument("--use-fake-device-for-media-stream")
	# make window size bigger to see all buttons
	options.add_argument("--window-size=1600,1200")
	# start webdriver and return it
	return webdriver.Chrome(options=options)

# prompt() - prompts the host to enter the room link
def prompt():
	# should probably be a tkinter window, don't know how packaging works with cmd line
	return

# link_builder() - builds web link from og link to skip local app prompt
# future: add password support (for locked rooms)
def link_builder(room_link):
	# replaces /j/ with /wc/join/ to open web client directly
	web_link = re.sub("/j/", "/wc/join/", room_link)
	return web_link

# login() - logs into the room
# reference: https://crossbrowsertesting.com/blog/test-automation/automate-login-with-selenium/
# reference: https://stackoverflow.com/questions/19035186/how-to-select-element-using-xpath-syntax-on-selenium-for-python
# future: add password support (for locked rooms)
def login(driver, room_link, bot_name = "Matt Smith", verbose = False):
	# print("\tLogging in...\n")
	web_link = link_builder(room_link) # convert to web client link
	try: # try opening the given link, logging in
		driver.get(web_link) # open zoom meeting login page
		driver.find_element_by_id('inputname').send_keys(bot_name) # enter bot name
		# might need to account for room passwords if using private rooms
		driver.find_element_by_id('joinBtn').click() # click login button
		# driver.send_keys(u'\ue007') # press enter key (alt login method)
	except: # bad link, try again
		print("\tError: Login Failed. Check the link and try again.\n")
		sys.exit()
	try: # wait and make sure we're logged in, loaded into the room
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'footer__leave-btn')))
		if EC.visibility_of(driver.find_element_by_class_name("footer__leave-btn")):
			if verbose:
				print("\tSuccessfully logged in.\n")
	except: # something went wrong, we weren't able to load into the room
		print("\tError: Login Failed. Verify that you're connecting to the right room.\n")
		sys.exit()

# click_participants() - click on the participants button
# originally always left open, made this to allow for closing to avoid interference
# refactor: combine this with click_chat() to make general menu opener
def click_participants(driver):
	time.sleep(2)
	try: # try to click it right away
		# find it using the participants icon
		driver.find_element_by_class_name("footer-button__participants-icon").click()
	except: # if it isn't clickable (sometimes takes a sec to load properly)
		# print("\tFailed. Trying again, please wait...\n")
		time.sleep(7)
		driver.find_element_by_class_name("footer-button__participants-icon").click()
	return

# open_participants() - opens the participants menu, loads all members
def open_participants(driver):
	# print("\tOpening participants list...\n")
	click_participants(driver)
	# print("\tOpened participants list.\n")
	return

# close_participants() - opens the participants menu, loads all members
def close_participants(driver):
	# print("\tClosing participants list...\n")
	click_participants(driver)
	# print("\tClosed participants list.\n")
	return

# count_reaction() - counts the number of a chosen reaction at a given time
def count_reaction(driver, reaction_name = "participants-icon__participants-raisehand"):
	# find elements of given reaction class (hand raise by default)
	react_list = driver.find_elements_by_class_name(reaction_name)
	# print("\tNumber of hands raised: " , len(react_list), "\n") # print total
	return len(react_list) # return number of reactions

# who_participates() - checks who is currently participating (via reactions)
# reference: https://stackoverflow.com/questions/18079765/how-to-find-parent-elements-by-python-webdriver
def who_participates(driver, reaction_name = "participants-icon__participants-raisehand"):
	participant_list = [] # empty list to hold participants
	# find elements of given reaction class (hand raise by default)
	react_list = driver.find_elements_by_class_name(reaction_name)
	for i in range(len(react_list)): # for each reaction element (belongs to a person)
		# go to grandparent element, so we can check the name (store in curr element)
		react_list[i] = react_list[i].find_element_by_xpath("../..")
		# get the name element (store in curr element)
		react_list[i] = react_list[i].find_element_by_class_name("participants-item__display-name")
		# refine to name string (store in curr element)
		react_list[i] = react_list[i].get_attribute("innerHTML")
	# print("\tPeople raising hands: " , react_list, "\n") # print total
	return react_list # return list of people reacting

# call_on() - calls on the first person to raise their hand; if it can't tell, randomizes
def call_on(driver):
	hand_raiser_list = who_participates(driver) # check who is raising their hand rn
	if (len(hand_raiser_list) == 0): # if no-one is raising their hand
		# print("\tYou can't call on anyone if no-one is raising their hand!\n")
		return # return no-one
	elif (len(hand_raiser_list) == 1): # if one person is raising their hand
		# print("\tThey raised their hand first, so you called on:",
		# 	hand_raiser_list[0], "\n") # print selection
		return hand_raiser_list[0] # return the one person raising their hand
	else: # if more than one person is raising their hand
		chosen_person = random.choice(hand_raiser_list) # choose someone randomly
		# print("\tYou didn't see who was first, so you guessed and called on:",
		# 	chosen_person, "\n") # print selection
		return chosen_person # return your "guess" at who was first

# identify_host() - identifies the name of the host
def identify_host(driver):
	# identify host by consistent place second in list, narrow down to display name
	target = driver.find_element_by_xpath(
		"//*[@id='participants-list-1']//span[@class='participants-item__display-name']")
	# get innerHTML of actual host's name
	recipient_name = target.get_attribute("innerHTML")
	# print("\tThe name of the host is:", recipient_name, "\n")
	return recipient_name

# click_chat(driver) - opens or closes chat window
# refactor: combine this with open_participants to make general menu opener
def click_chat(driver):
	time.sleep(2)
	# had to handle making window size bigger because participants list cut off button
	# see driver_start() for solution
	try: # try to click it right away
		# find it using the chat icon
		driver.find_element_by_class_name("footer-button__chat-icon").click()
	except: # if it isn't clickable (sometimes takes a sec to load properly)
		# print("\tFailed. Trying again, please wait...\n")
		time.sleep(7)
		driver.find_element_by_class_name("footer-button__chat-icon").click()
	return # successfully clicked (hopefully)

# open_chat() -  opens chat popup
def open_chat(driver):
	# print("\tOpening chat menu...\n")
	click_chat(driver) # click on the chat button
	# print("\tOpened chat menu.\n")
	return

# close_chat() - closes chat popup
def close_chat(driver):
	# print("\tClosing chat menu...\n")
	click_chat(driver) # click on the chat button
	# print("\tClosed chat menu.\n")
	return

# choose_recipient() - selects the chosen recipient from the dropdown
# reference: https://www.guru99.com/xpath-selenium.html
# reference: https://stackoverflow.com/questions/29346595/python-selenium-element-is-not-currently-interactable-and-may-not-be-manipulat
def choose_recipient(driver, recipient_name):
	# print("\tFinding target recipient.\n")
	# open the dropdown menu
	try: # try to find it right away
		# find the dropdown menu
		dropdown = driver.find_element_by_class_name(
			# "chat-receiver-list__chat-control-receiver ax-outline-blue-important dropdown-toggle btn btn-default")
			"chat-receiver-list__chat-control-receiver")
	except: # if it isn't clickable (sometimes takes a sec to load properly)
		# print("\tFailed. Trying again, please wait...\n")
		time.sleep(7)
		dropdown = driver.find_element_by_class_name(
			# "chat-receiver-list__chat-control-receiver ax-outline-blue-important dropdown-toggle btn btn-default")
			"chat-receiver-list__chat-control-receiver")
	dropdown.click() # click the dropdown menu
	time.sleep(2) # lazy way to wait for it to load
	# now find and click on the actual recipient
	# first, focus on the actual dropdown menu of potential recipients
	dropdown = driver.find_element_by_class_name("chat-receiver-list__scrollbar-height")
	# find the element with our recipient's name
	# dropdown.find_element_by_xpath('//dd[@data-value="' + recipient_name + '"])').click()
	# build our string for xpath (probably a better way, but oh well)
	xpath_string = "//a[contains(text(), '" + recipient_name + "')]"
	# print("testing name:\n", xpath_string)
	dropdown_element = dropdown.find_element_by_xpath(xpath_string)
	# now go up a level to the clickable parent
	dropdown_element = dropdown_element.find_element_by_xpath("./..")
	# now actually click the element so we can send 'em a message
	dropdown_element.click()
	# time.sleep(1) # just to be sure (testing)
	return

# type_message() - types out message in chatbox and sends it
def type_message(driver, message):
	# grab chatbox by its class name
	chatbox = driver.find_element_by_class_name("chat-box__chat-textarea")
	# type out the given message in the chatbox
	chatbox.send_keys(message)
	# hit enter in the chatbox to send the message
	chatbox.send_keys(u'\ue007')
	return

# send_message() - have the bot send someone (by default the host) a message
# reference: https://stackoverflow.com/questions/12323403/how-do-i-find-an-element-that-contains-specific-text-in-selenium-webdriver-pyth
def send_message(driver, recipient = "host", message = "Happy April Fool's Day!"):
	open_chat(driver) # open the chat menu, to enable sending a message
	recipient_name = "" # temporary storage for recipient name
	if (recipient == "host"): # if the recipient is default
		# call identify_host() to get host's name
		recipient_name = identify_host(driver) # set host's name to recipient name
	else:
		recipient_name = recipient # set recipient_name to input name
	choose_recipient(driver, recipient_name) # choose the recipient from the menu
	if (type(message) == str): # if the message argument is a string
		type_message(driver, message) # type one message
	elif (type(message) == list): # if the message argument is a list
		# send a message for each string in the list
		for i in range(len(message)):
			type_message(driver, message[i])
	# print("\tSending message to:", recipient_name, "\n")
	close_chat(driver) # close the chat menu, since you're done sending a message
	return recipient_name

# mass_message() - have the bots send everyone a message
# reference: https://stackoverflow.com/questions/12323403/how-do-i-find-an-element-that-contains-specific-text-in-selenium-webdriver-pyth
def mass_message(driver, message = "Happy April Fool's Day!"):
	open_chat(driver) # open the chat menu, to enable sending a message
	if (type(message) == str): # if the message argument is a string
		type_message(driver, message) # type one message
	elif (type(message) == list): # if the message argument is a list
		# send a message for each string in the list
		for i in range(len(message)):
			type_message(driver, message[i])
	# print("\tSending message to:", recipient_name, "\n")
	close_chat(driver) # close the chat menu, since you're done sending a message
	return

# sing_song() - sings a song using the bots
def sing_song(driver_list, lyrics):
	# split the lyrics by line, so diff bots can "sing" each one
	lyric_list = str.splitlines(lyrics)
	while (len(lyric_list) > 0):
		# while there are still lyrics left to sing in the lyric list
		for i in range(driver_list):
			# loop through the driver list and have each one sing a line
			mass_message(driver_list[i], lyric_list[0])
			# then chop off the lyric that was just sent and restart
			lyric_list = lyric_list[1:]
	return

# take_attendance() - take attendance of who is there at current time
# I'd have avoided the second list creation, but attendee list was polluted by bot names
# could add filtering out prof later, but requires searching addditional elements
def take_attendance(driver):
	# collect all attendees into list by looking for spans with the following class
	attendee_list = driver.find_elements_by_class_name("participants-item__display-name")
	new_attendee_list = [] # for storing refined list (filters out self)
	for i in range(len(attendee_list)): # for each webElement in list of attendees
		if (attendee_list[i].get_attribute("innerHTML") != "zoom edu bot"): # if not bot
			# then refine to name and add to the new list
			new_attendee_list.append(attendee_list[i].get_attribute("innerHTML"))
	# print("\tCurrent Students: ", new_attendee_list, "\n") # print list of attendee names
	return new_attendee_list # return attendee list

# leave_meeting() - leaves the meeting by closing the driver and quitting
def leave_meeting(driver):
	# print("\tLeaving meeting...\n")
	driver.quit() # quit and close the driver to prevent issues
	# print("\tSuccessfully left the meeting. See you next time!\n")
	return

# call_first() - calls on the first person to raise their hand and notifies them
def call_first(driver, message = "You're up!"):
	chosen_person = call_on(driver) # calls on the first person to raise hand and stores
	send_message(driver, chosen_person, message) # sends the person who was called on the given message
	return

# change_name() - changes current name to a given name
# reference: https://www.seleniumeasy.com/selenium-tutorials/how-to-perform-mouseover-action-in-selenium-webdriver
# needed actionchains because rename button wouldn't show until the participant was hovered over
def change_name(driver, new_name):
	# print("\tChanging name...\n")
	# driver.find_element_by_xpath("//button[contains(text(), 'Rename')]").click()
	# driver.find_element_by_xpath("//div[@class='participants-item__buttons']//button[contains(text(), 'Rename')]").click()
	my_entry = driver.find_element_by_id("participants-list-0")
	# build new action chain to do so
	action = ActionChains(driver)
	# hover over own name on participants list
	action.move_to_element(my_entry).perform()
	# find the rename button and click it
	# action.move_to_element(driver.find_element_by_xpath("//div[@class='participants-item__buttons']//button[contains(text(), 'Rename')]"))
	driver.find_element_by_xpath("//div[@class='participants-item__buttons']//button[contains(text(), 'Rename')]").click()
	# find the new name box
	name_box = driver.find_element_by_id("newname")
	# clear the old name
	name_box.clear()
	# type in the new name
	name_box.send_keys(new_name)
	# hit enter to save it
	name_box.send_keys(u'\ue007')
	# print("\tName changed to:", new_name, "\n")
	return

# remove_host() - for removing host from attendance
def remove_host(driver, name_list):
	# check who the host is
	host_name = identify_host(driver)
	# remove the host's name from the attendance list (they'll know you're not them)
	new_list = name_list[:]
	# had weird none type stuff when all of this was one line
	new_list.remove(host_name)
	return new_list # return edited list

# go_dark() - takes attendance and chooses name at random, then changes its own to match
def go_dark(driver):
	# print("\tGoing dark!\n") # let user know you're going undercover
	name_options = take_attendance(driver) # store current students in list
	# remove host's name from list
	name_options = remove_host(driver, name_options)
	# if there is anyone else there in attendance
	if (len(name_options) >= 1):
		# then choose one of their names randomly
		chosen_name = random.choice(name_options)
	else: # if noone but the host is there
		# set your name to Matt Smith
		chosen_name = "Matt Smith"
	change_name(driver, chosen_name) # call change name function
	# print("\tIdentity theft complete.\n") # let user know you're safely hidden
	return

# cavalry() - brings the "cavalry," by bringing in other bots with stolen names
def cavalry(driver, room_link, num_bots = 10):
	headless = True # should they show the chrome GUI?
	driver_list = [] # create list for storing newly-created bots
	name_options = take_attendance(driver) # get list of students
	name_options = remove_host(driver, name_options) # remove host's name
	og_name_options = name_options[:] # clone the list in case we need more later
	random.shuffle(name_options) # shuffle the name list
	for i in range(num_bots): # loop for as many times as num bots desired
		# account for case where desired num is higher than attendance
		# there's def a better way, but this is fine for these purposes
		if len(name_options) == 0:
			name_options = og_name_options[:]
		# set bot_name by popping name from attendance list (name_options)
		bot_name = name_options.pop()
		# launch another driver/client with the given info
		driver = launch(room_link, headless, bot_name)
		# store the newly-created bot in our list of drivers
		driver_list.append(driver)
	return driver_list # return the list of newly-created drivers

# infiltrate() - "infiltrate" the class by setting details and then flooding with clones
def infiltrate():
	headless = True
	bot_list = [] # list of drivers for each bot to close later
	print("\n\tWelcome to zoom.rip! Please don't abuse it.\n" +
		"\tI take no responsibility for your actions. Happy April Fools Day!" +
		"\n\n\tFollow @MaxPerrello on Twitter for future updates.\n")
	# wanted to keep char count below ninety
	room_link = input("\n\tWhat is the zoom meeting link?\n" +
		"\t(Paste it in and hit the Enter key)\n")
	print("\n") # for terminal formatting niceties
	# first_name = input("\tWhat do you want the first bot's name to be?\n" +
	# 	"\t(Think of something believable, then type it in and hit the Enter key)\n")
	# if you're looking at this, you know what this is and why I've done it
	first_name = "_Matt"
	# make sure first bot prints login results
	verbose = True
	# make the first bot that will open the floodgates
	first_bot = launch(room_link, headless, first_name, verbose)
	# write apologetic + explanatory message to teacher
	# for the record, \n doesn't work in zoom chat for new lines
	teach_msg = ["Hi, I'm the creator of this bot and this is an automated message.",
	"Basically, it enables people to fill meetings with clone users.",
	"I tried to minimize its potential for abuse by leaving a LOT of features",
	"out of it, but I'm sure it's still somewhat annoying. If someone is using",
	"this bot and it is bothering you, please don't hesitate to send me a message,",
	"and I'll walk you through how to prevent them from abusing it in the future.",
	"This was created as an April Fools project, but is based on what was originally",
	"a program I created to enhance teachers' Zoom experiences in the classroom.",
	"If you have any interest in using that, I'd be happy to help you set it up.",
	" ", " ", "tl;dr", " ",
	"Feel free to message me on Twitter @MaxPerrello for any reason whatsoever."]
	# send a message to the teacher, explaining what's going on and how to reach me
	send_message(first_bot, "host", teach_msg)
	# have the first bot go dark, stealth mode
	go_dark(first_bot)
	# append it to the storage list
	bot_list.append(first_bot)
	num_bots = input("\n\tHow many fake users to you want to flood the meeting?\n\n" +
		"\t(Keep in mind they will use system resources and slow down your computer)\n")
	try: # try to cast the given input to an int
		num_bots = int(num_bots)
	except: # if it fails, tell them and just use 10 instead
		print("\tSorry, that wasn't a number. Defaulting to 10 bots.\n")
		num_bots = 10
	# call in the cavalry (bring in the additional bots)
	the_cavalry = cavalry(first_bot, room_link, num_bots)
	# store all the new bots in our master bot list
	bot_list.extend(the_cavalry)
	return bot_list # return the stored list of bots

# signal_handler() - handles closing the program, to ensure all drivers are quit properly
# reference: https://www.devdungeon.com/content/python-catch-sigint-ctrl-c
def signal_handler(signal_received, frame):
	global bot_list # I've never used global variables with python, so idrk what I'm doin
	# Handle any cleanup here
	print("\n\tClosing all bots, please wait...\n")
	# for all bots stored in master list
	for i in range(len(bot_list)):
		leave_meeting(bot_list[i]) # leave and quit on each driver/bot
	print("\tAll done! If you enjoyed this, shoot me a tweet with a video of you using it.\n")
	sys.exit(0)

def main(argv):
	print("\n\t--- zoom.rip | making remote learning fun ---\n")
	driver_list = [] # store the bots so we can close 'em later
	main_driver = launch("xxx", False)
	driver_list.append(main_driver) # store the main one in the list
	go_dark(driver[0])
	time.sleep(60)

if __name__ == '__main__':
	# main(sys.argv)
	# start infiltrating! go bananas!
	bot_list = infiltrate() # store the bots to close later
	# Tell Python to run the handler() function when SIGINT is recieved
	signal.signal(signal.SIGINT, signal_handler)
	print("\tUse Control + C to close all bots.") # print instructions
	while True:
		# prompt the user to paste song lyrics
		# lyrics = input("\tWant the bots to sing a song? Just paste in the lyrics and hit the Enter key.\n")
		# call the sing song function with the given lyrics
		# sing_song(bot_list, lyrics)
		# Do nothing and hog CPU forever until SIGINT received.
		pass