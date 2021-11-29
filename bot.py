from AriefbustilloNim import Nim, train
from NimSum import NimSum
import pickle
from telegram import Update, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from functools import wraps
from typing import Union, List
import emoji
import random
import time


heaps_arr = []
session_start = False
choose_heap = False
choose_count = False
time_out = 15
global_thread_heap = 0
timeout_arr = [[], []]


def store_rankings(user_rankings, game_mode):
    rankings_1 = []
    with open('rankings_' + str(game_mode) + '.txt', 'r') as filehandle:
        for line in filehandle:
            currentPlace = line[:-1]
            rankings_1.append(currentPlace)

    rankings_1.append(user_rankings)
    with open('rankings_' + str(game_mode) + '.txt', 'w') as filehandle:
        for listitem in rankings_1:
            filehandle.write('%s\n' % listitem)


def get_rankings():
    rankings_god = []
    rankings_hard = []
    rankings_kids = []
    with open('rankings_god.txt', 'r') as filehandle:
        for line in filehandle:
            currentPlace = line[:-1]
            rankings_god.append(currentPlace)

    with open('rankings_hard.txt', 'r') as filehandle:
        for line in filehandle:
            currentPlace = line[:-1]
            rankings_hard.append(currentPlace)

    with open('rankings_kids.txt', 'r') as filehandle:
        dict_kids = {}
        for line in filehandle:
            currentPlace = line[:-1]
            rankings_kids.append(currentPlace)

    rankings_god.sort()
    rankings_hard.sort()
    rankings_kids.sort()

    # TODO
    return [rankings_god, rankings_hard, rankings_kids]


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


def train_ai(heap_arr, update):
    return train(30000, heap_arr, update)


def build_menu(buttons: List[InlineKeyboardButton], n_cols: int, header_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]] = None, footer_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]] = None) -> List[List[InlineKeyboardButton]]:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons if isinstance(header_buttons, list) else [header_buttons])
    if footer_buttons:
        menu.append(footer_buttons if isinstance(footer_buttons, list) else [footer_buttons])
    return menu


@send_action(ChatAction.TYPING)
def start(update: Update, context: CallbackContext) -> None:
    button_list = [
        InlineKeyboardButton(emoji.emojize(':video_game:') + " Play Now " + emoji.emojize(':video_game:'),
                             callback_data='/start_play'),
        InlineKeyboardButton(emoji.emojize(':trophy:') + " Rankings " + emoji.emojize(':trophy:'),
                             callback_data='/rankings_kids.txt')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    reply_text = "Welcome to jasperw_ge2340_bot!!! \n" \
                 "Developed by WONG Kuen Ching SID:57136079, Github: jkcw \n\n" \
                 "In this chat room, you will play Nim games against an extremely smart AI. Try to beat it and be " \
                 "ranked at the top of the list. \n\n" \
                 "" + emoji.emojize(':straight_ruler:') + "Rules " + emoji.emojize(':straight_ruler:') + "\n" \
                                                                                                         "There will be multiple heaps. Over the heaps, there will be multiple coins. In each round, a player " \
                                                                                                         "can only take coins from one heap, yet the number of coins taken from the heap is not limited. " \
                                                                                                         "The player who takes the last coin will lose. \n\n" \
                                                                                                         "" + emoji.emojize(
        ':kissing_cat:') + " You have the privilege to choose to be the first player or the second player. \n\n" \
                           "" + emoji.emojize(
        ':alarm_clock:') + " In each round, you will have 15 seconds to make the decision. \n\n" \
                           "" + emoji.emojize(':smiling_face_with_open_hands:') + " GOOD LUCK " + emoji.emojize(
        ':grinning_squinting_face:')
    update.message.reply_text(reply_text, reply_markup=reply_markup)


@send_action(ChatAction.TYPING)
@run_async
def play_kids_mode(update: Update, context: CallbackContext) -> None:
    global session_start
    global heaps_arr
    global start
    global sequence
    global start_timeout
    global sequence_selected
    global timeout_arr
    global global_thread_start
    global mode
    global ai
    mode = "kids"
    start_timeout = False
    sequence_selected = False
    if session_start:
        update.message.reply_text("You have already started a game, finish it before you start another one.")
        return None
    session_start = True
    heaps = 3
    heaps_arr.clear()

    for i in range(heaps):
        heaps_arr.append(int(random.randint(3, 19)))
    ai = train_ai(heaps_arr, update)
    start = time.time()

    global game
    game = Nim(heaps_arr)
    res = emoji.emojize(':money_bag:') + "Current Heaps: \n"
    for i, pile in enumerate(game.piles):
        res += f"Heap {i}: {pile}\n"

    update.message.reply_text(res)
    reply_text = "Start First or Second? \n\n" + "/start_first \n" + "/start_second \n"
    update.message.reply_text(reply_text)

    timeout_arr[0].append(0)

    time.sleep(time_out)
    if timeout_arr[0][0] == 0:
        nim_sum = NimSum(heaps_arr, False)
        if nim_sum.get_sequence():
            sequence = 1
            start_timeout = True
            print("DEBUG - start timeout AI round")
            ai_round(update)
        else:
            sequence = 0
            start_timeout = True
            print("DEBUG - start timeout Player round")
            player_round(update)


@run_async
def player_round(update: Update) -> None:
    print(timeout_arr)
    global global_thread_heap
    global available_actions

    update.message.reply_text("Your turn!" + emoji.emojize(':smirking_face:'))
    available_actions = game.available_actions(game.piles)
    time.sleep(0.3)
    update.message.reply_text('Choose Heap:')
    global choose_heap
    choose_heap = True

    timeout_arr[1].append(0)
    local_thread_heap = global_thread_heap
    global_thread_heap += 1

    print(choose_heap)

    time.sleep(time_out)
    if timeout_arr[1][local_thread_heap] == 0:
        print("HEAP - time out")
        for i in range(len(game.piles)):
            if game.piles[i] > 0:
                game.move((i, 1))
                break
        update.message.reply_text(emoji.emojize(':face_with_rolling_eyes:') + f"You have been chosen to take 1 from heap {i}.")
        ai_round(update)


def ai_round(update: Update) -> None:
    clear_thread()

    res = emoji.emojize(':money_bag:') + "Current Heaps: \n"
    for i, pile in enumerate(game.piles):
        if pile != 0:
            res += f"Heap {i}: {pile}\n"
    update.message.reply_text(res)

    update.message.reply_text("AI's Turn" + emoji.emojize(':robot:'))
    pile, count = ai.choose_action(game.piles, epsilon=False)
    game.move((pile, count))
    update.message.reply_text(emoji.emojize(':robot:') + f"AI chose to take {count} from heap {pile}.")

    res = emoji.emojize(':money_bag:') + "Current Heaps: \n"
    for i, pile in enumerate(game.piles):
        if pile != 0:
            res += f"Heap {i}: {pile}\n"
    update.message.reply_text("====================")
    update.message.reply_text(res)

    if heaps_empty():
        button_list = [
            InlineKeyboardButton(emoji.emojize(':memo:') + " Back to Menu " + emoji.emojize(':memo:'), callback_data='/start'),
            InlineKeyboardButton(emoji.emojize(':trophy:') + " Rankings " + emoji.emojize(':trophy:'), callback_data='/rankings_kids.txt')
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        # TODO

        time_spent = str(round(time.time() - start, 3)) + " sec " + update.message.from_user.username
        if mode == 'kids':
            store_rankings(time_spent, 'kids')
            update.message.reply_text("okok, you won:) But it is KIDS mode... Try HARD mode!!" + emoji.emojize(':sleepy_face:'), reply_markup=reply_markup)
        elif mode == 'hard':
            store_rankings(time_spent, 'hard')
            update.message.reply_text("You won, why not try GOD mode" + emoji.emojize(':smiling_face_with_horns:'), reply_markup=reply_markup)
        elif mode == 'god':
            store_rankings(time_spent, 'god')
            update.message.reply_text("You won, LOL!!!!!" + emoji.emojize(':smiling_face_with_heart-eyes:'), reply_markup=reply_markup)
        global session_start
        session_start = False
        return None

    player_round(update)


@run_async
def start_first(update: Update, context: CallbackContext) -> None:
    global start_timeout
    if start_timeout:
        update.message.reply_text("Time out!!! It won't work anymore!!!")
    else:
        timeout_arr[0][0] = 1
        if not start_timeout:
            start_timeout = True
            player_round(update)
        else:
            update.message.reply_text("Expired!!! It won't work anymore!!!")


def start_second(update: Update, context: CallbackContext) -> None:
    global start_timeout
    if start_timeout:
        update.message.reply_text("Time out!!! It won't work anymore!!!")
    else:
        timeout_arr[0][0] = 1
        if not start_timeout:
            start_timeout = True
            ai_round(update)
        else:
            update.message.reply_text("Expired!!! It won't work anymore!!!")


@send_action(ChatAction.TYPING)
@run_async
def play_hard_mode(update: Update, context: CallbackContext) -> None:
    global session_start
    global heaps_arr
    global start
    global sequence
    global start_timeout
    global sequence_selected
    global timeout_arr
    global global_thread_start
    global mode
    global ai
    mode = "hard"
    start_timeout = False
    sequence_selected = False
    if session_start:
        update.message.reply_text("You have already started a game, finish it before you start another one.")
        return None
    session_start = True
    heaps = 6
    heaps_arr.clear()

    for i in range(heaps):
        heaps_arr.append(int(random.randint(3, 19)))
    ai = train_ai(heaps_arr, update)
    start = time.time()

    global game
    game = Nim(heaps_arr)
    res = emoji.emojize(':money_bag:') + "Current Heaps: \n"
    for i, pile in enumerate(game.piles):
        res += f"Heap {i}: {pile}\n"

    update.message.reply_text(res)
    reply_text = "Start First or Second? \n\n" + "/start_first \n" + "/start_second \n"
    update.message.reply_text(reply_text)

    timeout_arr[0].append(0)

    time.sleep(time_out)
    if timeout_arr[0][0] == 0:
        nim_sum = NimSum(heaps_arr, False)
        if nim_sum.get_sequence():
            sequence = 1
            start_timeout = True
            print("DEBUG - start timeout AI round")
            ai_round(update)
        else:
            sequence = 0
            start_timeout = True
            print("DEBUG - start timeout Player round")
            player_round(update)


@send_action(ChatAction.TYPING)
@run_async
def play_god_mode(update: Update, context: CallbackContext) -> None:
    global session_start
    global heaps_arr
    global start
    global sequence
    global start_timeout
    global sequence_selected
    global timeout_arr
    global global_thread_start
    global mode
    global ai
    mode = "god"
    start_timeout = False
    sequence_selected = False
    if session_start:
        update.message.reply_text("You have already started a game, finish it before you start another one.")
        return None
    session_start = True
    heaps = 15
    heaps_arr.clear()

    for i in range(heaps):
        heaps_arr.append(int(random.randint(3, 19)))
    ai = train_ai(heaps_arr, update)
    start = time.time()

    global game
    game = Nim(heaps_arr)
    res = emoji.emojize(':money_bag:') + "Current Heaps: \n"
    for i, pile in enumerate(game.piles):
        res += f"Heap {i}: {pile}\n"

    update.message.reply_text(res)
    reply_text = "Start First or Second? \n\n" + "/start_first \n" + "/start_second \n"
    update.message.reply_text(reply_text)

    timeout_arr[0].append(0)

    time.sleep(time_out)
    if timeout_arr[0][0] == 0:
        nim_sum = NimSum(heaps_arr, False)
        if nim_sum.get_sequence():
            sequence = 1
            start_timeout = True
            print("DEBUG - start timeout AI round")
            ai_round(update)
        else:
            sequence = 0
            start_timeout = True
            print("DEBUG - start timeout Player round")
            player_round(update)


def enter_number(update: Update, context: CallbackContext) -> None:
    print(timeout_arr)
    global choose_heap
    global choose_count
    global global_thread_count
    global selected_heap
    global heap_selected
    global count_selected
    if choose_heap:
        try:
            heap = eval(update.message.text)
        except:
            update.message.reply_text("Please enter an integer!!")
            heap = -1
        if not isinstance(heap, int):
            update.message.reply_text("Please enter an integer!! Choose heap again:")
        elif heap > (len(game.piles) - 1) or heap < 0:
            update.message.reply_text("Invalid move! Choose heap again:")
        elif game.piles[heap] == 0:
            update.message.reply_text("Invalid move! Choose heap again:")
        else:
            selected_heap = heap

            choose_heap = False
            choose_count = True
            update.message.reply_text("Choose Count:")
    elif choose_count:
        try:
            count = eval(update.message.text)
        except:
            update.message.reply_text("Please enter an integer!!")
            count = -1
        if not isinstance(count, int):
            update.message.reply_text("Please enter an integer!! Choose count again:")
        elif count > game.piles[selected_heap]:
            update.message.reply_text("Invalid move! Choose count again:")
        elif count <= 0:
            update.message.reply_text("Invalid move! Choose count again:")
        else:
            count_selected = True
            choose_count = False
            choose_heap = False
            game.move((selected_heap, count))
            clear_thread()

            if heaps_empty():
                button_list = [
                    InlineKeyboardButton(emoji.emojize(':memo:') + " Back to Menu " + emoji.emojize(':memo:'), callback_data='/start'),
                    InlineKeyboardButton(emoji.emojize(':trophy:') + " Rankings " + emoji.emojize(':trophy:'), callback_data='/rankings_kids.txt')
                ]
                reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
                update.message.reply_text("You lost, NOOB!!!!!" + emoji.emojize(':yawning_face:'), reply_markup=reply_markup)
                global session_start
                session_start = False
                return None

            update.message.reply_text("====================")

            ai_round(update)


def heaps_empty():
    if sum(game.piles) == 0:
        return True
    else:
        return False


def clear_thread():
    global timeout_arr
    for sub_arr in timeout_arr:
        for i in range(len(sub_arr)):
            sub_arr[i] = 1
    return None


def start_callback_return(query) -> None:
    button_list = [
        InlineKeyboardButton(emoji.emojize(':video_game:') + " Play Now " + emoji.emojize(':video_game:'),
                             callback_data='/start_play'),
        InlineKeyboardButton(emoji.emojize(':trophy:') + " Rankings " + emoji.emojize(':trophy:'),
                             callback_data='/rankings_kids.txt')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    reply_text = "Welcome to jasperw_ge2340_bot!!! \n" \
                 "Developed by WONG Kuen Ching SID:57136079, Github: jkcw \n\n" \
                 "In this chat room, you will play Nim games against an extremely smart AI. Try to beat it and be " \
                 "ranked at the top of the list. \n\n" \
                 "" + emoji.emojize(':straight_ruler:') + "Rules " + emoji.emojize(':straight_ruler:') + "\n" \
                                                                                                         "There will be multiple heaps. Over the heaps, there will be multiple coins. In each round, a player " \
                                                                                                         "can only take coins from one heap, yet the number of coins taken from the heap is not limited. " \
                                                                                                         "The player who takes the last coin will lose. \n\n" \
                                                                                                         "" + emoji.emojize(
        ':kissing_cat:') + " You have the privilege to choose to be the first player or the second player. \n\n" \
                           "" + emoji.emojize(
        ':alarm_clock:') + " In each round, you will have 15 seconds to make the decision. \n\n" \
                           "" + emoji.emojize(':smiling_face_with_open_hands:') + " GOOD LUCK " + emoji.emojize(
        ':grinning_squinting_face:')
    query.edit_message_text(reply_text, reply_markup=reply_markup)


def rankings(query) -> None:
    button_list = [
        InlineKeyboardButton(emoji.emojize(':memo:') + " Back to Menu " + emoji.emojize(':memo:'), callback_data='/start')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    lst = get_rankings()
    reply_text = ""
    cnt = 0
    for mode_arr in lst:
        if cnt == 0:
            reply_text += emoji.emojize(':trophy:') + "GOD MODE RANKINGS" + emoji.emojize(':smiling_face_with_sunglasses:') + "\n"
        elif cnt == 1:
            reply_text += emoji.emojize(':thumbs_up:') + "HARD MODE RANKINGS" + emoji.emojize(':winking_face:') + "\n"
        elif cnt == 2:
            reply_text += emoji.emojize(':baby_medium-light_skin_tone:') + "KIDS MODE RANKINGS" + emoji.emojize(':baby_bottle:') + "\n"
        for i in range(len(mode_arr)):
            if i < 10:
                reply_text += "Top " + str(i + 1) + ": " + mode_arr[i] + "\n"
        reply_text += "\n"
        cnt += 1
    query.edit_message_text(reply_text, reply_markup=reply_markup)


def start_play(query) -> None:
    button_list = [
        InlineKeyboardButton(emoji.emojize(':baby:') + " Kids Mode " + emoji.emojize(':baby:'),
                             callback_data='/play_kids_mode'),
        InlineKeyboardButton(
            emoji.emojize(':fearful_face:') + " Hard Mode " + emoji.emojize(':anxious_face_with_sweat:'),
            callback_data='/play_hard_mode'),
        InlineKeyboardButton(
            emoji.emojize(':smirking_face:') + " GOD Mode " + emoji.emojize(':face_with_hand_over_mouth:'),
            callback_data='/play_god_mode'),
        InlineKeyboardButton(emoji.emojize(':memo:') + " Back to Menu " + emoji.emojize(':memo:'),
                             callback_data='/start')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    reply_text = "" + emoji.emojize(':warning:') + " WARNING " + emoji.emojize(':warning:') + "\n\n" \
                                                                                              "Don't try to choose GOD mode, cause YOU MUST LOSE" + emoji.emojize(
        ':full_moon_face:') + emoji.emojize(':full_moon_face:')
    query.edit_message_text(reply_text, reply_markup=reply_markup)


def start_game(query, mode) -> None:
    button_list = [
        InlineKeyboardButton(emoji.emojize(':memo:') + " Back to Menu " + emoji.emojize(':memo:'),
                             callback_data='/start')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    mode_text = mode.split('_')[1]
    reply_text = "You have chosen " + mode_text + " mode \n\n" \
                 "Please make sure you are ready for the game, since you only have 15 seconds each round!!! " + emoji.emojize(':face_exhaling:') + emoji.emojize(':hot_face:') + " \n\n" \
                 "If you are ready, please click the command below: " + emoji.emojize(':smiling_face_with_sunglasses:') + "\n" + mode
    query.edit_message_text(reply_text, reply_markup=reply_markup)


def callback_handler(update: Update, context: CallbackContext) -> None:
    start_menu = ['/start', '/rankings_kids.txt', '/start_play']
    play_menu = ['/play_kids_mode', '/play_hard_mode', '/play_god_mode']
    query = update.callback_query
    if query.data in start_menu:
        if query.data == '/rankings_kids.txt':
            rankings(query=query)
        elif query.data == '/start_play':
            start_play(query=query)
        elif query.data == '/start':
            start_callback_return(query=query)

    elif query.data in play_menu:
        chat_id = update.callback_query.from_user.id
        if query.data == '/play_kids_mode':
            start_game(query, '/play_kids_mode')
        elif query.data == '/play_hard_mode':
            start_game(query, '/play_hard_mode')
        elif query.data == '/play_god_mode':
            start_game(query, '/play_god_mode')


updater = Updater('TOKEN')

updater.dispatcher.logger.addFilter((lambda s: not s.msg.endswith('A TelegramError was raised while processing the Update')))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('play_kids_mode', play_kids_mode))
updater.dispatcher.add_handler(CommandHandler('play_hard_mode', play_hard_mode))
updater.dispatcher.add_handler(CommandHandler('play_god_mode', play_god_mode))
updater.dispatcher.add_handler(CommandHandler('start_first', start_first))
updater.dispatcher.add_handler(CommandHandler('start_second', start_second))
updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

updater.dispatcher.add_handler(MessageHandler(Filters.text, enter_number))

updater.start_polling()
updater.idle()
