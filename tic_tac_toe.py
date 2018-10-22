"""
Tic-Tac-Toe Online
Copyright (C) 2018  Marcell "Mazuh" Guilherme Costa da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

More info on GitHub:    https://github.com/Mazuh/TicTacToeOnline/
"""
import json
import time
import sys
import os

from simple_game_server import client as lib

TITLE_SIGN_POST = '''
 _______ _          _______             _______
|__   __(_)        |__   __|           |__   __|
   | |   _  ___ ______| | __ _  ___ ______| | ___   ___
   | |  | |/ __|______| |/ _` |/ __|______| |/ _ \ / _ \\
   | |  | | (__       | | (_| | (__       | | (_) |  __/
   |_|  |_|\___|      |_|\__,_|\___|      |_|\___/ \___|
                            _ _
                           | (_)
                 ___  _ __ | |_ _ __   ___
                / _ \| '_ \| | | '_ \ / _ \\
               | (_) | | | | | | | | |  __/
                \___/|_| |_|_|_|_| |_|\___|
'''

GAME_OVER_SIGN_POST = '''
  __ _  __ _ _ __ ___   ___    _____   _____ _ __
 / _` |/ _` | '_ ` _ \ / _ \  / _ \ \ / / _ \ '__|
| (_| | (_| | | | | | |  __/ | (_) \ V /  __/ |
 \__, |\__,_|_| |_| |_|\___|  \___/ \_/ \___|_|
  __/ |
 |___/
'''

FIELD_TEMPLATE = '''
    1   2   3
      |   |
    p | p | p   1
  ----*---*----
    p | p | p   2
  ----*---*----
    p | p | p   3
      |   |
'''.replace('p', '{}')

INITIAL_FIELD = [
    ' ', ' ', ' ',
    ' ', ' ', ' ',
    ' ', ' ', ' ',
]

X_MARK = 'x'

O_MARK = 'o'

CREATE_MODE = 'create'

JOIN_MODE = 'join'

def log(message=''):
    sys.stdout.write('{}\n'.format(message))
    sys.stdout.flush()

def log_inline(message=''):
    sys.stdout.write(message)
    sys.stdout.flush()

def read(prompt):
    return raw_input(prompt).lower().strip()

def read_option(prompt, availables,
                error_message='(Invalid input. Try again!)'):
    while True:
        tried = read(prompt)
        if tried not in availables:
            log(error_message)
        else:
            return tried

def clear_logs():
    os.system('clear || cls')

def select_some_room(client):
    log('Select an available room...')
    rooms = client.get_rooms()
    for room in rooms:
        if room['nb_players'] < room['capacity']:
            log('\t{name} ({nb_players}/{capacity})'.format(**room))
        else:
            log('\t****** (unavailable, full)')

    names = [room['name'] for room in rooms]
    selected = read_option('Your choosen room: ', names)

    for room in rooms:
        if selected == room['name'] and room['nb_players'] < room['capacity']:
            return room['id']
    raise Exception('Weird. Name not available.')

def select_game_mode(client):
    clear_logs()
    log(TITLE_SIGN_POST)
    log('Select how to begin your game...')
    log('\t{} (starts a new room)'.format(CREATE_MODE))
    log('\t{} (enter on an existing room)'.format(JOIN_MODE))

    return read_option('Your choosen mode: ', (CREATE_MODE, JOIN_MODE))

def marking_routine(client, field, player_mark):
    clear_logs()
    show(field)
    log('And where will you put your mark?')
    available_coordinates = [str(n) for n in range(1, 4)]
    selected_x = read_option('Horizontal number: ', available_coordinates)
    selected_y = read_option('Vertical number: ', available_coordinates)
    field = mark(field, player_mark, selected_x, selected_y)
    client.send(field)
    return field

def bootstrap_game_client(server_host='127.0.0.1',
                          server_port_tcp=1234,
                          server_port_udp=1234):
    for client_port_udp in range(1235, 1240):
        try:
            return lib.Client(
                server_host,
                server_port_tcp,
                server_port_udp,
                client_port_udp
            )
        except:
            continue
    raise Exception('Fatal failure, could not initialize client.')

def mark(field, character, x_position, y_position):
    index = (int(x_position) - 1) + ((int(y_position) - 1) * 3)

    def reducer(acc_field, cur_field_enumeration):
        cur_index, cur_value = cur_field_enumeration
        should_update = cur_index == index
        return acc_field + [character if should_update else cur_value]

    return reduce(reducer, enumerate(field), [])

def show(field):
    log(FIELD_TEMPLATE.format(*(field or INITIAL_FIELD)))

def game_over(player_result):
    log(GAME_OVER_SIGN_POST)
    log('Hope you had enjoyed.')
    log('Result: {}'.format(player_result))

def consume_field_from_messages(client):
    messages_set = client.get_messages()

    if len(messages_set) > 1:
        raise Exception('Unexpected messaging overflow.')

    for message_str in messages_set:
        try:
            sender_identifier, field = json.loads(message_str).popitem()
            if sender_identifier != client.identifier:
                return field
        except:
            error = 'Failed to parse received message. {}'.format(message_str)
            raise Exception(error)

    return None

def main():
    client = bootstrap_game_client()

    mode = select_game_mode(client)

    if mode == CREATE_MODE:
        creation = read('Room name: ')
        client.create_room(creation)
        player_mark = X_MARK
        field = None
        log('Now wait. Your partner must enter and play first.')

    if mode == JOIN_MODE:
        selection = select_some_room(client)
        client.join_room(selection)
        player_mark = O_MARK
        field = INITIAL_FIELD

    for _ in range(5):
        while field is None:
            field = consume_field_from_messages(client)
            log_inline('.')
            time.sleep(1)
        else:
            field = marking_routine(client, field, player_mark)
            clear_logs()
            show(field)
            field = None
    else:
        game_over('Exceeded attemptings to end.')

if __name__ == '__main__':
    main()
