from scipy import interpolate
import rsa
from rsa import PublicKey
from hashlib import sha256
from itertools import combinations
from numpy import poly1d
from json_stuff import *
from random import SystemRandom

def prod(x, G):
    p = 1
    for i in x:
        p *= i
    return p

def next_prime(N):
    # TODO: fix
    return N+1

def hasher(b):
    return sha256(b).hexdigest()

def check_poly(p):
    # TODO: maybe fix this
    return True

cryptorand = SystemRandom()
def randint(n):
    return cryptorand.randrange(n)

def lagrange(x, y, G):
    assert len(x) == len(y) and len(x) > 0, "Lengths of x and y must equal and non-zero."
    x_len = len(x)
    f = [0] * x_len
    for i in range(x_len):
        partial = []
        combo_list = list(x)
        combo_list.pop(i)
        for j in range(x_len):
            c = 0
            for k in combinations(combo_list, j):
                c += prod(map(lambda q: -q, k), G)
            partial.append(c)
        d = 1
        for j in range(x_len):
            if j != i:
                d = (d * (x[i] - x[j]))

        partial = map(lambda q: (q * y[i] / d) % G, partial)
        f = [(m + n) % G for m, n in zip(f, partial)] # also needs % G
    return f

def bytes_to_int(m):
    m = list(m)
    m_len = len(m)
    for i in range(m_len):
        m[i] *= 256**(m_len - 1 - i)

    return sum(m)

def compute_poly(f, x):
    y = 0
    for i in range(len(f)):
        y += f[i] * x**(len(f) - 1 - i)
    return y

class Alice:

    def __init__(self, M):
        self.M = M

        (pubkey, privkey) = rsa.newkeys(512)
        self.pubkey = pubkey
        self.privkey = privkey

        self.hashes = []

        for m in self.M:
            self.hashes.append(hasher(m))

    def setup(self, file_name = "alice_setup.json"):
        j = {"pubkey": {"e": self.pubkey.e, "n": self.pubkey.n},
                "hashes": self.hashes}

        write_json(file_name, j)
        print("Pubkey and hashes published.")

    def transmit(self, file_name = "alice_dec.json", bob_file_name = "bob_setup.json"):
        bob = read_json(bob_file_name)
        check_poly(bob)
        f = bob

        G = []
        for i in range(len(self.M)):
            print(compute_poly(f, i))
            F = pow(round(compute_poly(f, i)), self.privkey.d, self.pubkey.n)
            G.append(F * bytes_to_int(self.M[i]))

        write_json(file_name, G)
        print("G has been published.")

class Bob:

    def __init__(self, num_messages, num_des_messages, des_messages):
        self.num_messages = num_messages
        self.num_des_messages = num_des_messages
        self.des_messages = des_messages

    def setup(self, file_name = "bob_setup.json", alice_file_name = "alice_setup.json"):
        alice = read_json(alice_file_name)
        self.pubkey = PublicKey(alice["pubkey"]["n"], alice["pubkey"]["e"])
        print(self.pubkey)
        self.hashes = alice["hashes"]

        self.R = []
        T = []
        for j in range(self.num_des_messages):
            r = randint(self.pubkey.n)
            self.R.append(r)
            T.append(pow(r, self.pubkey.e, self.pubkey.n)) # the encrypted random value

        print(self.pubkey.n)
        G = next_prime(self.pubkey.n)
        f = lagrange(self.des_messages, T, G)

        write_json(file_name, f)
        print("Polynomial published.")

    def receive(self, alice_file_name = "alice_dec.json"):
        alice = read_json(alice_file_name)
        G = alice

        decrypted = []
        for j in range(self.num_des_messages):
            d = (G[self.des_messages[j]] / self.R[j]) % self.pubkey.n
            decrypted.append(int_to_bytes(d))

            if hasher(decrypted[j]) != self.hashes[des_messages[j]]:
                print("Hashes don't match. Either something messed up or Alice is up to something.")

        self.decrypted = decrypted
        return(decrypted)






        




