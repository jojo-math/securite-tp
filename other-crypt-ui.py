import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math
import random

# --- CONFIGURATION ---
ALPHABET = 'àâäæçéèêëîïôöùûüÿœÀÂÄÆÇÉÈÊËÎÏÔÖÙÛÜŸŒ0123456789²& é"(-è_çà)=~{[|^@]}€¤£µ*ù%!§:/;.,?<>+°¨$£¥¢©®™✓✔✕✖¶§±÷×≈≠≤≥∞√∑πΩαβγδεζηθικλμνξοπρστυφχψωABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#\''
N = len(ALPHABET)

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
        if char in ALPHABET:
            x = ALPHABET.index(char)
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
        if char in ALPHABET:
            y = ALPHABET.index(char)
            resultat += ALPHABET[(a_inv * (y - b)) % N]
        else:
            resultat += char
    return resultat

def cryptanalyse_brute_force(texte_code, callback):
    """Cryptanalyse par force brute."""
    mots_cles = [" le ", " la ", " est ", " de ", " un "]
    resultats = []
    
    for a in range(1, N):
        if math.gcd(a, N) == 1:
            for b in range(N):
                test = dechiffrement(texte_code, a, b)
                if test and any(mot in test.lower() for mot in mots_cles):
                    resultats.append((a, b, test))
                    if len(resultats) >= 10:  # Limite à 10 résultats
                        return resultats
    return resultats

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
        
        resultats = cryptanalyse_brute_force(texte, None)
        
        self.result_cryptanalyse.delete("1.0", tk.END)
        if resultats:
            for i, (a, b, texte_dechiffre) in enumerate(resultats, 1):
                self.result_cryptanalyse.insert(tk.END, f"--- Résultat {i} ---\n")
                self.result_cryptanalyse.insert(tk.END, f"Clé : a={a}, b={b}\n")
                self.result_cryptanalyse.insert(tk.END, f"Texte : {texte_dechiffre[:150]}...\n\n")
        else:
            self.result_cryptanalyse.insert("1.0", "Aucun résultat probant trouvé.")

# --- LANCEMENT ---

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptApp(root)
    root.mainloop()
