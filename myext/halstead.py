import math


def halstead(tor_u, and_u, tor_t, and_t):
    vocab = vocabulary(tor_u, and_u)
    leng = length(tor_t, and_t)
    vol = volume(leng, vocab)
    diff = difficulty(tor_u, and_t, and_u)
    eff = effort(diff, vol)
    bug = bugs(vol)


def vocabulary(tor_u, and_u):
    return tor_u + and_u


def length(tor_t, and_t):
    return tor_t + and_t


def volume(leng, vocab):
    return leng * math.log(vocab, 2)


def difficulty(tor_u, and_t, and_u):
    return (tor_u / 2) * (and_t / and_u)


def effort(diff, vol):
    return diff * vol


def bugs(vol):
    return vol / 3000


def output():
    print "hello"


print(effort(101.333333, 4216.647093))


