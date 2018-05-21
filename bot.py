import requests
import sys
import time
import re
import json
import termcolor
import unidecode

import CONFIG


class Outgoing_Message():

    def __init__(self, chat_id=None, text="", replie_to=None):
        self.chat_id = chat_id
        self.text = text
        self.reply_to_message_id = replie_to
        self.parse_mode = False
        self.disable_web_page_preview = False
        self.disable_notification = False


class Incoming_Message():

    def __init__(self, message_dict):
        self.raw = message_dict
        self.message_id = message_dict.get("message_id")
        self.text = message_dict.get("text", '')
        self.date = message_dict.get("date")
        self.edit_date = None
        self.from_usr_id = message_dict.get("from").get("id")
        self.from_usr_name = message_dict.get("from").get("username")
        self.from_chat_id = message_dict.get("chat").get("id")
        self.from_chat_name = None
        self.form_chat_type = message_dict.get("chat").get("type")
        if self.form_chat_type =="group":
            self.from_chat_name = message_dict.get("chat").get("title")
        elif self.form_chat_type == "private":
            self.from_chat_name = message_dict.get("chat").get("username")

    def __str__(self):
        values_string_array = ["{}: {}".format(key, value) for key, value in vars(self).items() if key != "raw"]
        class_name = self.__class__.__name__.replace("_", " ")
        return "<{}> {}".format(class_name, "\t".join(values_string_array))



def do_req(method="GET", endpoint="", params={}):
    if method == "GET":
        response = requests.get("{}/{}".format(CONFIG.base_url, endpoint), params=params)
    if method == "POST":
        response = requests.post("{}/{}".format(CONFIG.base_url, endpoint), json=params)
    print("[{}] {} {} -> [{}] {}".format(method, endpoint, params, response.status_code, json.loads(response.text)))
    return {"status_code": response.status_code, "content": json.loads(response.text)}


def start_pulling_loop():
    offset = 0
    while 1:
        updates = do_req(endpoint="getUpdates", params={"offset": offset}).get("content", {}).get("result", [])
        messages = [Incoming_Message(update.get('message')) for update in updates]
        for message in messages:
            do_the_stupid_shit_this_bot_does(message)
        if updates:
            offset = max([update.get("update_id") for update in updates]) + 1
        time.sleep(10)


def start_pulling_loop_v2():
    '''
    sometimes seems that offset = 0 or no offset pulls all messages las 24 hours
    I just let heare the code wile I test a lil bit more
    @TODO QA
    offset = 0
    while 1:
        updates = do_req(endpoint="getUpdates", params={"offset": offset}).get("content", {}).get("result", [])
        messages = [Incoming_Message(update.get('message')) for update in updates]
        if offset:
            for message in messages:
                print(message)
                do_the_stupid_shit_this_bot_does(message)
        if updates:
            offset = max([update.get("update_id") for update in updates])+1
        time.sleep(10)
    '''

def start_flask_api():
    '''
    @TODO
    It should be something like ...
    import flask
    app = flask.Flask("Telegram Flask Api")
    @app.route(CONFIG.incoming_endpoint, methods=['POST'])
    def wrapper():
        return do_the_stupid_shit_this_bot_does()

    app.run(debug=True)
    '''


def check_bot_config():
    response = do_req(endpoint='getMe')
    if response.get("status_code") != 200:
        print(termcolor.colored('[-] bot configuration checker returned: [{}] {}'.format(response.get("status_code"), response.get("content")), 'red'))
        sys.exit()
    else:
        print(termcolor.colored('[+] bot configuration seems ok', 'green'))


def print_help():
    print("there is no help for you \n - Astals")
    sys.exit()


def do_the_stupid_shit_this_bot_does(incoming_message):
    def __compress(input):
        res = ""
        for c in input:
            if c != res[-1:]:
                res = res + c
        return res

    def __leet_decoder(input):
        res = input
        translate_dict = {"b": ["3", "8"], "o": ["0"], "l": ["|"], "m": []}
        for char, leet_codes in translate_dict.items():
            for leet_code in leet_codes:
                res = res.replace(leet_code, char)
        return res

    def __stripper(input):
        return re.sub("[^a-zA-Z]", "", input)


    evals_results = []
    evals_results.append(incoming_message.from_usr_id == CONFIG.vel_usr_id)
    evals_results.append(incoming_message.from_chat_id == CONFIG.dpt_chat_id)
    #@TODO only form mon to fri and from 7 to 12 AM
    #evals_results.append(incoming_message.date == CONFIG.dpt_chat_id)
    #evals_results.append(incoming_message.date == CONFIG.dpt_chat_id)
    decodified_msg = __stripper(__compress(__leet_decoder(unidecode.unidecode(incoming_message.text).lower())))
    evals_results.append("bolomo" in decodified_msg)
    print("{} {}".format(evals_results, decodified_msg))
    if not any(res == False for res in evals_results):
        outgoing_message = Outgoing_Message(chat_id=incoming_message.from_chat_id, text="Medio!", replie_to=incoming_message.message_id)
        do_req(method="POST", endpoint="sendMessage", params={"chat_id": outgoing_message.chat_id, "text":outgoing_message.text, "reply_to_message_id": outgoing_message.reply_to_message_id})



if __name__ == '__main__':
    check_bot_config()
    if CONFIG.incoming_mode == CONFIG.LISTENER_MODE:
        start_flask_api()

    elif CONFIG.incoming_mode == CONFIG.PULLING_MODE:
        start_pulling_loop()

    else:
        print("invalid CONFIG.incoming_mode")
        print_help()


    def test():
        '''
        @TODO
        It should be something like ...
        import unittest
        bolomos = ["bolomo", "Bolomo", "B0lomo", "bolommo please", " booooo ooo lomoo.     o"]
        not_bolomos = []
        for bolomo in bolomos:
            assert....
        '''