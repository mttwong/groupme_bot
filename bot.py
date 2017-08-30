from flask import Flask, request
from .secrets.py import bot_id
import requests
import dice

app = Flask(__name__)

url = 'https://api.groupme.com/v3/bots/post'

def send_message(message):
    data = {
        'text': message,
        'bot_id': bot_id,
    }
    requests.post(url, data=data)

commands = {}

def command(prefix):
    def decorator(func):
        commands[prefix] = func
        return func
    return decorator

@command('echo')
def echo(args):
    message = ' '.join(args[1:])
    send_message(message)

@command('roll')
def roll(args):
    dice_to_roll = args[1:]
    num_dice = len(dice_to_roll)

    if num_dice == 0:
        send_message('USAGE: /roll <dice_type> ...')
    elif num_dice == 1:
        try:
            out = dice.roll(args[1])
        except dice.ParseException:
            send_message("I didn't undserstand that...")

        msg = 'Your roll is:\n{}: {}'.format(args[1], out)
        send_message(msg)
    else:
        msg = 'Your rolls are:\n'
        for outcome in args[1:]:
            try:
                out = dice.roll(outcome)
            except dice.ParseException:
                send_message("I didn't undserstand that...")
            msg += '{}: {}\n'.format(outcome, out)
        send_message(msg[:-1])

@app.route('/', methods=['POST'])
def hello():
    data = request.json

    text = data['text']
    if text.startswith('/'):
        rest = text[1:]
        args = rest.split()

        if args[0] in commands:
            command = args[0]
            commands[command](args)
            
            print('ran {}'.format(command))
            return 'ran {}'.format(command)
        else:
            print('unknown command')
            return 'unknown command'

    print('no command')
    return 'no command'
