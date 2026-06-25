# MVPT-4 — Package YunoHost

Calculateur de scores pour le **Motor-Free Visual Perception Test, 4e édition** (MVPT-4).

## Fonctionnalités

- Saisie des 45 items avec retour visuel immédiat (vert/rouge)
- Calcul automatique du score standard, percentile et âge équivalent
- Interprétation basée sur la comparaison âge réel / âge équivalent
- Gestion des sessions patients (sauvegarde, recherche, filtrage, tri)
- Export/import JSON pour la portabilité des données
- Rapport HTML imprimable par patient

## Arborescence du package

```
mvpt4_ynh/
├── manifest.toml              # Métadonnées YunoHost
├── scripts/
│   ├── install                # Script d'installation
│   ├── remove                 # Désinstallation
│   ├── backup                 # Sauvegarde
│   ├── restore                # Restauration
│   └── upgrade                # Mise à jour
├── conf/
│   ├── nginx.conf             # Configuration reverse proxy
│   └── systemd.service        # Service gunicorn
└── sources/
    └── app/
        ├── app.py             # Backend Flask (logique métier + API REST)
        ├── wsgi.py            # Point d'entrée WSGI pour gunicorn
        ├── init_db.py         # Initialisation SQLite
        ├── templates/
        │   ├── index.html     # Interface principale
        │   └── rapport.html   # Rapport imprimable
        └── static/
            ├── css/style.css
            └── js/app.js
```

## API REST

| Méthode | Route                  | Description                          |
|---------|------------------------|--------------------------------------|
| GET     | `/api/sessions`        | Liste des sessions (filtres, tri)    |
| GET     | `/api/sessions/<id>`   | Détail d'une session                 |
| POST    | `/api/sessions`        | Créer ou mettre à jour une session   |
| DELETE  | `/api/sessions/<id>`   | Supprimer une session                |
| POST    | `/api/calculate`       | Calculer les scores                  |
| GET     | `/api/export`          | Export JSON de toutes les sessions   |
| POST    | `/api/import`          | Import JSON                          |
| GET     | `/rapport/<id>`        | Rapport HTML imprimable              |

## Installation sur YunoHost

```bash
yunohost app install https://github.com/votre-org/mvpt4_ynh
```

## Développement local

```bash
cd sources/app
python3 -m venv venv && source venv/bin/activate
pip install flask gunicorn
export DB_PATH=./mvpt4_dev.db
python3 app.py
# → http://localhost:5000
```

## Données

Les sessions sont stockées dans une base SQLite à `__DATA_DIR__/mvpt4.db`.  
La désinstallation conserve les données (`data_dir` non supprimé).  
Utilisez l'export JSON intégré pour sauvegardes manuelles.
