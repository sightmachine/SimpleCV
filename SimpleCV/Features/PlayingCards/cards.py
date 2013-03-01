import itertools
import random
import pickle
import time

# cribbed from
# http://pastebin.com/mzNmCdV5 
# http://stackoverflow.com/questions/2518753/best-way-to-implement-a-deck-for-a-card-game-in-python
# data
SUITS = ('c', 'd', 'h', 's')
RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A')

DECK = tuple(''.join(card) for card in itertools.product(RANKS, SUITS))

ORDER_LOOKUP = dict(zip(DECK, range(52)))
RANK_LOOKUP = dict(zip(RANKS, range(13)))
SUIT_LOOKUP = dict(zip(SUITS, range(4)))

# utility functions
def cmp_cards(a, b):
    return cmp(ORDER_LOOKUP[a], ORDER_LOOKUP[b])
    
def cmp_tuples(a, b):
    n1 = len(a)
    n2 = len(b)
    if n1 != n2:
        return cmp(n1, n2)
    return cmp(a, b)
    
def suit(card):
    return card[1]
    
def suit_int(card):
    return SUIT_LOOKUP[card[1]]
    
def rank(card):
    return card[0]
    
def rank_int(card):
    return RANK_LOOKUP[card[0]]
    
def card_int(card):
    s = 1 << suit_int(card)
    r = rank_int(card)
    c = (s << 4) | r
    return c
    
# test functions
def is_straight(cards):
    previous = rank_int(cards[0]) - 1
    for card in cards:
        r = rank_int(card)
        if r != previous + 1:
            if not (r == 12 and previous == 3):
                return False
        previous = r
    return True
    
def is_flush(cards):
    s = suit(cards[0])
    return all(suit(card) == s for card in cards)
    
def same_rank(cards):
    r = rank(cards[0])
    return all(rank(card) == r for card in cards)
    
def split_ranks(cards, indexes):
    for index in indexes:
        a, b = cards[:index], cards[index:]
        if same_rank(a) and same_rank(b):
            return True
    return False
    
def is_full_house(cards):
    return split_ranks(cards, (2, 3))
    
def is_four(cards):
    return split_ranks(cards, (1, 4))
    
def is_pat(cards):
    return is_straight(cards) or is_flush(cards) or is_full_house(cards) or is_four(cards)
    
def is_straight_flush(cards):
    return is_straight(cards) and is_flush(cards)
    
def rank_count(cards):
    result = {}
    for card in cards:
        r = rank_int(card)
        result[r] = result.get(r, 0) + 1
    return result
    
def is_three(cards, counts=None):
    counts = counts or rank_count(cards)
    for rank, count in counts.iteritems():
        if count == 3:
            return True
    return False
    
def is_two_pair(cards, counts=None):
    pairs = 0
    counts = counts or rank_count(cards)
    for rank, count in counts.iteritems():
        if count == 2:
            pairs += 1
    return pairs == 2
    
def is_pair(cards, counts=None):
    counts = counts or rank_count(cards)
    for rank, count in counts.iteritems():
        if count == 2:
            return True
    return False
    
def get_ranks(counts):
    values = [(count, rank) for rank, count in counts.iteritems()]
    values.sort(reverse=True)
    values = [n[1] for n in values]
    return values
    
def get_straight_rank(cards):
    top = rank_int(cards[-1])
    bottom = rank_int(cards[0])
    if top == 12 and bottom == 0:
        return 3
    return top
    
def evaluate_hand(cards):
    flush = is_flush(cards)
    straight = is_straight(cards)
    counts = rank_count(cards)
    ranks = get_ranks(counts)
    if straight:
        ranks = [get_straight_rank(cards)]
    if straight and flush:
        value = 9
    elif is_four(cards):
        value = 8
    elif is_full_house(cards):
        value = 7
    elif flush:
        value = 6
    elif straight:
        value = 5
    elif is_three(cards, counts):
        value = 4
    elif is_two_pair(cards, counts):
        value = 3
    elif is_pair(cards, counts):
        value = 2
    else:
        value = 1
    ranks.insert(0, value)
    return tuple(ranks)
