# NosAi static data

Questa directory contiene **snapshot generati** dei dati statici necessari all'intelligenza di NosAi.

## Principi

- I dati qui presenti sono read-only durante il runtime.
- Ogni snapshot deve avere provenance, source version, import timestamp e SHA-256.
- Nessun dato runtime (HP, posizione, cooldown, inventario corrente, target corrente, ecc.) va salvato qui.
- Nessuna API remota viene interrogata durante il gameplay.
- Gli import devono essere riproducibili e validare lo schema prima di sostituire uno snapshot.

## Dataset previsti

| Dataset | Uso | Dipendenze |
|---|---|---|
| items | equipaggiamento, consumabili, drop, prezzi statici | localization |
| monsters | statistiche, resistenze, skill, drop | skills, BCards |
| npcs | identità e proprietà statiche | localization, maps |
| skills | range, cooldown, costi, effetti | BCards |
| bcards | semantica degli effetti | — |
| maps | metadata delle mappe | map points/grid |
| map_points | spawn, punti di interesse, collegamenti | maps |
| quests | obiettivi e prerequisiti statici | items, monsters, npcs, maps |
| localization | nomi/descrizioni | dataset che usano codici ZTS |

## Pipeline

`provider/API -> raw snapshot -> schema validation -> normalization -> cross-reference validation -> indexed snapshot -> runtime`

La pipeline deve fallire in modo esplicito se una fonte è incompleta, incompatibile o non verificabile.
