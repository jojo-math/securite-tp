ascii = 'àâäæçéèêëîïôöùûüÿœÀÂÄÆÇÉÈÊËÎÏÔÖÙÛÜŸŒ0123456789²& é"(-è_çà)=~{[|^@]}€¤£µ*ù%!§:/;.,?<>+°¨$£¥¢©®™✓✔✕✖¶§±÷×≈≠≤≥∞√∑πΩαβγδεζηθικλμνξοπρστυφχψωABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#\''
print(len(ascii))
x = input("Entrez le texte a chiffrer : ")
y = ""
## Algo de chiffrement : y = (a * x + b) mod m
for i in x:
    if i in ascii:
        y += ascii[(7 * ascii.index(i) + 27) % 190] # a = 7, b = 27, m = 190 : y = (a * x + b) mod m
    else:
        y += i
        print("Le caractere '" + i + "' n'est pas dans la table ASCII de notre programme, il a donc ete ajoute tel quel dans le texte chiffre.")
print("Texte chiffre: " + y)

## Algo de dechiffrement : x = a^-1 * (y - b) mod m
y = ""
y = input("Entrez le texte chiffre : ")
x = ""
for i in y:
    if i in ascii:
        x += ascii[(27 * (ascii.index(i) - 27)) % 190] # a^-1 = 27, b = 27, m = 190 : x = a^-1 * (y - b) mod m
    else:
        x += i
        print("Le caractere '" + i + "' n'est pas dans la table ASCII de notre programme, il a donc ete ajoute tel quel dans le texte dechiffre.")

print("Texte dechiffre: " + x)

