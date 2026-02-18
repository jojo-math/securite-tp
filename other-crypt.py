import math
import random

# --- CONFIGURATION ---
ALPHABET = 'àâäæçéèêëîïôöùûüÿœÀÂÄÆÇÉÈÊËÎÏÔÖÙÛÜŸŒ0123456789²& é"(-è_çà)=~{[|^@]}€¤£µ*ù%!§:/;.,?<>+°¨$£¥¢©®™✓✔✕✖¶§±÷×≈≠≤≥∞√∑πΩαβγδεζηθικλμνξοπρστυφχψωABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#\''
N = len(ALPHABET)

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

def cryptanalyse_brute_force(texte_code):
    """Opération 4 : Cryptanalyse par force brute."""
    print("\n[Recherche en cours...]")
    mots_cles = [" le ", " la ", " est ", " de ", " un "] # Pour détecter le français
    
    for a in range(1, N):
        if math.gcd(a, N) == 1:
            for b in range(N):
                test = dechiffrement(texte_code, a, b)
                # On vérifie si un mot commun apparaît
                if any(mot in test for mot in mots_cles):
                    print(f" Clé potentielle trouvée : a={a}, b={b}")
                    print(f" Texte : {test[:100]}...")
                    reponse = input("Est-ce correct ? (o/n) : ")
                    if reponse.lower() == 'o':
                        return test
    print("Aucun résultat probant trouvé.")

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