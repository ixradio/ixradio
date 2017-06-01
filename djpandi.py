import os
import time
from slackclient import SlackClient
import spotipy
import spotipy.util as util
from random import randint
import requests

username = '12141837005'
SPOTIPY_CLIENT_ID='da61104d40134998a6849f43ef39035f'
SPOTIPY_CLIENT_SECRET='b2d879812bc14f268cf56286e24213ae'

# starterbot's ID as an environment variable
BOT_ID = 'U5M8K8WMR' 

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"


VALID_COMMAND = ['suggest', 'music']
nextSongId = 0 # reset after suggestion period ends

#key = song name
suggestionPool = {}

class Command(object):
    add = "suggest"
    music = "music"

# instantiate Slack & Twilio clients
slack_client = SlackClient('xoxb-191291302739-3ZcVJx4QiTsxupMYsiFz1xXw')

def returnPlayList():
    response = "https://open.spotify.com/user/12141837005/playlist/55GfcCkX2hHFyFkoLwkMJE"
    return response

def showExisting():
    response = ""
    print suggestionPool
    for key in suggestionPool.keys():
        response += "{}: Song Name: {} \t Artist: {} \t Current Vote: {}\n".format(suggestionPool[key]['id'], key, suggestionPool[key]['artist'], suggestionPool[key]['votes'])
    return response 

def eightBall():
    
    option = {
        1: "Your taste is questionable...",
        2: "Coming right up!",
        3: "Sure thing",
        4: "Hey man .. \n Might as well play static noise",
        5: "That's my favourite song right now!",
        6: "sliently ignoring your request",
        7: "Can I have a bamboo?",
        8: "PPPARRRTTTYY~"
    }
    num = randint(1, 8)
    return option[num]

def vote(cmd):
    songId = cmd.replace('vote', '').strip()
    try:
        id = int(songId)
    except:
        return "Please enter a valid song id"
    for key in suggestionPool.keys():
        if suggestionPool[key]['id'] == id:
            suggestionPool[key]['votes'] += 1
            return "Your vote has been registered."


def addMusic(query):
    print query

    query = "".join(query.split('suggest')[1:])

    print query
    sp = spotipy.Spotify(auth="BQChkvEBlXHHSzRqpS13xAO0fO4rySIlI7pbYOCTk-WCQmISRrBOBKyDNg_igY5VsNNJvExZjplJ4_WfY8OV4ZB_--foelGrtH0LBle_hgUxErSHGlQUMg1OZQ2SywJdoirIsLEqxuR683FngENhjIFEONn7GcUeK9KPfmHSd3F_-LzrZPwxHJI-sEx2vnOP0gIMWr_042i6O0SQOqGVjjhHGzG9IJif8ZgcDCQ_")
    sp.trace = False

    searchResult = sp.search(query, limit=1, type='track')
    print suggestionPool
    global nextSongId
    if searchResult:
        songInfo = searchResult['tracks']['items'][0]

        name = songInfo["name"]
        artist = songInfo['artists'][0]['name']

        if name in suggestionPool:
            pass
        else:
            suggestionPool[name] = {
                'id': nextSongId,
                'artist': artist,
                'votes': 0
            }
            nextSongId += 1
        return "Your request has been accepted. \n({})".format(eightBall())
    else:
        return "I can't find the song you request for"
    #results = sp.user_playlist_add_tracks(username, playlist_id, [searchResult['tracks']['items'][0]['uri']])

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    
    if command.startswith(Command.music):
        response = returnPlayList()
    elif command.startswith(Command.add):
        response = addMusic(command)
    elif command.startswith("show"):
        response = showExisting()
    elif command.startswith("vote"):
        response = vote(command)

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
