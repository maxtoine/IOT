# IOT

## Description

Ce projet Python implémente un serveur IoT léger capable de lire des trames série, de décoder des messages selon différents formats et de stocker les données dans une base SQLite.

Le serveur est construit avec une architecture modulaire :
- `adapter/` : gestion du port série
- `implementations/encodages/` : encodages binaires et texte
- `implementations/storages/` : persistance des données
- `core/` : logique principale du serveur et modèles de données
- `interface/` : interfaces pour encodage et stockage

## Fonctionnalités

- Lecture de données depuis un port série
- Découpage et extraction de trames complètes
- Décodage binaire (`BinaryEncodage`) et texte (`TextEncodage`)
- Filtrage par adresse de destination
- Sauvegarde automatique dans une base SQLite

## Installation

1. Cloner le dépôt

```bash
git clone <votre-repo>
cd IOT
```

2. Installer les dépendances

```bash
pip install -r requirements.txt
```

3. S'assurer que le port série est accessible et disponible

> Exemple : `/dev/pts/4` ou `/dev/ttyUSB0`

## Utilisation

Le point d'entrée principal est `main.py`.

```bash
python main.py
```

Par défaut, `main.py` initialise :
- `BinaryEncodage()` pour le décodage binaire
- `SQLiteStorage("values.db")` pour la base de données
- `SerialAdapter(port="/dev/pts/4", baudrate=115200, length=encodage.framing_length)`
- `ServerIot(..., mon_adresse="0")`

### Configuration

Vous pouvez modifier `main.py` ou ajouter un mécanisme de configuration via `config.py`.

`config.py` expose également une classe `ServerConfig` capable de charger :
- `SERIAL_PORT`
- `BAUDRATE`
- `STORAGE_PATH`

## Architecture

- `core/server.py` : boucle principale de lecture série, extraction des trames, décodage et sauvegarde
- `adapter/serial_adapter.py` : initialisation du port série, lecture brute et fermeture
- `implementations/encodages/binary_encodage.py` : trames binairement packées via ctypes
- `implementations/encodages/text_encodage.py` : trames textuelles séparées par `\n` et champ `;`
- `implementations/storages/sqlite_storage.py` : persistance SQLite avec opérations CRUD de base

## Extension

Pour ajouter un nouvel encodage :
1. Créer une classe héritant de `InterfaceEncodage`
2. Implémenter `extract_frames`, `extract_address`, `encode` et `decode`
3. Instancier la nouvelle classe dans `main.py`

Pour ajouter un nouveau stockage :
1. Créer une classe héritant de `InterfaceSave`
2. Implémenter `save_data`, `search_data`, `load_data`, `delete_data` et `data_exists`
3. Utiliser la classe dans `main.py`

## Dépendances

- `pyserial` pour la communication série
- `sqlite3` est inclus dans Python standard

## Remarques

- Le serveur conserve le buffer de lecture tant que les heures complètes ne sont pas disponibles.
- Seules les trames destinées à `mon_adresse` ou à l'adresse `0` sont traitées.
- Pour arrêter proprement le serveur, utilisez `Ctrl+C`.
