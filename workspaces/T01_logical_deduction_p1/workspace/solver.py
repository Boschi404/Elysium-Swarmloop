#!/usr/bin/env python3
"""Knights and Knaves solver — verifica automatizzata del puzzle T01."""
import sys

def is_knight(person: bool) -> bool:
    """True = Knight, False = Knave."""
    return person

def verifica(a_is_knight: bool, b_is_knight: bool) -> tuple[bool, str]:
    """
    Verifica se l'assegnazione A/B è coerente.
    Knights dicono SEMPRE vero, Knaves SEMPRE falso.
    """
    a_says = not b_is_knight          # A: "B è un Knave"
    b_says = a_is_knight and b_is_knight  # B: "Siamo entrambi Knights"

    a_coerente = a_is_knight == a_says   # Knight→vero, Knave→falso
    b_coerente = b_is_knight == b_says

    if a_coerente and b_coerente:
        return (True, f"A={'Knight' if a_is_knight else 'Knave'}, B={'Knight' if b_is_knight else 'Knave'} ✅")
    else:
        problemi = []
        if not a_coerente: problemi.append(f"A={'Knight' if a_is_knight else 'Knave'} dice '{a_says}' → contraddizione")
        if not b_coerente: problemi.append(f"B={'Knight' if b_is_knight else 'Knave'} dice '{b_says}' → contraddizione")
        return (False, "; ".join(problemi))

def main():
    casi = [
        (True,  True,  "Caso 1: A=Knight, B=Knight"),
        (True,  False, "Caso 2: A=Knight, B=Knave"),
        (False, True,  "Caso 3: A=Knave, B=Knight"),
        (False, False, "Caso 4: A=Knave, B=Knave"),
    ]

    print("=" * 55)
    print("  T01 — Knights and Knaves: Analisi di tutti i casi")
    print("=" * 55)
    print()

    soluzione_trovata = False
    for a_knight, b_knight, nome in casi:
        print(f"  {nome}")
        print(f"  ├─ A dice: 'B è un Knave' (→ {not b_knight})")
        print(f"  └─ B dice: 'Siamo entrambi Knights' (→ {a_knight and b_knight})")
        ok, msg = verifica(a_knight, b_knight)
        print(f"     → {msg}")
        print()

        if ok:
            soluzione_trovata = True

    print("=" * 55)
    if soluzione_trovata:
        print("  ✅ SOLUZIONE UNICA: A = Knight, B = Knave")
    else:
        print("  ❌ Nessuna soluzione valida trovata (errore nel ragionamento)")
        sys.exit(1)
    print("=" * 55)

if __name__ == "__main__":
    main()
