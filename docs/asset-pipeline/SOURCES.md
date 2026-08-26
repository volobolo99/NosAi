# NosTale asset pipeline — fonti e provenienza

Questo documento definisce le sorgenti utilizzate da NosAi per costruire localmente il registry grafico. Il repository contiene codice, metadata e riferimenti alle sorgenti; gli asset proprietari del client NosTale non vengono redistribuiti nel repository.

## 1. Taletool

Repository: https://github.com/imxeno/taletool

Riferimento usato: commit `5d15f4830c0ea7c4b2175c1aed5e73c130379367`

Copertura documentata:
- archivi binari `.NOS` e split archive;
- CCINF / `NSpnData.NOS` e `NSmnData.NOS`;
- texture;
- sprite;
- `NSpcData` / `NSmcData` sprite animations;
- `NSpmData` player resource remaps;
- `NStgData` / `NStgeData` geometry/render nodes;
- `NSedData`, `NSeffData`, `NSemData`, `NSesData` effects;
- mappe e ulteriori dati.

## 2. OnexExplorer / OnexExplorerCli

Repository individuati nella ricerca GitHub:
- https://github.com/OnexTale/OnexExplorer
- https://github.com/GorlikItsMe/OnexExplorerCli

Sono sorgenti di confronto/validazione dei formati. Non vengono trattati come fonte primaria degli asset del client.

## 3. Client NosTale locale — fonte primaria

Il renderer deve preferire sempre la copia locale del client selezionata dall'utente:

```text
NosTale root
└── NostaleData
    ├── *.NOS
    ├── NSpnData.NOS
    ├── NSpcData.NOS
    ├── NSpmData.NOS
    ├── texture/sprite resources
    └── effect/geometry resources
```

Gli asset locali vengono indicizzati con SHA-256 e riferimenti relativi. Non vengono modificati.

## 4. Regola di provenienza

Priorità:

1. asset del client locale;
2. metadata/format reference da Taletool;
3. tool open-source di confronto;
4. eventuali fonti online aggiuntive solo se legalmente redistribuibili e con licenza compatibile.

Non scaricare nel repository binari proprietari di NosTale o raccolte di asset del gioco prive di licenza di redistribuzione.

## 5. Obiettivo di estrazione

Il registry deve essere in grado di collegare:

```text
NSpn -> NSpc -> frame -> NSpm -> sprite/texture -> layer
                             \-> effects/geometry
```

Il risultato viene salvato come manifest/metadata locale e utilizzato dal renderer 2.5D.
