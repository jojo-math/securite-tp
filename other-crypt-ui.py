import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math
import random
import unicodedata
from collections import Counter
import heapq
import re
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
ALPHABET = 'àâäæçéèêëîïôöùûüÿœÀÂÄÆÇÉÈÊËÎÏÔÖÙÛÜŸŒ0123456789²& é"(-è_çà)=~{[|^@]}€¤£µ*ù%!§:/;.,?<>+°¨$£¥¢©®™✓✔✕✖¶§±÷×≈≠≤≥∞√∑πΩαβγδεζηθικλμνξοπρστυφχψωABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#\''
ALPHABET = ''.join(dict.fromkeys(ALPHABET))
N = len(ALPHABET)
CHAR_TO_INDEX = {char: idx for idx, char in enumerate(ALPHABET)}
VALID_A_VALUES = [a for a in range(1, N) if math.gcd(a, N) == 1]
A_INVERSES = {a: inverse for a in VALID_A_VALUES if (inverse := pow(a, -1, N)) is not None}
KEY_SPACE = [(a, b) for a in VALID_A_VALUES for b in range(N)]
MAX_WORKERS = 8

COMMON_WORDS = {
    "the", "and", "for", "with", "this", "that", "you", "are", "was", "from", "have", "not",
    "le", "la", "les", "des", "une", "dans", "est", "pas", "pour", "que", "qui", "sur",
    "de", "del", "los", "las", "una", "para", "con", "por", "que", "como", "pero", "sus",
    "der", "die", "das", "und", "ist", "nicht", "mit", "ein", "eine", "auf", "von", "den",
    "il", "lo", "gli", "una", "con", "per", "che", "non", "nel", "della", "sono", "come",
    "uma", "com", "para", "que", "não", "dos", "das", "por", "mais", "como", "seus", "tem",
    "een", "van", "met", "niet", "voor", "het", "dat", "zijn", "was", "maar", "ook", "naar",
}
WORD_PATTERN = re.compile(r"[^\W\d_]+", flags=re.UNICODE)
RAINBOW_CACHE = {}

# --- FONCTIONS MATHÉMATIQUES ---

def inverse_modulaire(a, n):
    """Calcule l'inverse de a modulo n."""
    t, nouveau_t = 0, 1
    r, nouveau_r = n, a
    while nouveau_r != 0:
        quotient = r // nouveau_r
        t, nouveau_t = nouveau_t, t - quotient * nouveau_t
        r, nouveau_r = nouveau_r, r - quotient * nouveau_r
    if r > 1: return None
    return t % n

def generer_cle():
    """Génération de clé valide."""
    a = random.randint(1, N - 1)
    while math.gcd(a, N) != 1:
        a = random.randint(1, N - 1)
    b = random.randint(0, N - 1)
    return a, b

def chiffrement(texte, a, b):
    """Chiffrement."""
    resultat = ""
    for char in texte:
        x = CHAR_TO_INDEX.get(char)
        if x is not None:
            resultat += ALPHABET[(a * x + b) % N]
        else:
            resultat += char
    return resultat

def dechiffrement(texte_code, a, b):
    """Déchiffrement."""
    a_inv = inverse_modulaire(a, N)
    if a_inv is None: return None
    resultat = ""
    for char in texte_code:
        y = CHAR_TO_INDEX.get(char)
        if y is not None:
            resultat += ALPHABET[(a_inv * (y - b)) % N]
        else:
            resultat += char
    return resultat

def _score_texte_universel(texte):
    """Score agnostique à la langue basé sur des propriétés statistiques du texte."""
    if not texte:
        return float('-inf')

    taille = len(texte)
    compte_categories = Counter(unicodedata.category(char)[0] for char in texte)

    score = 0.0
    score += compte_categories.get('L', 0) * 3.0   # Lettres (toutes langues)
    score += compte_categories.get('N', 0) * 2.0   # Chiffres
    score += compte_categories.get('P', 0) * 1.0   # Ponctuation
    score += compte_categories.get('Z', 0) * 2.0   # Espaces/séparateurs
    score -= compte_categories.get('S', 0) * 1.5   # Symboles math/currency/etc
    score -= compte_categories.get('C', 0) * 4.0   # Contrôles/non imprimables

    freqs = Counter(texte)
    unicite = len(freqs) / taille
    score += (1.0 - unicite) * 50.0

    if taille > 1:
        ic = sum(freq * (freq - 1) for freq in freqs.values()) / (taille * (taille - 1))
        score += ic * 2000.0

    return score

def _normaliser_mot(mot):
    """Normalise un mot pour le matching dictionnaire (agnostique accents/casse)."""
    decomposed = unicodedata.normalize('NFKD', mot.casefold())
    return ''.join(char for char in decomposed if not unicodedata.combining(char))

def _extraire_mots(texte):
    """Extrait les mots Unicode d'un texte."""
    return [_normaliser_mot(mot) for mot in WORD_PATTERN.findall(texte)]

def _score_dictionnaire(texte):
    """Score basé sur présence de mots fréquents multi-langues."""
    mots = [mot for mot in _extraire_mots(texte) if len(mot) >= 3]
    if not mots:
        return 0.0

    hits = [mot for mot in mots if mot in COMMON_WORDS]
    nb_hits = len(hits)
    nb_uniques = len(set(hits))
    plus_long = max((len(mot) for mot in hits), default=0)
    ratio_hits = nb_hits / len(mots)
    return ratio_hits * 260.0 + min(nb_hits, 15) * 7.0 + min(nb_uniques, 8) * 5.0 + plus_long * 1.5

def _dechiffrement_depuis_indices(indices, texte_source, a_inv, b):
    """Déchiffrement rapide à partir d'indices pré-calculés."""
    resultat = []
    for char, y in zip(texte_source, indices):
        if y is None:
            resultat.append(char)
        else:
            resultat.append(ALPHABET[(a_inv * (y - b)) % N])
    return ''.join(resultat)

def _chunks(sequence, taille):
    for i in range(0, len(sequence), taille):
        yield sequence[i:i + taille]

def _worker_rainbow(chunk_cles, echantillon_texte, echantillon_indices):
    """Worker: construit des stats de table arc-en-ciel sur un sous-ensemble de clés."""
    local_entries = []
    for a, b in chunk_cles:
        texte_test = _dechiffrement_depuis_indices(echantillon_indices, echantillon_texte, A_INVERSES[a], b)
        score_stats = _score_texte_universel(texte_test)
        score_dict = _score_dictionnaire(texte_test)
        local_entries.append((a, b, score_stats, score_dict))
    return local_entries

def _construire_table_arc_en_ciel(texte_code, taille_echantillon):
    """Construit/cache une table arc-en-ciel simplifiée (clé -> scores d'empreinte)."""
    signature = texte_code[:taille_echantillon]
    cache_key = (signature, taille_echantillon)
    if cache_key in RAINBOW_CACHE:
        return RAINBOW_CACHE[cache_key]

    echantillon_texte = signature
    echantillon_indices = [CHAR_TO_INDEX.get(char) for char in echantillon_texte]

    nb_workers = max(1, min(MAX_WORKERS, len(KEY_SPACE)))
    taille_bloc = max(1, len(KEY_SPACE) // nb_workers)

    table = {}
    with ThreadPoolExecutor(max_workers=nb_workers) as executor:
        futures = [
            executor.submit(_worker_rainbow, chunk, echantillon_texte, echantillon_indices)
            for chunk in _chunks(KEY_SPACE, taille_bloc)
        ]
        for future in futures:
            for a, b, score_stats, score_dict in future.result():
                table[(a, b)] = (score_stats, score_dict)

    if len(RAINBOW_CACHE) > 8:
        RAINBOW_CACHE.pop(next(iter(RAINBOW_CACHE)))
    RAINBOW_CACHE[cache_key] = table
    return table

def _worker_evaluer_cles(chunk_cles, texte_code, indices):
    """Worker: évalue les clés candidates sur le texte complet."""
    resultats = []
    for a, b in chunk_cles:
        texte_dechiffre = _dechiffrement_depuis_indices(indices, texte_code, A_INVERSES[a], b)
        score = _score_texte_universel(texte_dechiffre) + 1.6 * _score_dictionnaire(texte_dechiffre)
        resultats.append((score, a, b, texte_dechiffre))
    return resultats

def cryptanalyse_brute_force(texte_code, callback=None, max_resultats=10):
    """Cryptanalyse hybride: dictionnaire + table arc-en-ciel + calcul parallèle."""
    if not texte_code:
        return []

    indices = [CHAR_TO_INDEX.get(char) for char in texte_code]
    taille_echantillon = min(len(texte_code), 120)

    rainbow_table = _construire_table_arc_en_ciel(texte_code, taille_echantillon)

    if callback:
        callback("Table arc-en-ciel prête.")

    preselection = []
    for (a, b), (score_stats, score_dict) in rainbow_table.items():
        score_pre = score_stats + 2.2 * score_dict
        preselection.append((score_pre, a, b))

    nb_candidats = len(preselection)
    meilleurs_candidats = heapq.nlargest(nb_candidats, preselection, key=lambda x: x[0])
    cles_candidates = [(a, b) for _, a, b in meilleurs_candidats]

    if callback:
        callback(f"{len(cles_candidates)} clés candidates à tester.")

    nb_workers = max(1, min(MAX_WORKERS, len(cles_candidates)))
    taille_bloc = max(1, len(cles_candidates) // nb_workers)

    resultats = []
    with ThreadPoolExecutor(max_workers=nb_workers) as executor:
        futures = [
            executor.submit(_worker_evaluer_cles, chunk, texte_code, indices)
            for chunk in _chunks(cles_candidates, taille_bloc)
        ]
        for future in futures:
            resultats.extend(future.result())

    if callback:
        callback("Évaluation finale terminée.")

    meilleurs = heapq.nlargest(max_resultats, resultats, key=lambda x: x[0])
    return [(a, b, texte, score) for score, a, b, texte in meilleurs]

# --- INTERFACE GRAPHIQUE ---

class CryptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Chiffrement Affine Grp1")
        self.root.geometry("700x500")
        
        # Style des onglets
        style = ttk.Style()
        style.configure('TNotebook.Tab', 
                        font=('Arial', 8, 'bold'),
                        padding=[11, 10])
        style.map('TNotebook.Tab',
                  background=[('selected', '#4CAF50')],
                  foreground=[('selected', 'green')])
        
        # Création des onglets
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=9)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=9)
        
        # Onglet 1 : Générer clé
        self.create_tab_generer()
        
        # Onglet 2 : Chiffrer
        self.create_tab_chiffrer()
        
        # Onglet 3 : Déchiffrer
        self.create_tab_dechiffrer()
        
        # Onglet 4 : Cryptanalyse
        self.create_tab_cryptanalyse()
    
    def create_tab_generer(self):
      
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Générer Clés")
        
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Générer Vos Clés Aléatoire Ici" , font=('Arial', 14, 'bold')).pack(pady=20)
        
        btn_generer = ttk.Button(frame, text="Générer Des clés", command=self.generer_cle_ui)
        btn_generer.pack(pady=10)
        
        self.label_cle = ttk.Label(frame, text="", font=('Arial', 12))
        self.label_cle.pack(pady=20)
    
    def create_tab_chiffrer(self):
      
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Chiffrer")
        
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Message à chiffrer :").pack(anchor='w')
        self.text_chiffrer = scrolledtext.ScrolledText(frame, height=5, width=60)
        self.text_chiffrer.pack(pady=5)
        
        # Clés
        cle_frame = ttk.Frame(frame)
        cle_frame.pack(pady=10)
        
        ttk.Label(cle_frame, text="Clé a :").grid(row=0, column=0, padx=5)
        self.entry_a_chiffrer = ttk.Entry(cle_frame, width=10)
        self.entry_a_chiffrer.grid(row=0, column=1, padx=5)
        
        ttk.Label(cle_frame, text="Clé b :").grid(row=0, column=2, padx=5)
        self.entry_b_chiffrer = ttk.Entry(cle_frame, width=10)
        self.entry_b_chiffrer.grid(row=0, column=3, padx=5)
        
        ttk.Button(frame, text="Chiffrer", command=self.chiffrer_ui).pack(pady=10)
        
        ttk.Label(frame, text="Résultat :").pack(anchor='w')
        self.result_chiffrer = scrolledtext.ScrolledText(frame, height=5, width=60)
        self.result_chiffrer.pack(pady=5)
    
    def create_tab_dechiffrer(self):
     
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Déchiffrer")
        
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Message chiffré :").pack(anchor='w')
        self.text_dechiffrer = scrolledtext.ScrolledText(frame, height=5, width=60)
        self.text_dechiffrer.pack(pady=5)
        
        # Clés
        cle_frame = ttk.Frame(frame)
        cle_frame.pack(pady=10)
        
        ttk.Label(cle_frame, text="Clé a :").grid(row=0, column=0, padx=5)
        self.entry_a_dechiffrer = ttk.Entry(cle_frame, width=10)
        self.entry_a_dechiffrer.grid(row=0, column=1, padx=5)
        
        ttk.Label(cle_frame, text="Clé b :").grid(row=0, column=2, padx=5)
        self.entry_b_dechiffrer = ttk.Entry(cle_frame, width=10)
        self.entry_b_dechiffrer.grid(row=0, column=3, padx=5)
        
        ttk.Button(frame, text="Déchiffrer", command=self.dechiffrer_ui).pack(pady=10)
        
        ttk.Label(frame, text="Résultat :").pack(anchor='w')
        self.result_dechiffrer = scrolledtext.ScrolledText(frame, height=5, width=60)
        self.result_dechiffrer.pack(pady=5)
    
    def create_tab_cryptanalyse(self):
     
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Cryptanalyse")
        
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Texte chiffré à analyser :").pack(anchor='w')
        self.text_cryptanalyse = scrolledtext.ScrolledText(frame, height=4, width=60)
        self.text_cryptanalyse.pack(pady=5)
        
        ttk.Button(frame, text="Analyser (Force Brute)", command=self.cryptanalyse_ui).pack(pady=10)
        
        ttk.Label(frame, text="Résultats possibles :").pack(anchor='w')
        self.result_cryptanalyse = scrolledtext.ScrolledText(frame, height=12, width=60)
        self.result_cryptanalyse.pack(pady=5)
    
    # --- FONCTIONS UI ---
    
    def generer_cle_ui(self):
        a, b = generer_cle()
        self.label_cle.config(text=f"Clés générées :\na = {a}\nb = {b}")
    
    def chiffrer_ui(self):
        try:
            texte = self.text_chiffrer.get("1.0", tk.END).strip()
            a = int(self.entry_a_chiffrer.get())
            b = int(self.entry_b_chiffrer.get())
            
            if math.gcd(a, N) != 1:
                messagebox.showerror("Erreur", f"La clé a={a} n'est pas valide (pgcd(a, {N}) doit être 1)")
                return
            
            resultat = chiffrement(texte, a, b)
            self.result_chiffrer.delete("1.0", tk.END)
            self.result_chiffrer.insert("1.0", resultat)
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des nombres valides pour a et b")
    
    def dechiffrer_ui(self):
        try:
            texte = self.text_dechiffrer.get("1.0", tk.END).strip()
            a = int(self.entry_a_dechiffrer.get())
            b = int(self.entry_b_dechiffrer.get())
            
            resultat = dechiffrement(texte, a, b)
            if resultat is None:
                messagebox.showerror("Erreur", "Clé invalide ! Impossible de calculer l'inverse modulaire.")
                return
            
            self.result_dechiffrer.delete("1.0", tk.END)
            self.result_dechiffrer.insert("1.0", resultat)
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des nombres valides pour a et b")
    
    def cryptanalyse_ui(self):
        texte = self.text_cryptanalyse.get("1.0", tk.END).strip()
        if not texte:
            messagebox.showwarning("Attention", "Veuillez entrer un texte chiffré")
            return
        
        self.result_cryptanalyse.delete("1.0", tk.END)
        self.result_cryptanalyse.insert("1.0", "Analyse en cours...\n\n")
        self.root.update()
        
        resultats = cryptanalyse_brute_force(texte)
        
        self.result_cryptanalyse.delete("1.0", tk.END)
        if resultats:
            for i, (a, b, texte_dechiffre, score) in enumerate(resultats, 1):
                self.result_cryptanalyse.insert(tk.END, f"--- Résultat {i} ---\n")
                self.result_cryptanalyse.insert(tk.END, f"Clé : a={a}, b={b} (score={score:.2f})\n")
                self.result_cryptanalyse.insert(tk.END, f"Texte : {texte_dechiffre[:150]}...\n\n")
        else:
            self.result_cryptanalyse.insert("1.0", "Aucun résultat probant trouvé.")

# --- LANCEMENT ---

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptApp(root)
    root.mainloop()
