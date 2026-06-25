#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════╗
║         ПОДВАЛ БЕЗУМИЯ                       ║
║      Текстовая хоррор-игра                   ║
╚══════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import random
import textwrap
import pickle
from datetime import datetime

# ─── ANSI коды ────────────────────────────────────────────────
class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    BLINK   = "\033[5m"

    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    BG_RED    = "\033[41m"
    BG_BLACK  = "\033[40m"
    BG_GREEN  = "\033[42m"

    GRAY      = "\033[90m"
    L_RED     = "\033[91m"
    L_GREEN   = "\033[92m"
    L_YELLOW  = "\033[93m"
    L_BLUE    = "\033[94m"
    L_MAGENTA = "\033[95m"
    L_CYAN    = "\033[96m"

C = Color

# ─── Утилиты вывода ───────────────────────────────────────────

TERM_WIDTH = 70

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def hr(char="═", color=C.GRAY):
    print(color + char * TERM_WIDTH + C.RESET)

def slow_print(text, delay=0.03, color=""):
    for ch in text:
        print(color + ch + C.RESET, end="", flush=True)
        time.sleep(delay)
    print()

def flicker_print(text, color=C.L_RED):
    for _ in range(3):
        print(color + text + C.RESET, end="\r", flush=True)
        time.sleep(0.07)
        print(" " * len(text), end="\r", flush=True)
        time.sleep(0.05)
    print(color + text + C.RESET)

def box_print(text, color=C.CYAN, width=TERM_WIDTH):
    lines = textwrap.wrap(text, width - 4)
    top    = color + "╔" + "═" * (width - 2) + "╗" + C.RESET
    bottom = color + "╚" + "═" * (width - 2) + "╝" + C.RESET
    print(top)
    for line in lines:
        padding = width - 2 - len(line)
        print(color + "║ " + C.RESET + line + " " * padding + color + "║" + C.RESET)
    print(bottom)

def narrative(text, delay=0.018, color=C.WHITE):
    lines = textwrap.wrap(text, TERM_WIDTH)
    for line in lines:
        slow_print(line, delay=delay, color=color)

def spooky(text):
    narrative(text, delay=0.025, color=C.L_RED)

def whisper(text):
    narrative("  " + text + "  ", delay=0.04, color=C.GRAY + C.DIM)

def sound(text):
    print(C.YELLOW + C.DIM + "  [ " + text + " ]" + C.RESET)

def jumpscare(text):
    clear()
    time.sleep(0.1)
    print("\n" * 5)
    print(C.BG_RED + C.WHITE + C.BOLD + " " * ((TERM_WIDTH - len(text)) // 2) + text + " " * ((TERM_WIDTH - len(text)) // 2) + C.RESET)
    time.sleep(1.2)
    input(C.GRAY + "\n  [нажмите Enter, чтобы продолжить...]" + C.RESET)
    clear()

def sanity_distort(text, sanity):
    """Искажает текст при низком рассудке."""
    if sanity > 40:
        return text
    chars = list(text)
    intensity = max(0, (40 - sanity) / 40.0)
    glitch_chars = "̷̵̶̴̸̡̢̧̨̛̖̗̘̙̜̝̞̟̠̣̤̥̦̩̪̫̬̭̮̯̰̱̲̳"
    for i in range(len(chars)):
        if random.random() < intensity * 0.3 and chars[i] not in " \n":
            chars[i] = chars[i] + random.choice(glitch_chars)
    return "".join(chars)

def hallucination_message(sanity):
    """Случайная галлюцинация при низком рассудке."""
    if sanity > 30:
        return
    msgs = [
        "Ты слышишь своё имя. Кто-то шепчет из-за стены.",
        "На секунду тебе кажется, что в тёмном углу кто-то стоит. Потом — ничего.",
        "Твои руки. Они движутся сами по себе? Нет. Просто усталость.",
        "ОН ЗДЕСЬ. Нет. Никого нет. ОН ВСЕГДА ЗДЕСЬ.",
        "Числа на стенах складываются во что-то. Ты не можешь разобрать.",
        "Запах озона и старой крови. Откуда он?",
        "Дверь была закрыта. Теперь открыта. Ты её не открывал.",
    ]
    if random.random() < 0.4:
        print()
        whisper(random.choice(msgs))
        print()

# ─── СИСТЕМА БЛУЖДАЮЩЕЙ СУЩНОСТИ ──────────────────────────────

# Комнаты, куда Тень никогда не заходит
ENTITY_SAFE_ROOMS = {"вход", "выход"}

# Ходы предупреждения перед появлением сущности
ENTITY_ACTIVATE_TURN = 8

# Звуки приближения Тени (слышны когда она в соседней комнате)
ENTITY_NEAR_SOUNDS = [
    "Где-то рядом — тяжёлые, медленные шаги. Не человеческие.",
    "Тихий скрежет по стене. Близко. Очень близко.",
    "Ты чувствуешь запах — гниль и что-то сладковатое. Он нарастает.",
    "Из-за стены слышен долгий выдох. Нечеловеческий.",
    "Что-то касается двери с той стороны. Один раз. Два. Три.",
    "Тень пробегает по стене — там, где нет источника света.",
]

# Тексты встречи (Тень в той же комнате)
ENTITY_ENCOUNTER_SCARES = [
    "ОНО ЗДЕСЬ",
    "НЕ СМОТРИ НА НЕГО",
    "БЕГИ",
    "ОН ВИДИТ ТЕБЯ",
]

ENTITY_ENCOUNTER_TEXTS = [
    (
        "Из темноты появляется фигура. Высокая — слишком высокая. "
        "Без лица. Без звука. Она просто стоит и смотрит туда, где твоё лицо должно быть. "
        "Ноги отказывают. Ты разворачиваешься и бежишь."
    ),
    (
        "Ты чувствуешь его раньше, чем видишь — холод охватывает тебя, как вода. "
        "Потом оно поворачивается. У него нет глаз. Но оно видит тебя. "
        "Ты бежишь. Ты не помнишь, как оказался в другой комнате."
    ),
    (
        "Кто-то стоит в углу. Спиной к тебе. Слишком неподвижно. "
        "Потом голова медленно поворачивается — неестественно, слишком далеко. "
        "Ты видишь не лицо. Просто темноту. И ты бежишь."
    ),
    (
        "Лампа мигает. В миг темноты — оно рядом. В миг света — "
        "пусто, но твоё плечо горит там, где оно коснулось. "
        "Ты уже на бегу, не понимая когда начал."
    ),
]

def entity_adjacent_rooms(room_name):
    """Возвращает список комнат, смежных с данной."""
    return list(ROOMS[room_name]["exits"].values())

def move_entity(state):
    """Перемещает Тень по подвалу каждые N ходов."""
    wander_rooms = [r for r in ROOMS if r not in ENTITY_SAFE_ROOMS]
    if not state.entity_active:
        if state.turns >= ENTITY_ACTIVATE_TURN:
            # Активируем — спавним в случайной комнате, подальше от игрока
            candidates = [
                r for r in wander_rooms
                if r != state.current_room
                and r not in entity_adjacent_rooms(state.current_room)
            ]
            if not candidates:
                candidates = [r for r in wander_rooms if r != state.current_room]
            state.entity_room = random.choice(candidates) if candidates else "морг"
            state.entity_active = True
        return

    state.entity_move_counter += 1
    # Интервал движения уменьшается с каждой встречей (становится быстрее)
    interval = max(2, 4 - state.entity_encounters)
    if state.entity_move_counter < interval:
        return
    state.entity_move_counter = 0

    # Выбираем следующую комнату для Тени
    current = state.entity_room
    adjacent = [
        r for r in entity_adjacent_rooms(current)
        if r not in ENTITY_SAFE_ROOMS
    ]
    if not adjacent:
        return

    # Тень тяготеет к игроку: с вероятностью 55% движется в сторону игрока
    player_room = state.current_room
    toward_player = [r for r in adjacent if player_room in entity_adjacent_rooms(r) or r == player_room]

    if toward_player and random.random() < 0.55:
        state.entity_room = random.choice(toward_player)
    else:
        state.entity_room = random.choice(adjacent)

def entity_proximity(state):
    """Возвращает: 'here' | 'near' | 'far'"""
    if not state.entity_active or not state.entity_room:
        return "far"
    if state.entity_room == state.current_room:
        return "here"
    if state.entity_room in entity_adjacent_rooms(state.current_room):
        return "near"
    return "far"

def check_entity_encounter(state):
    """Проверяет встречу с Тенью и обрабатывает её."""
    if entity_proximity(state) != "here":
        return

    # Встреча!
    time.sleep(0.3)
    scare_text = random.choice(ENTITY_ENCOUNTER_SCARES)
    encounter_text = random.choice(ENTITY_ENCOUNTER_TEXTS)

    jumpscare(scare_text)

    spooky(encounter_text)
    time.sleep(0.8)

    # Потеря рассудка зависит от того, сколько уже было встреч
    drain = 20 + state.entity_encounters * 5
    state.drain_sanity(drain)
    state.entity_encounters += 1

    # Принудительное бегство: переносим игрока в случайную смежную комнату
    adjacent = entity_adjacent_rooms(state.current_room)
    safe_adjacent = [r for r in adjacent if r != state.entity_room]
    if safe_adjacent:
        flee_room = random.choice(safe_adjacent)
    elif adjacent:
        flee_room = random.choice(adjacent)
    else:
        flee_room = "вход"

    print()
    spooky(f"Ты в панике вырываешься в {ROOMS[flee_room]['name']}.")
    time.sleep(0.5)

    state.current_room = flee_room
    state.turns += 1

    # Тень остаётся там, где была встреча, потом случайно уходит
    adj_entity = [
        r for r in entity_adjacent_rooms(state.entity_room)
        if r not in ENTITY_SAFE_ROOMS and r != flee_room
    ]
    if adj_entity:
        state.entity_room = random.choice(adj_entity)

    print()
    input(C.GRAY + "  [нажмите Enter, чтобы прийти в себя...]" + C.RESET)

# ─── ПРЕДМЕТЫ ─────────────────────────────────────────────────

ITEMS = {
    "ржавый ключ": {
        "name": "ржавый ключ",
        "desc": "Тяжёлый ключ с биркой «ПАЛАТА №7». Покрыт бурыми пятнами.",
        "emoji": "🗝️",
        "combinable": None,
        "usable_in": ["палата №7", "коридор б"],
        "quest_item": True,
    },
    "канистра": {
        "name": "канистра",
        "desc": "Пустая металлическая канистра. Пахнет бензином.",
        "emoji": "🪣",
        "combinable": "бензин",
        "usable_in": [],
        "quest_item": False,
    },
    "бензин": {
        "name": "бензин",
        "desc": "Небольшой запас бензина в пластиковой бутылке. Ещё свежий.",
        "emoji": "🛢️",
        "combinable": "канистра",
        "usable_in": [],
        "quest_item": False,
    },
    "канистра с бензином": {
        "name": "канистра с бензином",
        "desc": "Канистра, заполненная бензином. Готова к использованию.",
        "emoji": "⛽",
        "combinable": None,
        "usable_in": ["электрощитовая"],
        "quest_item": True,
    },
    "скальпель": {
        "name": "скальпель",
        "desc": "Медицинский скальпель. Острый, несмотря на ржавчину.",
        "emoji": "🔪",
        "combinable": None,
        "usable_in": ["изолятор"],
        "quest_item": False,
    },
    "записка главврача": {
        "name": "записка главврача",
        "desc": "Скомканная бумага. Написано: «Код сейфа: 3-7-2-1. Никто не должен знать.»",
        "emoji": "📝",
        "combinable": None,
        "usable_in": [],
        "quest_item": True,
    },
    "фонарик": {
        "name": "фонарик",
        "desc": "Старый фонарик. Батарейки почти сели, но работает.",
        "emoji": "🔦",
        "combinable": None,
        "usable_in": [],
        "quest_item": False,
        "gives_sanity": 10,
    },
    "успокоительное": {
        "name": "успокоительное",
        "desc": "Таблетка из склада. Восстанавливает рассудок.",
        "emoji": "💊",
        "combinable": None,
        "usable_in": [],
        "quest_item": False,
        "gives_sanity": 25,
        "consumable": True,
    },
    "железный прут": {
        "name": "железный прут",
        "desc": "Кусок арматуры. Можно использовать как рычаг или оружие.",
        "emoji": "🔩",
        "combinable": None,
        "usable_in": ["кабинет главврача"],
        "quest_item": False,
    },
    "магнитофонная лента": {
        "name": "магнитофонная лента",
        "desc": "Старая кассета с подписью «Сеанс 48-Б. Пациент Икс. СЕКРЕТНО».",
        "emoji": "📼",
        "combinable": None,
        "usable_in": ["процедурная"],
        "quest_item": False,
        "lore": True,
    },
    "карточка пациента": {
        "name": "карточка пациента",
        "desc": "Карточка пациента №48. «Диагноз: острый психоз. Пациент утверждает, что слышит голоса из подвала. Рекомендована изоляция.»",
        "emoji": "📋",
        "combinable": None,
        "usable_in": [],
        "quest_item": False,
        "lore": True,
    },
    "ключ выхода": {
        "name": "ключ выхода",
        "desc": "Большой ключ с табличкой «ВЫХОД». Долгожданный.",
        "emoji": "🔑",
        "combinable": None,
        "usable_in": ["выход"],
        "quest_item": True,
    },
}

# ─── КОМНАТЫ ──────────────────────────────────────────────────

ROOMS = {
    "вход": {
        "name": "Вход в подвал",
        "emoji": "🚪",
        "desc": (
            "Ты очнулся на холодном бетонном полу. Голова раскалывается. "
            "Подвал психиатрической больницы окружает тебя со всех сторон — сырые, "
            "покрытые плесенью стены, редкие аварийные лампы, мигающие в агонии. "
            "Запах сырости, хлорки и чего-то неуловимо органического бьёт в ноздри. "
            "Где-то далеко капает вода. Где-то ещё дальше — скрип. "
            "Ты не помнишь, как сюда попал. Но одно знаешь точно: нужно выбраться."
        ),
        "exits": {
            "север": "коридор а",
            "восток": "процедурная",
        },
        "items": ["фонарик"],
        "dark": False,
        "visited": False,
        "sanity_drain": 0,
        "events": [
            "Лампа над твоей головой мигает трижды и гаснет. Потом снова загорается.",
            "За стеной что-то скребётся. Потом — тишина.",
        ],
        "first_visit_text": (
            "Позади — лестница вверх. Она заблокирована рухнувшей балкой. "
            "Выход только вперёд. Всегда только вперёд."
        ),
    },
    "коридор а": {
        "name": "Коридор А",
        "emoji": "🌑",
        "desc": (
            "Длинный коридор уходит в темноту. Стены покрыты облупившейся краской "
            "и старыми граффити — пациенты царапали что-то ногтями. «ПОМОГИТЕ», "
            "«НЕ СПИТЕ», «ОН СЛЫШИТ ВСЁ» — читаешь ты, и по спине бежит холод. "
            "Под ногами хрустит битое стекло и какая-то труха."
        ),
        "exits": {
            "юг": "вход",
            "север": "палата №7",
            "запад": "электрощитовая",
            "восток": "коридор б",
        },
        "items": [],
        "dark": True,
        "visited": False,
        "sanity_drain": 3,
        "events": [
            "В дальнем конце коридора что-то мелькнуло. Тень? Крыса? Или...",
            "Шаги. Тяжёлые. Откуда-то сверху. Кто-то ходит по первому этажу. Или нет.",
            "Ты слышишь детский смех. Он обрывается так же внезапно, как и начался.",
        ],
        "first_visit_text": None,
    },
    "палата №7": {
        "name": "Старая палата №7",
        "emoji": "🛏️",
        "desc": (
            "Бывшая палата для пациентов. Три ржавые кровати с порванными матрасами. "
            "На стенах — рисунки, сделанные чем-то тёмным: спирали, глаза, фигуры "
            "без лиц. На одной из кроватей лежит скомканный халат. "
            "В углу — перевёрнутая тумбочка. На полу — бурые пятна, которые "
            "ты предпочитаешь не идентифицировать. "
            "Запах старой мочи, страха и чего-то сладковатого, тошнотворного."
        ),
        "exits": {
            "юг": "коридор а",
        },
        "items": ["ржавый ключ", "карточка пациента"],
        "dark": True,
        "visited": False,
        "sanity_drain": 5,
        "events": [
            "Кровать скрипит. Сама. Потом — тишина.",
            "На рисунке на стене ты замечаешь фигуру, которой раньше не было. Или была?",
            "Из-под кровати тянет холодом. Ты не смотришь под кровать. Ты не будешь смотреть.",
        ],
        "first_visit_text": (
            "Это место видело многое. Стены помнят крики, которые никто не слышал."
        ),
        "quest_trigger": "quest_1",
    },
    "процедурная": {
        "name": "Процедурная",
        "emoji": "🏥",
        "desc": (
            "Операционная или процедурный кабинет — стол с кожаными ремнями по-прежнему "
            "стоит посередине. Ремни потемнели и потрескались. Медицинские инструменты "
            "разбросаны по полу, некоторые — явно сломаны. Старый магнитофон на тумбочке. "
            "Шкаф с разбитым стеклом. Запах спирта и ржавчины."
        ),
        "exits": {
            "запад": "вход",
            "север": "коридор б",
            "восток": "склад медикаментов",
        },
        "items": ["скальпель", "магнитофонная лента"],
        "dark": False,
        "visited": False,
        "sanity_drain": 4,
        "events": [
            "Ремни на операционном столе слегка покачиваются. Без сквозняка.",
            "Магнитофон трещит. Ты слышишь отрывок: «...пациент не реагирует на...» — и тишина.",
        ],
        "first_visit_text": None,
    },
    "коридор б": {
        "name": "Коридор Б",
        "emoji": "🌑",
        "desc": (
            "Более узкий коридор. Потолок здесь ниже, трубы ближе. "
            "Из одной трубы капает что-то тёмное — надеешься, что это вода. "
            "Запахи здесь гуще, тяжелее. Двери с обеих сторон заперты — все, кроме одной."
        ),
        "exits": {
            "запад": "коридор а",
            "юг": "процедурная",
            "север": "морг",
        },
        "items": ["железный прут"],
        "dark": True,
        "visited": False,
        "sanity_drain": 5,
        "events": [
            "Одна из запертых дверей ударяется изнутри. Один раз. Больше — ни звука.",
            "Ты слышишь дыхание. Не своё.",
        ],
        "first_visit_text": None,
    },
    "электрощитовая": {
        "name": "Электрощитовая",
        "emoji": "⚡",
        "desc": (
            "Щитовая заполнена старыми рубильниками, перегоревшими предохранителями "
            "и паутиной. В центре — дизельный генератор, старый, но, возможно, ещё рабочий. "
            "В воздухе пахнет озоном и палёной проводкой. "
            "На стене — схема электроснабжения больницы. Большинство секций помечены красным: «АВАРИЙНО»."
        ),
        "exits": {
            "восток": "коридор а",
        },
        "items": ["канистра"],
        "dark": True,
        "visited": False,
        "sanity_drain": 2,
        "events": [
            "Рубильник сам по себе переключается. Потом возвращается обратно.",
            "Генератор издаёт глухой стон. Как будто хочет что-то сказать.",
        ],
        "first_visit_text": None,
        "quest_trigger": "quest_2",
    },
    "склад медикаментов": {
        "name": "Склад медикаментов",
        "emoji": "💊",
        "desc": (
            "Длинные стеллажи с опрокинутыми и разбитыми флаконами. "
            "Большинство лекарств давно просрочено или испорчено. "
            "Запах химии, кислоты и плесени смешивается в тошнотворный коктейль. "
            "Где-то в глубине стеллажей можно ещё найти что-нибудь целое."
        ),
        "exits": {
            "запад": "процедурная",
        },
        "items": ["бензин", "успокоительное"],
        "dark": False,
        "visited": False,
        "sanity_drain": 1,
        "events": [
            "Флакон с полки падает сам по себе. Разбивается о пол.",
        ],
        "first_visit_text": (
            "Здесь лечили. Или делали вид, что лечат."
        ),
    },
    "морг": {
        "name": "Морг",
        "emoji": "☠️",
        "desc": (
            "Ты входишь — и холод обнимает тебя как старый знакомый. "
            "Металлические секции для тел — большинство пустые, некоторые задвинуты. "
            "На центральном столе — чьи-то останки, накрытые простынёй. "
            "Ты стараешься не смотреть. Ты смотришь. Лучше бы не смотрел. "
            "На стене написано мелом: «ЦИФРЫ — КЛЮЧ. 3-7-2-1». "
            "В углу — старый сейф."
        ),
        "exits": {
            "юг": "коридор б",
            "север": "изолятор",
        },
        "items": ["записка главврача"],
        "dark": False,
        "visited": False,
        "sanity_drain": 10,
        "events": [
            "Одна из задвинутых секций двигается. Изнутри? Снаружи? Ты не проверяешь.",
            "Простыня на столе медленно сползает. Ты отворачиваешься.",
        ],
        "first_visit_text": (
            "В этой комнате умерли люди. Ты чувствуешь это каждой клеткой тела."
        ),
        "quest_trigger": "quest_3",
        "puzzle": True,
        "puzzle_solved": False,
        "puzzle_answer": "3721",
    },
    "изолятор": {
        "name": "Изолятор",
        "emoji": "🔒",
        "desc": (
            "Комната без окон. Стены обиты мягким материалом — когда-то белым, "
            "теперь жёлто-серым и разодранным. Царапины везде. "
            "«ВЫПУСТИТЕ МЕНЯ», «ОН ПРИХОДИТ НОЧЬЮ», «Я НЕ СУМАСШЕДШИЙ» — "
            "читаешь ты надписи, сделанные чем-то острым, может быть ногтями. "
            "В центре — смирительная рубашка. Пустая. Хочется верить, что пустая."
        ),
        "exits": {
            "юг": "морг",
            "север": "кабинет главврача",
        },
        "items": [],
        "dark": True,
        "visited": False,
        "sanity_drain": 12,
        "events": [
            "Дверь за тобой на секунду закрывается. Сама открывается. Ты не дышишь.",
            "Надписи на стене. Ты мог бы поклясться, что секунду назад их было меньше.",
        ],
        "first_visit_text": (
            "Здесь держали тех, кого боялись. Или тех, кто знал слишком много."
        ),
    },
    "кабинет главврача": {
        "name": "Кабинет главного врача",
        "emoji": "🖊️",
        "desc": (
            "Просторный кабинет. Массивный стол, перевёрнутое кожаное кресло. "
            "Стены увешаны дипломами и фотографиями — на всех лицах вырезаны глаза. "
            "Шкаф взломан и пуст. На столе — разбросанные бумаги, пепельница, "
            "и маленький сейф, приваренный к раме стола. "
            "Запах сигарного дыма — давнего, но будто бы только что."
        ),
        "exits": {
            "юг": "изолятор",
            "север": "выход",
        },
        "items": [],
        "dark": False,
        "visited": False,
        "sanity_drain": 6,
        "events": [
            "Фотографии. Ты мог бы поклясться — одна из них повернулась.",
            "Бумаги на столе шелестят. Ни одного сквозняка.",
        ],
        "first_visit_text": (
            "Тот, кто сидел здесь, принимал решения. Страшные решения."
        ),
        "quest_trigger": "quest_4",
        "locked": True,
        "lock_item": "железный прут",
    },
    "выход": {
        "name": "Аварийный выход",
        "emoji": "🚪",
        "desc": (
            "Металлическая дверь с красным знаком «ВЫХОД». "
            "Она заперта на массивный замок. "
            "Сквозь щели пробивается свежий воздух снаружи. "
            "Ты так давно не дышал нормальным воздухом."
        ),
        "exits": {
            "юг": "кабинет главврача",
        },
        "items": [],
        "dark": False,
        "visited": False,
        "sanity_drain": 0,
        "events": [],
        "first_visit_text": None,
        "is_exit": True,
    },
}

# ─── КВЕСТЫ ───────────────────────────────────────────────────

QUESTS = {
    "quest_1": {
        "id": "quest_1",
        "name": "Найти ключ",
        "desc": "В старой палате должен быть ключ. Осмотри всё.",
        "completed": False,
        "trigger_room": "палата №7",
        "complete_condition": lambda inv: "ржавый ключ" in inv,
        "complete_msg": "Ты нашёл ржавый ключ. Он откроет путь через Коридор Б.",
    },
    "quest_2": {
        "id": "quest_2",
        "name": "Запустить генератор",
        "desc": "Генератор в электрощитовой нужно заправить. Найди топливо.",
        "completed": False,
        "trigger_room": "электрощитовая",
        "complete_condition": lambda inv: "канистра с бензином" in inv,
        "complete_msg": "Генератор запущен. Некоторые двери теперь открыты.",
    },
    "quest_3": {
        "id": "quest_3",
        "name": "Решить головоломку морга",
        "desc": "В морге есть сейф с кодом. Найди четырёхзначный код.",
        "completed": False,
        "trigger_room": "морг",
        "complete_condition": lambda inv: "ключ выхода" not in inv,
        "complete_msg": "Сейф открыт. Ты нашёл то, что искал.",
    },
    "quest_4": {
        "id": "quest_4",
        "name": "Найти ключ от выхода",
        "desc": "Ключ выхода должен быть в кабинете главврача. Войди туда.",
        "completed": False,
        "trigger_room": "кабинет главврача",
        "complete_condition": lambda inv: "ключ выхода" in inv,
        "complete_msg": "Ключ выхода у тебя. Выход рядом.",
    },
}

# ─── СОСТОЯНИЕ ИГРЫ ───────────────────────────────────────────

class GameState:
    def __init__(self):
        self.current_room   = "вход"
        self.inventory      = []
        self.sanity         = 100
        self.has_flashlight = False
        self.generator_on   = False
        self.turns          = 0
        self.quests         = {k: False for k in QUESTS}
        self.room_visits    = {k: 0 for k in ROOMS}
        self.items_found    = []
        self.dead           = False
        self.won            = False
        self.events_seen    = {k: [] for k in ROOMS}
        self.puzzle_solved  = False
        self.locked_rooms_opened = []
        # Сущность («Тень»)
        self.entity_active        = False
        self.entity_room          = None
        self.entity_move_counter  = 0
        self.entity_encounters    = 0

    def drain_sanity(self, amount):
        if self.has_flashlight:
            room = ROOMS[self.current_room]
            if room.get("dark"):
                amount = max(0, amount - 2)
        self.sanity = max(0, self.sanity - amount)

    def restore_sanity(self, amount):
        self.sanity = min(100, self.sanity + amount)

    def add_item(self, item_name):
        if item_name not in self.inventory:
            self.inventory.append(item_name)

    def remove_item(self, item_name):
        if item_name in self.inventory:
            self.inventory.remove(item_name)

    def has_item(self, item_name):
        return item_name in self.inventory

    def to_dict(self):
        return {
            "current_room": self.current_room,
            "inventory": self.inventory,
            "sanity": self.sanity,
            "has_flashlight": self.has_flashlight,
            "generator_on": self.generator_on,
            "turns": self.turns,
            "quests": self.quests,
            "room_visits": self.room_visits,
            "items_found": self.items_found,
            "dead": self.dead,
            "won": self.won,
            "puzzle_solved": self.puzzle_solved,
            "locked_rooms_opened": self.locked_rooms_opened,
            "entity_active": self.entity_active,
            "entity_room": self.entity_room,
            "entity_move_counter": self.entity_move_counter,
            "entity_encounters": self.entity_encounters,
        }

    @classmethod
    def from_dict(cls, d):
        s = cls()
        s.current_room   = d["current_room"]
        s.inventory      = d["inventory"]
        s.sanity         = d["sanity"]
        s.has_flashlight = d["has_flashlight"]
        s.generator_on   = d["generator_on"]
        s.turns          = d["turns"]
        s.quests         = d["quests"]
        s.room_visits    = d["room_visits"]
        s.items_found    = d.get("items_found", [])
        s.dead           = d.get("dead", False)
        s.won            = d.get("won", False)
        s.puzzle_solved  = d.get("puzzle_solved", False)
        s.locked_rooms_opened = d.get("locked_rooms_opened", [])
        s.entity_active       = d.get("entity_active", False)
        s.entity_room         = d.get("entity_room", None)
        s.entity_move_counter = d.get("entity_move_counter", 0)
        s.entity_encounters   = d.get("entity_encounters", 0)
        return s

# ─── СОХРАНЕНИЕ / ЗАГРУЗКА ────────────────────────────────────

SAVE_FILE = "game/save.json"

def save_game(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
    print(C.GREEN + "  ✓ Игра сохранена." + C.RESET)

def load_game():
    if not os.path.exists(SAVE_FILE):
        print(C.RED + "  Файл сохранения не найден." + C.RESET)
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        state = GameState.from_dict(d)
        print(C.GREEN + "  ✓ Игра загружена." + C.RESET)
        return state
    except Exception as e:
        print(C.RED + f"  Ошибка загрузки: {e}" + C.RESET)
        return None

# ─── ОТОБРАЖЕНИЕ HUD ──────────────────────────────────────────

def show_hud(state):
    room = ROOMS[state.current_room]
    s = state.sanity

    if s > 70:
        s_color = C.L_GREEN
        s_bar   = "█" * (s // 10) + "░" * (10 - s // 10)
    elif s > 40:
        s_color = C.L_YELLOW
        s_bar   = "█" * (s // 10) + "░" * (10 - s // 10)
    elif s > 20:
        s_color = C.L_RED
        s_bar   = "█" * (s // 10) + "░" * (10 - s // 10)
    else:
        s_color = C.RED + C.BLINK
        s_bar   = "▓" * (s // 10) + "░" * (10 - s // 10)

    dark_str = (C.GRAY + " 🌑 ТЕМНО" + C.RESET) if (room.get("dark") and not state.has_flashlight) else ""

    # Индикатор близости Тени
    proximity = entity_proximity(state)
    if proximity == "here":
        entity_str = C.RED + C.BLINK + "  👁 ОНО ЗДЕСЬ" + C.RESET
    elif proximity == "near":
        entity_str = C.L_RED + "  ⚠ ЧТО-ТО РЯДОМ" + C.RESET
    else:
        entity_str = ""

    hr("─")
    print(
        C.CYAN + f"  {room['emoji']} {room['name']}" + C.RESET +
        dark_str + entity_str
    )
    print(
        C.GRAY + "  Рассудок: " + C.RESET +
        s_color + f"[{s_bar}] {s}%" + C.RESET +
        C.GRAY + f"   Ход: {state.turns}" + C.RESET
    )
    hr("─")

def show_room(state):
    room = ROOMS[state.current_room]
    is_dark = room.get("dark") and not state.has_flashlight

    if is_dark:
        spooky(sanity_distort(
            "Темно. Почти полная темнота. Ты слышишь своё дыхание. "
            "Ты двигаешься на ощупь, касаясь мокрых стен.",
            state.sanity
        ))
        if state.sanity < 50:
            whisper("Кто-то здесь. Ты чувствуешь это.")
    else:
        text = room["desc"]
        narrative(sanity_distort(text, state.sanity))

    if state.room_visits[state.current_room] == 0 and room.get("first_visit_text"):
        print()
        whisper(room["first_visit_text"])

    # Выходы
    print()
    exits = room["exits"]
    exit_str = ", ".join([f"{C.L_CYAN}{d}{C.RESET} → {C.WHITE}{ROOMS[r]['name']}{C.RESET}" for d, r in exits.items()])
    print(C.GRAY + "  Выходы: " + C.RESET + exit_str)

    # Предметы
    available_items = [i for i in room.get("items", []) if i not in state.items_found]
    if available_items:
        items_str = ", ".join([f"{ITEMS[i]['emoji']} {i}" for i in available_items if i in ITEMS])
        print(C.YELLOW + "  Видно: " + C.RESET + items_str)

    # Звук приближения Тени (если в соседней комнате)
    if entity_proximity(state) == "near" and random.random() < 0.75:
        print()
        sound(random.choice(ENTITY_NEAR_SOUNDS))
        state.drain_sanity(2)

    # Случайное событие комнаты
    events = room.get("events", [])
    seen = state.events_seen.get(state.current_room, [])
    unseen = [e for e in events if e not in seen]
    if unseen and random.random() < 0.45:
        chosen = random.choice(unseen)
        print()
        sound(chosen)
        state.events_seen[state.current_room].append(chosen)

    state.room_visits[state.current_room] += 1

# ─── ИНВЕНТАРЬ ────────────────────────────────────────────────

def show_inventory(state):
    hr()
    print(C.CYAN + C.BOLD + "  🎒 ИНВЕНТАРЬ" + C.RESET)
    hr()
    if not state.inventory:
        print(C.GRAY + "  Пусто." + C.RESET)
    else:
        for item_name in state.inventory:
            item = ITEMS.get(item_name, {})
            print(f"  {item.get('emoji','▪')} {C.WHITE}{item_name}{C.RESET}")
            print(C.GRAY + f"     {item.get('desc','')}" + C.RESET)
    hr()

def combine_items(state, item1, item2):
    item_data = ITEMS.get(item1, {})
    if item_data.get("combinable") == item2:
        state.remove_item(item1)
        state.remove_item(item2)
        result = item1 + " с " + item2
        # Особые случаи
        if (item1 == "канистра" and item2 == "бензин") or (item1 == "бензин" and item2 == "канистра"):
            result = "канистра с бензином"
        state.add_item(result)
        print(C.L_GREEN + f"  Ты объединил {item1} и {item2} → {result}" + C.RESET)
        return True
    item_data2 = ITEMS.get(item2, {})
    if item_data2.get("combinable") == item1:
        return combine_items(state, item2, item1)
    print(C.GRAY + "  Эти предметы нельзя объединить." + C.RESET)
    return False

# ─── ИСПОЛЬЗОВАНИЕ ПРЕДМЕТОВ ──────────────────────────────────

def use_item(state, item_name):
    if item_name not in state.inventory:
        print(C.GRAY + "  У тебя нет такого предмета." + C.RESET)
        return

    item = ITEMS.get(item_name, {})
    room_name = state.current_room

    # Фонарик
    if item_name == "фонарик":
        if not state.has_flashlight:
            state.has_flashlight = True
            state.restore_sanity(item.get("gives_sanity", 0))
            slow_print("  Ты включаешь фонарик. Луч света прорезает темноту.", color=C.L_YELLOW)
        else:
            print(C.GRAY + "  Фонарик уже включён." + C.RESET)
        return

    # Успокоительное
    if item_name == "успокоительное":
        state.restore_sanity(item.get("gives_sanity", 25))
        state.remove_item("успокоительное")
        slow_print("  Ты глотаешь таблетку. Мир слегка успокаивается.", color=C.L_GREEN)
        return

    # Магнитофонная лента
    if item_name == "магнитофонная лента" and room_name == "процедурная":
        print()
        slow_print("  Ты вставляешь ленту в старый магнитофон. Он хрипит. Начинает играть.", color=C.CYAN)
        time.sleep(0.5)
        print()
        whisper("«Пациент №48 отказывается говорить. Только пишет одно и то же: 'Он живёт в стенах.'»")
        time.sleep(0.5)
        whisper("«Сегодня пациент вскрыл вены. Говорит, что так он 'выпустит его'. Мы не понимаем.»")
        time.sleep(0.5)
        whisper("«Я слышу это сам. Ночью. Я слышу. Боже, я тоже слышу.»")
        print()
        state.drain_sanity(5)
        return

    # Канистра с бензином в щитовой
    if item_name == "канистра с бензином" and room_name == "электрощитовая":
        if not state.generator_on:
            slow_print("  Ты заливаешь бензин в генератор. Дёргаешь рычаг запуска.", color=C.L_YELLOW)
            time.sleep(0.5)
            sound("Кашель. Рёв. РЁВВВВ.")
            slow_print("  Генератор запускается! Свет мигает по всему подвалу.", color=C.L_GREEN)
            state.generator_on = True
            state.remove_item("канистра с бензином")
            # Разблокируем некоторые двери
            state.locked_rooms_opened.append("электрощитовая_gen")
            state.quests["quest_2"] = True
            print()
            print(C.L_GREEN + C.BOLD + "  ✓ КВЕСТ ВЫПОЛНЕН: Запустить генератор" + C.RESET)
        else:
            print(C.GRAY + "  Генератор уже работает." + C.RESET)
        return

    # Ключ в коридоре б (открывает морг)
    if item_name == "ржавый ключ" and room_name in ["коридор б", "коридор а"]:
        if "коридор_б_opened" not in state.locked_rooms_opened:
            slow_print("  Ты используешь ключ на засове в коридоре. Замок поддаётся с трудом.", color=C.L_YELLOW)
            state.locked_rooms_opened.append("коридор_б_opened")
            print(C.L_GREEN + "  Путь в Морг открыт." + C.RESET)
        else:
            print(C.GRAY + "  Этот замок уже открыт." + C.RESET)
        return

    # Железный прут — вскрыть кабинет главврача
    if item_name == "железный прут" and room_name == "изолятор":
        if "кабинет_opened" not in state.locked_rooms_opened:
            slow_print("  Ты используешь прут как рычаг на двери в конце коридора.", color=C.L_YELLOW)
            time.sleep(0.3)
            sound("СКРЕЖЕТ МЕТАЛЛА. Дверь поддаётся.")
            state.locked_rooms_opened.append("кабинет_opened")
            print(C.L_GREEN + "  Кабинет главврача открыт!" + C.RESET)
        else:
            print(C.GRAY + "  Дверь уже открыта." + C.RESET)
        return

    # Ключ выхода
    if item_name == "ключ выхода" and room_name == "выход":
        trigger_ending(state)
        return

    print(C.GRAY + f"  Здесь нет смысла использовать {item_name}." + C.RESET)

# ─── ГОЛОВОЛОМКА МОРГА ────────────────────────────────────────

def run_puzzle(state):
    if state.puzzle_solved:
        print(C.GRAY + "  Сейф уже открыт." + C.RESET)
        return

    print()
    hr("─")
    print(C.L_RED + C.BOLD + "  🔐 КОДОВЫЙ СЕЙФ" + C.RESET)
    hr("─")
    narrative(
        "Старый сейф в углу. Четырёхзначный кодовый замок. "
        "На стене мелом написаны цифры. В кармане халата ты нашёл записку. "
        "Вспомни всё, что ты видел. Какой код?"
    )
    print(C.GRAY + "  (введи четырёхзначный код или 'отмена' для выхода)" + C.RESET)
    print()

    attempts = 0
    while attempts < 3:
        try:
            code = input(C.CYAN + "  Код: " + C.RESET).strip()
        except (EOFError, KeyboardInterrupt):
            return
        if code.lower() in ("отмена", "выход", "назад"):
            return
        if code == "3721":
            print()
            slow_print("  Сейф открывается с глухим щелчком.", color=C.L_GREEN)
            time.sleep(0.5)
            narrative(
                "Внутри — потрёпанная папка с документами и тяжёлый ключ. "
                "На папке написано: «ЭКСПЕРИМЕНТ «ТЕНЬ». СТРОГО СЕКРЕТНО». "
                "Ты берёшь ключ и листаешь несколько страниц. "
                "Лучше бы не листал. Лучше бы никогда не знал."
            )
            state.add_item("ключ выхода")
            state.items_found.append("ключ выхода")
            state.puzzle_solved = True
            state.quests["quest_3"] = True
            state.quests["quest_4"] = True
            state.drain_sanity(8)
            print()
            print(C.L_GREEN + C.BOLD + "  ✓ КВЕСТ ВЫПОЛНЕН: Головоломка морга" + C.RESET)
            print(C.L_GREEN + C.BOLD + "  ✓ КВЕСТ ВЫПОЛНЕН: Найти ключ выхода" + C.RESET)
            return
        else:
            attempts += 1
            state.drain_sanity(5)
            remaining = 3 - attempts
            if remaining > 0:
                print(C.RED + f"  Неверно. Осталось попыток: {remaining}" + C.RESET)
            else:
                print(C.L_RED + "  Неверно. Сейф блокируется." + C.RESET)
                time.sleep(0.5)
                jumpscare("ЧТО-ТО КОСНУЛОСЬ ТВОЕЙ ШЕИ")
                state.drain_sanity(15)
                print(C.GRAY + "  Сейф заблокирован. Попробуй найти другие подсказки." + C.RESET)
                return

# ─── ПРОВЕРКА КОДА СЕЙФА (ДЛЯ ВЕБ-РЕЖИМА) ────────────────────

def handle_puzzle_attempt(state, code):
    """Проверяет один код для сейфа морга (без интерактивного ввода)."""
    if state.puzzle_solved:
        print(C.GRAY + "  Сейф уже открыт. Ключ выхода у тебя." + C.RESET)
        return True
    if code == "3721":
        print()
        slow_print("  Сейф открывается с глухим щелчком.", color=C.L_GREEN)
        narrative(
            "Внутри — потрёпанная папка с документами и тяжёлый ключ. "
            "На папке написано: «ЭКСПЕРИМЕНТ «ТЕНЬ». СТРОГО СЕКРЕТНО». "
            "Ты берёшь ключ. Лучше бы не смотрел в папку. Лучше бы никогда не знал."
        )
        state.add_item("ключ выхода")
        state.items_found.append("ключ выхода")
        state.puzzle_solved = True
        state.quests["quest_3"] = True
        state.quests["quest_4"] = True
        state.drain_sanity(8)
        print()
        print(C.L_GREEN + C.BOLD + "  ✓ КВЕСТ ВЫПОЛНЕН: Головоломка морга" + C.RESET)
        print(C.L_GREEN + C.BOLD + "  ✓ КВЕСТ ВЫПОЛНЕН: Найти ключ выхода" + C.RESET)
        return True
    else:
        state.drain_sanity(5)
        print(C.RED + "  Неверный код. Сейф не поддаётся." + C.RESET)
        return False

# ─── КВЕСТ-ЧЕКИ ───────────────────────────────────────────────

def check_quests(state):
    room_name = state.current_room

    # Квест 1: найти ключ
    if not state.quests["quest_1"] and "ржавый ключ" in state.inventory:
        state.quests["quest_1"] = True
        print()
        print(C.L_GREEN + C.BOLD + "  ✓ КВЕСТ ВЫПОЛНЕН: Найти ключ" + C.RESET)

    # Квест 2: запустить генератор — проверяется при использовании канистры

def show_quests(state):
    hr()
    print(C.CYAN + C.BOLD + "  📋 ЗАДАНИЯ" + C.RESET)
    hr()
    for qid, q in QUESTS.items():
        done = state.quests.get(qid, False)
        status = C.L_GREEN + "✓" if done else C.GRAY + "○"
        q_color = C.GRAY if done else C.WHITE
        print(f"  {status} {C.RESET}{q_color}{q['name']}{C.RESET}")
        if not done:
            print(C.GRAY + f"     {q['desc']}" + C.RESET)
    hr()

# ─── КОНЦОВКИ ─────────────────────────────────────────────────

def trigger_ending(state):
    clear()
    sanity = state.sanity

    if sanity >= 60:
        # Хорошая концовка
        slow_print("\n\n  Ты вставляешь ключ выхода в замок.", delay=0.04, color=C.WHITE)
        time.sleep(0.5)
        sound("Замок щёлкает. Дверь со скрипом открывается.")
        time.sleep(0.5)
        slow_print("\n  Холодный ночной воздух врывается внутрь.", delay=0.03, color=C.L_CYAN)
        time.sleep(0.5)
        narrative(
            "Ты выходишь. Ноги подкашиваются, но ты идёшь. "
            "Позади остаётся темнота. Впереди — ночное небо, усыпанное звёздами. "
            "Ты жив. Ты в своём уме. Почти."
        )
        time.sleep(1)
        print()
        hr("═")
        print(C.L_GREEN + C.BOLD + "\n  КОНЦОВКА: ПОБЕГ\n" + C.RESET)
        hr("═")
        print()
        narrative(
            "Ты добрался до дороги. Остановил машину. "
            "Водитель не задавал лишних вопросов — твой вид говорил сам за себя. "
            "Полиция потом найдёт папку про «Эксперимент Тень». "
            "Больница будет опечатана. "
            "Ты будешь долго не спать по ночам. "
            "Но ты выжил."
        )

    elif sanity >= 25:
        # Нейтральная концовка
        slow_print("\n\n  Ты вставляешь ключ. Пальцы дрожат.", delay=0.04, color=C.WHITE)
        time.sleep(0.5)
        sound("Замок. Дверь.")
        narrative(
            "Снаружи светло. Ты щуришься. Свет режет глаза. "
            "Ты идёшь, не оглядываясь. "
            "Но ты знаешь: что-то осталось там, в темноте. "
            "И оно не забыло тебя."
        )
        print()
        hr("═")
        print(C.L_YELLOW + C.BOLD + "\n  КОНЦОВКА: СЛОМЛЕННЫЙ\n" + C.RESET)
        hr("═")
        print()
        narrative(
            "Ты выбрался. Технически. "
            "Но часть тебя осталась там, в подвале. "
            "По ночам ты слышишь шаги. Шёпот. "
            "Врачи говорят — стресс. "
            "Ты знаешь правду."
        )

    else:
        # Плохая концовка
        jumpscare("РАЗУМ СЛОМЛЕН")
        slow_print("\n\n  Ты поворачиваешь ключ.", delay=0.04, color=C.RED)
        time.sleep(0.3)
        spooky(
            "Но что-то идёт не так. "
            "Дверь открывается. Но ты не выходишь. "
            "Ты смотришь на выход — и поворачиваешься назад. "
            "В темноту. К голосам. Они зовут тебя. "
            "Они так долго ждали."
        )
        print()
        hr("═")
        print(C.RED + C.BOLD + "\n  КОНЦОВКА: БЕЗУМИЕ\n" + C.RESET)
        hr("═")
        print()
        narrative(
            "Тебя нашли через неделю. "
            "Сидящего в тёмном углу палаты №7. "
            "Ты что-то царапал на стене. "
            "«ВЫПУСТИТЕ МЕНЯ», «ОН ПРИХОДИТ НОЧЬЮ», «Я НЕ СУМАСШЕДШИЙ»."
        )
        time.sleep(1)
        narrative(
            "Знакомые слова. Правда?"
        )

    time.sleep(1)
    print()
    print(C.GRAY + f"  Ходов сделано: {state.turns}" + C.RESET)
    print(C.GRAY + f"  Финальный рассудок: {state.sanity}%" + C.RESET)
    print()

    state.won = True
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

    input(C.GRAY + "  [Enter для выхода]" + C.RESET)
    sys.exit(0)

# ─── СМЕРТЬ ───────────────────────────────────────────────────

def check_death(state):
    if state.sanity <= 0:
        clear()
        time.sleep(0.5)
        jumpscare("РАЗУМ УГАС")
        time.sleep(0.5)
        spooky(
            "Тьма поглощает тебя полностью. "
            "Голоса становятся слишком громкими. "
            "Ты перестаёшь отличать реальное от воображаемого. "
            "Ты перестаёшь быть собой."
        )
        print()
        hr("═")
        print(C.RED + C.BOLD + "\n  КОНЕЦ: РАЗУМ ПОГЛОЩЁН\n" + C.RESET)
        hr("═")
        print(C.GRAY + "  Ты не смог выдержать ужасы подвала." + C.RESET)
        print(C.GRAY + "  Рассудок: 0%. Игра окончена." + C.RESET)
        print()
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        input(C.GRAY + "  [Enter для выхода]" + C.RESET)
        sys.exit(0)

# ─── ОСМОТР / ОБЫСК ───────────────────────────────────────────

def examine_room(state):
    room = ROOMS[state.current_room]
    available = [i for i in room.get("items", []) if i not in state.items_found]
    is_dark = room.get("dark") and not state.has_flashlight

    if is_dark:
        narrative("Слишком темно, чтобы что-то разглядеть.")
        return

    if not available:
        narrative("Больше ничего интересного здесь нет.")
    else:
        print()
        for item_name in available:
            item = ITEMS.get(item_name, {})
            print(C.L_YELLOW + f"  {item['emoji']} Ты нашёл: {C.BOLD}{item_name}{C.RESET}")
            print(C.GRAY + f"  {item.get('desc', '')}" + C.RESET)
            state.add_item(item_name)
            state.items_found.append(item_name)
            if item_name == "фонарик":
                state.has_flashlight = False  # Потребует явного использования
            print()
        # Проверяем квесты
        check_quests(state)

# ─── ПЕРЕМЕЩЕНИЕ ──────────────────────────────────────────────

DIRECTION_MAP = {
    "север": "север", "с": "север", "n": "север",
    "юг":    "юг",    "ю": "юг",    "s": "юг",
    "запад": "запад", "з": "запад", "w": "запад",
    "восток":"восток","в": "восток","e": "восток",
}

def try_move(state, direction):
    room = ROOMS[state.current_room]
    exits = room.get("exits", {})

    if direction not in exits:
        print(C.GRAY + "  Туда нельзя." + C.RESET)
        return

    target = exits[direction]

    # Проверки заблокированных комнат
    if target == "морг":
        if "коридор_б_opened" not in state.locked_rooms_opened and not state.quests.get("quest_1"):
            print(C.GRAY + "  Путь заблокирован засовом. Нужен ключ." + C.RESET)
            return
        if "коридор_б_opened" not in state.locked_rooms_opened:
            print(C.GRAY + "  Путь заблокирован засовом. Используй ключ из инвентаря." + C.RESET)
            return

    if target == "кабинет главврача":
        if "кабинет_opened" not in state.locked_rooms_opened:
            print(C.GRAY + "  Дверь заперта. Нужен рычаг или что-то для взлома." + C.RESET)
            return

    if target == "выход":
        if not state.has_item("ключ выхода"):
            print(C.GRAY + "  Дверь заперта на замок. Нужен ключ." + C.RESET)
            return

    # Переходим
    state.current_room = target
    target_room = ROOMS[target]
    state.turns += 1

    # Дренаж рассудка
    drain = target_room.get("sanity_drain", 0)
    if target_room.get("dark") and not state.has_flashlight:
        drain += 3
    state.drain_sanity(drain)

    # Галлюцинации
    hallucination_message(state.sanity)

    # Джампскер?
    if state.sanity < 40 and random.random() < 0.12:
        scares = [
            "КТО-ТО ЗА СПИНОЙ",
            "НЕ СМОТРИ НАЗАД",
            "ОН УЖЕ ЗДЕСЬ",
        ]
        jumpscare(random.choice(scares))

# ─── ОБРАБОТКА КОМАНД ─────────────────────────────────────────

def parse_command(cmd, state):
    cmd = cmd.strip().lower()
    words = cmd.split()

    if not words:
        return

    first = words[0]
    rest  = " ".join(words[1:]) if len(words) > 1 else ""

    # Движение
    if first in ("идти", "идем", "иди", "пойти", "перейти", "пройти"):
        direction = DIRECTION_MAP.get(rest, rest)
        if not direction:
            print(C.GRAY + "  Куда идти?" + C.RESET)
        else:
            try_move(state, direction)
        return

    if first in DIRECTION_MAP:
        try_move(state, DIRECTION_MAP[first])
        return

    # Осмотр
    if first in ("осмотреть", "осмотр", "обыскать", "искать", "посмотреть", "смотреть", "поискать"):
        examine_room(state)
        return

    # Инвентарь
    if first in ("инвентарь", "inv", "вещи", "рюкзак", "сумка", "и"):
        show_inventory(state)
        return

    # Задания
    if first in ("задания", "квесты", "цель", "задание", "квест", "з"):
        show_quests(state)
        return

    # Взять предмет
    if first in ("взять", "подобрать", "подобрать", "поднять", "схватить"):
        room = ROOMS[state.current_room]
        avail = [i for i in room.get("items", []) if i not in state.items_found]
        if not rest:
            if avail:
                print(C.GRAY + "  Что взять? Видно: " + ", ".join(avail) + C.RESET)
            else:
                print(C.GRAY + "  Здесь нечего брать." + C.RESET)
        elif rest in avail:
            item = ITEMS.get(rest, {})
            state.add_item(rest)
            state.items_found.append(rest)
            print(C.L_GREEN + f"  Ты берёшь: {item.get('emoji','')} {rest}" + C.RESET)
            check_quests(state)
        else:
            print(C.GRAY + "  Здесь нет такого предмета." + C.RESET)
        return

    # Использовать предмет
    if first in ("использовать", "применить", "юз", "use"):
        if not rest:
            print(C.GRAY + "  Что использовать?" + C.RESET)
        else:
            use_item(state, rest)
        return

    # Выбросить
    if first in ("выбросить", "бросить", "выкинуть"):
        if rest in state.inventory:
            state.remove_item(rest)
            print(C.GRAY + f"  Ты выбрасываешь {rest}." + C.RESET)
        else:
            print(C.GRAY + "  Такого предмета нет в инвентаре." + C.RESET)
        return

    # Комбинировать
    if first in ("объединить", "скомбинировать", "совместить", "комбинировать"):
        parts = rest.split(" с ", 1) if " с " in rest else rest.split(" и ", 1)
        if len(parts) == 2:
            combine_items(state, parts[0].strip(), parts[1].strip())
        else:
            print(C.GRAY + "  Как? Пример: 'объединить канистра с бензин'" + C.RESET)
        return

    # Головоломка
    if first in ("решить", "открыть") and ("сейф" in rest or "головоломку" in rest or "код" in rest):
        if state.current_room == "морг":
            run_puzzle(state)
        else:
            print(C.GRAY + "  Здесь нет сейфа." + C.RESET)
        return

    # Читать
    if first in ("читать", "прочитать", "изучить") and rest:
        if rest in state.inventory:
            item = ITEMS.get(rest, {})
            print(C.L_CYAN + f"  {item.get('emoji','')} {rest}:" + C.RESET)
            print(C.WHITE + f"  {item.get('desc','Нет описания.')}" + C.RESET)
        else:
            print(C.GRAY + "  Такого предмета нет в инвентаре." + C.RESET)
        return

    # Сохранить
    if first in ("сохранить", "сохранение", "save"):
        save_game(state)
        return

    # Загрузить
    if first in ("загрузить", "загрузка", "load"):
        loaded = load_game()
        if loaded:
            return loaded  # Возвращаем новый стейт
        return

    # Помощь
    if first in ("помощь", "help", "команды", "?"):
        show_help()
        return

    # Выход
    if first in ("выход", "quit", "exit", "выйти") and "игра" in rest:
        print()
        confirm = input(C.GRAY + "  Выйти из игры? (да/нет): " + C.RESET).strip().lower()
        if confirm in ("да", "y", "yes"):
            save_game(state)
            print(C.GRAY + "  До встречи в темноте..." + C.RESET)
            sys.exit(0)
        return

    # Статус
    if first in ("статус", "состояние", "рассудок"):
        print(C.CYAN + f"  Рассудок: {state.sanity}%" + C.RESET)
        if state.sanity > 70:
            print(C.L_GREEN + "  Ты в порядке." + C.RESET)
        elif state.sanity > 40:
            print(C.L_YELLOW + "  Ты начинаешь слышать странные вещи." + C.RESET)
        elif state.sanity > 20:
            print(C.L_RED + "  Ты на грани. Реальность расплывается." + C.RESET)
        else:
            print(C.RED + C.BLINK + "  РАССУДОК НА ПРЕДЕЛЕ." + C.RESET)
        return

    print(C.GRAY + f"  Не понимаю: '{cmd}'. Введи 'помощь' для списка команд." + C.RESET)

def show_help():
    hr()
    print(C.CYAN + C.BOLD + "  📖 КОМАНДЫ" + C.RESET)
    hr()
    cmds = [
        ("идти [север/юг/запад/восток]", "Перемещение"),
        ("осмотреть", "Осмотреть комнату, найти предметы"),
        ("инвентарь", "Посмотреть инвентарь"),
        ("взять [предмет]", "Подобрать предмет"),
        ("использовать [предмет]", "Использовать предмет"),
        ("объединить [А] с [Б]", "Объединить два предмета"),
        ("выбросить [предмет]", "Выбросить предмет"),
        ("читать [предмет]", "Прочитать предмет"),
        ("задания", "Список активных заданий"),
        ("статус", "Состояние рассудка"),
        ("решить сейф", "Решить головоломку сейфа (в морге)"),
        ("сохранить", "Сохранить игру"),
        ("загрузить", "Загрузить сохранение"),
        ("выйти из игры", "Выйти"),
    ]
    for cmd, desc in cmds:
        print(C.L_CYAN + f"  {cmd:<35}" + C.RESET + C.GRAY + desc + C.RESET)
    hr()

# ─── ГЛАВНОЕ МЕНЮ ─────────────────────────────────────────────

def show_title():
    clear()
    print()
    art = r"""
  ██████╗  ██████╗ █████╗  ██╗      ██████╗  ███████╗
  ██╔══██╗██╔═══██╗██╔══██╗ ██║     ██╔═══██╗██╔════╝
  ██████╔╝██║   ██║███████║ ██║     ██║   ██║███████╗
  ██╔═══╝ ██║   ██║██╔══██║ ██║     ██║   ██║╚════██║
  ██║     ╚██████╔╝██║  ██║ ███████╗╚██████╔╝███████║
  ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚══════╝ ╚═════╝ ╚══════╝
    """
    print(C.RED + C.BOLD + art + C.RESET)
    print(C.L_RED + C.BOLD + "            БЕЗУМИЯ" + C.RESET)
    print()
    print(C.GRAY + "         Текстовая хоррор-игра" + C.RESET)
    print(C.GRAY + "    Заброшенная психиатрическая больница" + C.RESET)
    print()
    hr()
    print(C.GRAY + "  [1] Новая игра" + C.RESET)
    print(C.GRAY + "  [2] Загрузить игру" + C.RESET)
    print(C.GRAY + "  [3] Помощь" + C.RESET)
    print(C.GRAY + "  [4] Выйти" + C.RESET)
    hr()

def intro_cutscene():
    clear()
    time.sleep(0.3)
    narrative("...", delay=0.1)
    time.sleep(0.5)
    narrative("...тишина.", delay=0.06)
    time.sleep(0.5)
    narrative("...темнота.", delay=0.06)
    time.sleep(0.7)
    spooky("Ты приходишь в себя.")
    time.sleep(0.5)
    narrative(
        "Холодный бетон под щекой. Запах сырости. Где-то вдалеке — капель. "
        "Ты не помнишь, как сюда попал. Ты не помнишь своё имя. "
        "Ты помнишь только одно:"
    )
    time.sleep(0.5)
    slow_print("\n  НУЖНО ВЫБРАТЬСЯ.\n", delay=0.06, color=C.L_RED + C.BOLD)
    time.sleep(0.7)
    whisper("Удачи. Тебе понадобится.")
    time.sleep(1)
    input(C.GRAY + "\n  [нажмите Enter...]" + C.RESET)

# ─── ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ ─────────────────────────────────────

def game_loop(state):
    clear()
    show_hud(state)
    show_room(state)

    while True:
        check_death(state)

        print()
        try:
            cmd = input(C.CYAN + "  > " + C.RESET)
        except (EOFError, KeyboardInterrupt):
            print()
            save_game(state)
            print(C.GRAY + "  До встречи в темноте..." + C.RESET)
            break

        result = parse_command(cmd, state)
        # Если загружена новая игра
        if isinstance(result, GameState):
            state = result

        # Тень движется и проверяет встречу
        move_entity(state)
        check_entity_encounter(state)

        clear()
        show_hud(state)
        show_room(state)

# ─── ТОЧКА ВХОДА ──────────────────────────────────────────────

def main():
    while True:
        show_title()
        try:
            choice = input(C.CYAN + "\n  Выбор: " + C.RESET).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "1":
            state = GameState()
            intro_cutscene()
            game_loop(state)
            break

        elif choice == "2":
            state = load_game()
            if state:
                time.sleep(0.5)
                game_loop(state)
                break
            else:
                input(C.GRAY + "  [Enter]" + C.RESET)

        elif choice == "3":
            clear()
            show_help()
            input(C.GRAY + "\n  [Enter для возврата]" + C.RESET)

        elif choice == "4":
            print(C.GRAY + "\n  Выход..." + C.RESET)
            break
        else:
            print(C.GRAY + "  Введи 1, 2, 3 или 4." + C.RESET)
            time.sleep(0.5)

if __name__ == "__main__":
    main()
