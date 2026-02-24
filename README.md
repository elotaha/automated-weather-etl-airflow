#  Pipeline ETL Automatisé de Données Météo (AWS & Apache Airflow)

##  Contexte du Projet
Dans le cadre de mon développement en pipeline côté prodution, je construis un pipeline ETL (Extract, Transform, Load) automatisé de bout en bout. 
Ce projet extrait des données météorologiques en temps réel pour une ville spécifique depuis l'**API OpenWeatherMap**, applique des transformations avec **Python (Pandas)**, et charge automatiquement les données traitées sous forme de fichier CSV dans un Data Lake **Amazon S3**. L'ensemble du workflow est orchestré et planifié quotidiennement à l'aide d'**Apache Airflow**, hébergé sur une instance AWS EC2.

---

##  Stack Technique & Architecture
*   **Infrastructure Cloud :** AWS EC2 (Ubuntu, t2.small), AWS S3, AWS IAM Roles, AWS CLI (Jetons STS)
*   **Orchestration :** Apache Airflow (Standalone)
*   **Langage & Traitement des données :** Python 3.10, Pandas
*   **Connecteurs :** S3FS, API REST

---

##  Workflow du DAG Airflow
Le pipeline est défini dans un Graphe Orienté Acyclique (DAG) nommé `weather_etl_pipeline` et se compose de 3 tâches séquentielles utilisant des opérateurs natifs d'Airflow :

1.  **`is_weather_api_ready` (HttpSensor) :** Interroge intelligemment le point de terminaison de l'API pour vérifier sa disponibilité et la validité des identifiants avant d'autoriser le pipeline à se poursuivre.
2.  **`extract_weather_data` (SimpleHttpOperator) :** Exécute une requête GET vers l'API OpenWeatherMap, filtre la réponse et la convertit au format JSON.
3.  **`transform_load_weather_data` (PythonOperator) :** 
    *   Récupère les données JSON brutes de la tâche précédente en utilisant le système de messagerie interne **Airflow XComs**.
    *   Transforme les données (ex : conversion des températures de Kelvin vers Fahrenheit, formatage des horodatages) avec **Pandas**.
    *   Charge de manière sécurisée le DataFrame final structuré directement dans un bucket Amazon S3 sous la forme d'un fichier CSV horodaté.

---

## 📁 Structure du Dépôt
```text
automated-weather-etl-airflow/
│
├── dags/                       
│   └── weather_dag.py          # La définition du DAG Airflow et les fonctions Python
│
├── images/                     # Preuves d'exécution et captures d'écran de l'UI
│   ├── airflow_login.png       
│   ├── airflow_dags.png        
│   └── aws_s3_success.png      
│
├── .gitignore                  
├── requirements.txt            # Dépendances Python (pandas, s3fs, apache-airflow)
└── README.md                   
```
---

## Configuration de l'Infrastructure
- L'environnement a été configuré sur une instance AWS EC2 en utilisant un environnement virtuel Python (airflow_venv). Airflow fonctionne sur le port 8080 (Règle de sécurité Custom TCP).
Vous pouvez visualisez sur image quelques étapes de mon projet en capture d'écran au fur et à mesure de mon avancement.
---

## Bonnes Pratiques de Sécurité Implémentées
• Aucun secret en dur : Les clés API sont gérées de manière sécurisée via l'interface des Connexions internes d'Airflow (weather_map_api).
• Rôles IAM & AWS CLI : Les identifiants AWS (Clés d'accès & Jetons de session) ont été configurés via AWS CLI pour autoriser de façon sécurisée l'instance EC2 à écrire dans le bucket S3 sans exposer de clés dans le code source.
##  Prochaines Étapes & Améliorations
• Finaliser le projet.
• Implémenter un pipeline CI/CD avec GitHub Actions pour automatiser le déploiement des DAGs sur le serveur EC2.
• Conteneuriser l'environnement Airflow en utilisant Docker & Docker Compose.
