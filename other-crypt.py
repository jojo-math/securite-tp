import math
import random
import unicodedata
from collections import Counter
import re

# --- CONFIGURATION ---
ALPHABET = 'àâäæçéèêëîïôöùûüÿœÀÂÄÆÇÉÈÊËÎÏÔÖÙÛÜŸŒ0123456789²& é"(-è_çà)=~{[|^@]}€¤£µ*ù%!§:/;.,?<>+°¨$£¥¢©®™✓✔✕✖¶§±÷×≈≠≤≥∞√∑πΩαβγδεζηθικλμνξοπρστυφχψωABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#\''
N = len(ALPHABET)
CHAR_TO_INDEX = {char: idx for idx, char in enumerate(ALPHABET)}
VALID_A_VALUES = [a for a in range(1, N) if math.gcd(a, N) == 1]
WORD_PATTERN = re.compile(r"[^\W\d_]+", flags=re.UNICODE)
COMMON_WORDS = {"le", "la", "les", "des", "une", "dans", "est", "pas", "pour", "que", "qui", "sur", "de", "et"}
FREQUENT_CLEAR_CHARS = [
    char for char in " eaistnrulodcmpvqfbghjxykzwETAOINSHRDLU"
    if char in CHAR_TO_INDEX
]

# --- OUTILS MATHÉMATIQUES ---

def inverse_modulaire(a, n):
    """Calcule l'inverse de a modulo n (Euclide étendu)."""
    t, nouveau_t = 0, 1
    r, nouveau_r = n, a
    while nouveau_r != 0:
        quotient = r // nouveau_r
        t, nouveau_t = nouveau_t, t - quotient * nouveau_t
        r, nouveau_r = nouveau_r, r - quotient * nouveau_r
    if r > 1: return None
    return t % n

# --- LES 4 OPÉRATIONS ---

def generer_cle():
    """Opération 1 : Génération de clé valide."""
    a = random.randint(1, N - 1)
    while math.gcd(a, N) != 1:
        a = random.randint(1, N - 1)
    b = random.randint(0, N - 1)
    return a, b

def chiffrement(texte, a, b):
    """Opération 2 : Chiffrement."""
    resultat = ""
    for char in texte:
        if char in ALPHABET:
            x = ALPHABET.index(char)
            resultat += ALPHABET[(a * x + b) % N]
        else:
            resultat += char
    return resultat

def dechiffrement(texte_code, a, b):
    """Opération 3 : Déchiffrement."""
    a_inv = inverse_modulaire(a, N)
    if a_inv is None: return "Clé invalide !"
    resultat = ""
    for char in texte_code:
        if char in ALPHABET:
            y = ALPHABET.index(char)
            resultat += ALPHABET[(a_inv * (y - b)) % N]
        else:
            resultat += char
    return resultat

def _normaliser_mot(mot):
    decomposed = unicodedata.normalize('NFKD', mot.casefold())
    return ''.join(char for char in decomposed if not unicodedata.combining(char))

def _score_texte(texte):
    if not texte:
        return float('-inf')

    categories = Counter(unicodedata.category(char)[0] for char in texte)
    score = 0.0
    score += categories.get('L', 0) * 2.8
    score += categories.get('Z', 0) * 2.0
    score += categories.get('P', 0) * 1.0
    score -= categories.get('S', 0) * 1.5
    score -= categories.get('C', 0) * 4.0

    mots = [_normaliser_mot(mot) for mot in WORD_PATTERN.findall(texte) if len(mot) >= 2]
    if mots:
        hits = sum(1 for mot in mots if mot in COMMON_WORDS)
        score += (hits / len(mots)) * 300.0

    return score

def _resoudre_lineaire_modulaire(coef, rhs, modulo):
    g = math.gcd(coef, modulo)
    if rhs % g != 0:
        return []

    coef_reduit = coef // g
    rhs_reduit = rhs // g
    modulo_reduit = modulo // g
    inv = pow(coef_reduit, -1, modulo_reduit)
    x0 = (inv * rhs_reduit) % modulo_reduit
    return [(x0 + k * modulo_reduit) % modulo for k in range(g)]

def _indices_plus_frequents(texte, limite=10):
    compteur = Counter(char for char in texte if char in CHAR_TO_INDEX)
    return [CHAR_TO_INDEX[char] for char, _ in compteur.most_common(limite)]

def _generer_cles_par_frequences(texte_code, max_cipher_chars=12, max_plain_chars=12):
    indices_cipher = _indices_plus_frequents(texte_code, limite=max_cipher_chars)
    indices_plain = [CHAR_TO_INDEX[char] for char in FREQUENT_CLEAR_CHARS[:max_plain_chars]]

    cles = set()
    for i, c1 in enumerate(indices_cipher):
        for c2 in indices_cipher[i + 1:]:
            delta_c = (c1 - c2) % N
            for j, p1 in enumerate(indices_plain):
                for p2 in indices_plain[j + 1:]:
                    delta_p = (p1 - p2) % N
                    if delta_p == 0:
                        continue
                    for a in _resoudre_lineaire_modulaire(delta_p, delta_c, N):
                        if math.gcd(a, N) != 1:
                            continue
                        b = (c1 - a * p1) % N
                        cles.add((a, b))
    return list(cles)

def cryptanalyse_brute_force(texte_code):
    """Opération 4 : Cryptanalyse affine guidée par fréquences."""
    print("\n[Analyse fréquentielle + brute-force en cours...]")

    cles_freq = _generer_cles_par_frequences(texte_code)
    print(f"Candidats fréquentiels: {len(cles_freq)}")

    if len(cles_freq) < 10:
        cles = cles_freq + [(a, b) for a in VALID_A_VALUES for b in range(N) if (a, b) not in set(cles_freq)]
    else:
        cles = cles_freq

    meilleurs = []
    for a, b in cles:
        test = dechiffrement(texte_code, a, b)
        score = _score_texte(test)
        meilleurs.append((score, a, b, test))

    meilleurs.sort(reverse=True, key=lambda x: x[0])
    top = meilleurs[:10]

    for i, (score, a, b, texte) in enumerate(top, 1):
        print(f"\n--- Résultat {i} ---")
        print(f"Clé: a={a}, b={b} (score={score:.2f})")
        print(f"Texte: {texte[:140]}...")

    if not top:
        print("Aucun résultat probant trouvé.")
        return None

    return top[0][3]

# --- MENU PRINCIPAL ---

def menu():
    while True:
        print("\n--- SYSTÈME AFFINE ÉTENDU ---")
        print("1. Générer une clé")
        print("2. Chiffrer un message")
        print("3. Déchiffrer un message")
        print("4. Cryptanalyser (Brute Force)")
        print("5. Quitter")
        
        choix = input("Votre choix : ")
        
        if choix == '1':
            a, b = generer_cle()
            print(f"Clé générée : a={a}, b={b}")
        elif choix == '2':
            msg = input("Message à chiffrer : ")
            a = int(input("Entrez la clé a : "))
            b = int(input("Entrez la clé b : "))
            print("Résultat :", chiffrement(msg, a, b))
        elif choix == '3':
            msg = input("Message à déchiffrer : ")
            a = int(input("Entrez la clé a : "))
            b = int(input("Entrez la clé b : "))
            print("Résultat :", dechiffrement(msg, a, b))
        elif choix == '4':
            msg = input("Texte chiffré à casser : ")
            cryptanalyse_brute_force(msg)
        elif choix == '5':
            break

if __name__ == "__main__":
    menu()