import json
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
import pandas as pd

# --- Fonction Python pour Transformer et Charger (Regroupé) ---
def transform_load_weather_data(task_instance):
    """Récupère le JSON brut via XCom, transforme et charge sur S3."""
    
    # 1. Récupération des données extraites à l'étape précédente via XCOM
    data = task_instance.xcom_pull(task_ids="extract_weather_data")
    
    # 2. Transformation (Exemple de conversion Kelvin -> Celsius/Fahrenheit)
    city = data.get("name")
    weather_desc = data["weather"]["description"]
    temp_f = (data["main"]["temp"] - 273.15) * 9/5 + 32 # Conversion Kelvin vers Fahrenheit
    
    # Création du dictionnaire
    transformed_data = {
        "City": city,
        "Description": weather_desc,
        "Temperature_F": temp_f,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 3. Conversion en DataFrame
    df = pd.DataFrame([transformed_data])
    
    # 4. Chargement vers Amazon S3 (Remplacer par tes infos de bucket)
    # AWS Credentials configurées via AWS CLI (STS) ou via les storage_options
    file_name = f"s3://ton-nom-de-bucket-s3/current_weather_data_{city}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
    
    # df.to_csv(file_name, index=False) # Ligne à décommenter quand tu auras configuré S3
    print(f"Data transformed and theoretically loaded to {file_name}")

# --- Paramètres par défaut du DAG ---
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

# --- Définition du DAG ---
with DAG(
    dag_id="weather_etl_pipeline",
    default_args=default_args,
    description="ETL météo avec Sensor, SimpleHttp et PythonOperator",
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["etl", "weather", "AWS"],
) as dag:

    # Tâche 1 : Sensor pour vérifier que l'API est en ligne
    is_weather_api_ready = HttpSensor(
        task_id="is_weather_api_ready",
        http_conn_id="weather_map_api", # Configurera via l'UI Airflow
        endpoint="/data/2.5/weather?q=Portland&appid={{ var.value.openweather_api_key }}" # Utilisation des Variables Airflow
    )

    # Tâche 2 : Extraction HTTP propre
    extract_weather_data = SimpleHttpOperator(
        task_id="extract_weather_data",
        http_conn_id="weather_map_api",
        endpoint="/data/2.5/weather?q=Portland&appid={{ var.value.openweather_api_key }}",
        method="GET",
        response_filter=lambda response: json.loads(response.text), # Convertit directement en JSON
        log_response=True
    )

    # Tâche 3 : Transformation et Load
    transform_load_weather_data = PythonOperator(
        task_id="transform_load_weather_data",
        python_callable=transform_load_weather_data
    )

    # --- Définition de l'ordre d'exécution ---
    is_weather_api_ready >> extract_weather_data >> transform_load_weather_data