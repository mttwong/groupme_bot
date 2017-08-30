from flask import Flask, request
from .secrets import bot_id
import requests
import dice

url = 'https://api.groupme.com/v3/bots/post'

class GroupMeBot(Flask):
    def __init__(self, name, key):
        self.commands = {} 
        self.key = key 
        super().__init__(name)

    def send_message(self, message):
        data = {
            'text': message,
            'bot_id': self.key,
        }
        requests.post(url, data=data)

    def command(self, prefix):
        def decorator(func):
            self.commands[prefix] = func
            return func
        return decorator

bot = GroupMeBot(__name__, bot_id)

@bot.route('/', methods=['POST'])
def index():
    data = request.json

    text = data['text']
    if text.startswith('/'):
        rest = text[1:]
        args = rest.split()

        if args[0] in bot.commands:
            command = args[0]
            bot.commands[command](args)
            
            print('ran {}'.format(command))
            return 'ran {}'.format(command)
        else:
            print('unknown command')
            return 'unknown command'

    print('no command')
    return 'no command'

@bot.command('echo')
def echo(args):
    message = ' '.join(args[1:])
    bot.send_message(message)

@bot.command('roll')
def roll(args):
    dice_to_roll = args[1:]
    num_dice = len(dice_to_roll)

    if num_dice == 0:
        bot.send_message('USAGE: /roll <dice_type> ...')
    elif num_dice == 1:
        try:
            out = dice.roll(args[1])
        except dice.ParseException:
            bot.send_message("I didn't undserstand that...")

        msg = 'Your roll is:\n{}: {}'.format(args[1], out)
        bot.send_message(msg)
    else:
        msg = 'Your rolls are:\n'
        for outcome in args[1:]:
            try:
                out = dice.roll(outcome)
            except dice.ParseException:
                bot.send_message("I didn't undserstand that...")
            msg += '{}: {}\n'.format(outcome, out)
        bot.send_message(msg[:-1])

