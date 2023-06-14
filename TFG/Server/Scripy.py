import os
import sqlite3
import time
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd


class DatabaseAnalyzer:
    def __init__(self, db_file):
        self.db_file = db_file

    def analyze_tables(self):
        # Conexión a la base de datos
        conn = sqlite3.connect(self.db_file)

        # Obtener los datos de la tabla 'api_keys' si no está vacía
        df_api_keys = pd.read_sql_query("SELECT * FROM api_keys", conn)
        if not df_api_keys.empty:
            print("Tabla 'api_keys':")
            print(df_api_keys)
        else:
            print("Tabla 'api_keys' vacía")

        # Obtener los datos de la tabla 'blacklist' si no está vacía
        df_blacklist = pd.read_sql_query("SELECT * FROM blacklist", conn)
        if not df_blacklist.empty:
            print("\nTabla 'blacklist':")
            print(df_blacklist)
        else:
            print("Tabla 'blacklist' vacía")

        # Obtener los datos de la tabla 'request' si no está vacía
        df_request = pd.read_sql_query("SELECT * FROM requests", conn)
        if not df_request.empty:
            print("\nTabla 'request':")
            print(df_request)
            # Generar un gráfico de barras con los datos de la tabla 'request'
            df_request_by_ip = df_request.groupby('ip').size()
            df_request_by_ip.plot(kind='bar')
            plt.xlabel('IP')
            plt.ylabel('Cantidad de peticiones')
            plt.title('Peticiones por IP')
        else:
            print("Tabla 'request' vacía")

        # Cerrar la conexión a la base de datos
        conn.close()

        # Crear una carpeta con el nombre de la fecha y hora actual
        folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(folder_name, exist_ok=True)

        # Guardar los archivos en la carpeta si las tablas no están vacías
        if not df_api_keys.empty:
            api_keys_file = f"{folder_name}/api_keys.csv"
            df_api_keys.to_csv(api_keys_file, index=False)

        if not df_blacklist.empty:
            blacklist_file = f"{folder_name}/blacklist.csv"
            df_blacklist.to_csv(blacklist_file, index=False)

        if not df_request.empty:
            request_file = f"{folder_name}/request.csv"
            df_request.to_csv(request_file, index=False)
            plt.savefig(f"{folder_name}/graph.png")

        print(f"\nArchivos guardados en la carpeta: {folder_name}")


def main():
    # Ejemplo de uso
    db_file = "TFG.db"
    analyzer = DatabaseAnalyzer(db_file)

    while True:
        analyzer.analyze_tables()
        # Esperar 1 hora antes de ejecutar de nuevo
        time.sleep(3600)


if __name__ == '__main__':
    main()
