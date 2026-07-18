# Knights and Knaves — Solution

## Identificazione del problema
Siamo su un'isola dove i **Knights** dicono sempre la verità e i **Knaves** mentono sempre.
Dobbiamo determinare chi è cosa tra A e B, analizzando le loro affermazioni.

## Dichiarazioni
- **A dice**: "B è un Knave."
- **B dice**: "Siamo entrambi Knights."

## Analisi dei casi

### Caso 1: A = Knight, B = Knight
- A dice "B è un Knave" → **falso** (B è Knight)
- A è Knight → deve dire verità → ❌ **CONTRADDIZIONE**
- **Impossibile.**

### Caso 2: A = Knight, B = Knave ✅
- A dice "B è un Knave" → **vero** (B è Knave)
- A è Knight → dice verità → ✅ OK
- B dice "Siamo entrambi Knights" → **falso** (nessuno è Knight)
- B è Knave → mente → ✅ OK
- **SOLUZIONE: A = Knight, B = Knave**

### Caso 3: A = Knave, B = Knight
- A dice "B è un Knave" → **falso** (B è Knight)
- A è Knave → mente → ✅ OK
- B dice "Siamo entrambi Knights" → **falso** (A è Knave)
- B è Knight → deve dire verità → ❌ **CONTRADDIZIONE**
- **Impossibile.**

### Caso 4: A = Knave, B = Knave
- A dice "B è un Knave" → **vero** (B è Knave)
- A è Knave → deve mentire → ❌ **CONTRADDIZIONE**
- **Impossibile.**

## Conclusione

L'unica combinazione logicamente coerente è:
- **A = Knight** (dice sempre la verità)
- **B = Knave** (mente sempre)

Spiegazione concisa: la dichiarazione di A è vera (B mente), quindi A è Knight. La dichiarazione di B è falsa (non sono entrambi Knights), quindi B mente — coerente per un Knave.

## Edge case ed esempio

**Edge case:** se entrambi fossero Knaves, la dichiarazione di A ("B è un Knave") sarebbe vera, ma un Knave non può dire la verità — questo edge case mostra come l'autoreferenzialità crei vincoli stringenti.

**Esempio analogo:** Se X dice "Y mentirà" e Y dice "X dice la verità", si crea un paradosso simile. Questo puzzle è un caso classico di logica proposizionale a due attori, dove una singola contraddizione elimina 3 dei 4 casi possibili.
