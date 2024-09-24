from random import choice, randint
from collections import deque
global parent_parser, construct_builtin

STARTER = "Lorem Ipsum dolor sit amet, consectetur adipiscing elit"
STARTER_SIZE = len(STARTER.split(' '))
STARTER_WORDS = STARTER.split()

DIVISORS = ('.', ',', '?')
ENDERS = ('.', '?')

REQUIRES_PREFIX = ["lor", "ips", "s", "qu", "rum", "popul",
                   "habit", "vehicul", "en", "plat", "tor",
                   "liber", "auc", "semp", "taur", "lup", "nab",
                   "caes", "cic", "senat", "rom", "imperi", "arbo",
                   "pharm", "magn", "lect", "turp", "aliqu", "excep", "plat",
                   "penat", "bland", "hend", "fin", "sagit", "pur", "cur", "ursin",
                   "ur", "cer"]

BASE_TEXT = (f"nulla quam voluptat equit tincid est ligula id platea "
             f"dolor populat ad et num ea necessit facil magna massa alias "
             f"condiment carpe commodo reprehenderit velit esse "
             f"prun dictu duc soda nunc nisi purus varius "
             f"gravida malesua pharetra vestibul habit nec labor integer"
             f"sapien augue nisl himena justo {parent_parser.get_name()}")


Suffixes = ("que", "em", "am", "a", "it", "qua", "ae", "ea", "tes", "es", "at", "asse",
            "te", "e", "bus", 'i', "im", "is", 'esque', "atis", "unt", "us", "teur",
            "os", "mst", "tor", "o", "ion", "da", "lis", "dae", "um")


def format_word(word: str):
    word = word.replace('.', '').replace(',', '')
    return word.lower()


def randomize(word: str):
    if randint(0, 6) < 2 or word in REQUIRES_PREFIX:
        return word + choice([s for s in Suffixes if not word[-1] == s[0] and not word == s])
    return word


BASE_WORDS = [
                 format_word(word).strip() for word in BASE_TEXT.replace("\n", '').split(' ') if word.strip()
             ] + REQUIRES_PREFIX


def generate_sentence(word_amount: int = STARTER_SIZE,
                      base: list[str] = None, capitalize=False, basic=False) -> list[str]:
    if not base:
        base = BASE_WORDS

    if basic:
        return STARTER_WORDS[:word_amount]

    mem = deque(list(), maxlen=12)
    words = []
    chosen = None
    for i in range(word_amount):
        while chosen is None or chosen in mem:
            chosen = randomize(choice(base))

        if capitalize and i == 0:
            words.append(chosen.capitalize())
        else:
            words.append(chosen)
        mem.append(chosen)

    return words


def randomline():
    return '\n' if randint(0, 10) < 4 else ''


def lorem_builtin(amount: int = STARTER_SIZE) -> str:
    sentence = generate_sentence(
        STARTER_SIZE if amount > STARTER_SIZE else amount,
        capitalize=True,
        basic=True
    )
    part = int(0.22 * amount)
    amount -= STARTER_SIZE
    if amount > 0:
        while amount > 0:
            rand_size = randint(min(6, part), amount if not part else part)
            amount -= rand_size
            generated = generate_sentence(rand_size,
                                          capitalize=(sentence[-1][-1] == '\n' or sentence[-1][-1] in ENDERS))

            if randint(0, 10) <= 7 and amount > 0:
                chosen_div = choice(DIVISORS)
                generated[-1] = generated[-1] + chosen_div + (randomline() if chosen_div in ENDERS else "")
            sentence += generated

    joint = " ".join(sentence).strip()
    if joint.endswith(','):
        return joint[:-1] + '.'
    return " ".join(sentence) + ('.' if joint[-1] not in ENDERS else '')


parent_parser.assign_references({
    "lorem": construct_builtin('lorem', lorem_builtin)
})
