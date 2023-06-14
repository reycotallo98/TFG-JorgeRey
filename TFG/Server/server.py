import datetime
import re
import socket
import sqlite3
import threading
import openai
import Scripy

API_KEY = '' # OpenAI Api Key
IP = '' # Local IP

class MessageFilter:
    def __init__(self):
        self.palabras_prohibidas = ['eval', 'exec', 'import', 'os']

    def filtrar_mensaje(self, mensaje):
        for palabra in self.palabras_prohibidas:
            if palabra.lower() in mensaje.lower():
                return False  # El mensaje contiene una palabra prohibida
        # Verificar si el mensaje contiene caracteres especiales
        return self.contiene_caracteres_especiales(mensaje)  # El mensaje contiene caracteres especiales




    def contiene_caracteres_especiales(self, mensaje):
        # Patrón regex para caracteres especiales
        patron = r'[!@#$%^&*(),.?":{}|<>]'

        # Buscar coincidencias en el mensaje
        coincidencias = re.match(patron, mensaje)

        # Devolver True si se encontraron coincidencias, False en caso contrario
        return coincidencias is None


class RequestLog:
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS requests
                     (ip TEXT, timestamp TEXT, request TEXT)''')
        conn.commit()
        c.execute('''CREATE TABLE IF NOT EXISTS api_keys
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, api_key TEXT)''')
        conn.commit()
        c.execute('''CREATE TABLE IF NOT EXISTS blacklist
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT)''')
        conn.commit()
        conn.close()

    def add_user(self, ip, api_key):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.close()
        c = conn.cursor()
        c.execute("INSERT INTO api_keys (ip, api_key) VALUES (?, ?)", (ip, api_key))
        conn.commit()
        conn.close()

    def get_user(self, ip):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT api_key FROM api_keys WHERE ip=?", (ip,))
        api = c.fetchone()
        conn.close()
        return api

    def add_request(self, ip, request):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute(f"INSERT INTO requests VALUES (?, ?, ?)", (ip, timestamp, request))
        conn.commit()
        conn.close()

    def get_requests_by_ip(self, ip):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM requests WHERE ip=?", (ip,))
        requests = c.fetchone()
        conn.close()
        return requests

    def get_all_requests(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM requests")
        all_requests = c.fetchall()
        conn.close()
        return all_requests

    def get_requests_today(self, ip):
        today = datetime.date.today()
        start_of_day = datetime.datetime.combine(today, datetime.time.min)
        end_of_day = datetime.datetime.combine(today, datetime.time.max)

        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM requests WHERE ip=? AND timestamp BETWEEN ? AND ?",
                  (ip, start_of_day, end_of_day))
        requests = int(c.fetchone()[0])
        conn.close()
        return requests

    def get_request_count_today(self, ip):
        today = datetime.date.today()
        start_of_day = datetime.datetime.combine(today, datetime.time.min)
        end_of_day = datetime.datetime.combine(today, datetime.time.max)

        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT COUNT(ip) FROM requests WHERE ip=? AND timestamp BETWEEN ? AND ?",
                  (ip, start_of_day, end_of_day))
        count = int(c.fetchone()[0])
        conn.close()
        return count

    def add_user_to_blacklist(self, ip):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT INTO blacklist (ip) VALUES (?)", (ip,))
        conn.commit()
        conn.close()

    def find_user_in_blacklist(self, ip):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM blacklist WHERE ip=?", (ip,))
        user = c.fetchone()
        conn.close()
        return user


def conexiones():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, 1234))
    server_socket.listen(10)
    bd = RequestLog("TFG.db")

    filtro = MessageFilter()
    print('Servidor en espera de conexiones... en ' + IP)

    while True:
        client_socket, client_address = server_socket.accept()
        print('Conexión establecida desde:', client_address)
        hilo = threading.Thread(target=proceso, args=(bd, client_socket, client_address, filtro)) # Crea un hilo que gestiona la petición
        hilo.start()


def proceso(bd, client_socket, client_address, filtro):
    print("creo hilo")
    mensaje = client_socket.recv(1024).decode('utf-8')
    print('Mensaje recibido:', mensaje)
    client_address = client_address[0]
    if mensaje.startswith("API.."):
        bd.add_user(client_address, mensaje.split("..")[1])
        client_socket.send("API Registrada".encode('utf-8'))
    else:
        if bd.find_user_in_blacklist(client_address) is None or not filtro.filtrar_mensaje(mensaje):

            apik = bd.get_user(client_address)

            if bd.get_requests_today(client_address) < 10 or apik is not None:

                if apik is not None:
                    apik = apik[0][0:-1]
                    print(apik)
                    respuesta = obtener_respuesta(mensaje, apik)
                else:
                    respuesta = obtener_respuesta_noAPI(mensaje)

                print('Respuesta:', respuesta)
                bd.add_request(client_address, mensaje)
            else:
                respuesta = "Has realizado el numero máximo de peticiones gratuitas, para continuar ingrese su propia API de openAI escribiendo API..APIKEY siendo APIKEY tu API"

            client_socket.sendall(respuesta.encode('utf-8'))
        else:
            bd.add_user_to_blacklist(client_socket)
            client_socket.send("Se ha detectado actividad maliciosa en tu cuenta, y se bloqueó tu IP")
    client_socket.close()


def obtener_respuesta(mensaje, api):
    openai.api_key = api
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt="Respondeme en una línea a: " + mensaje,
        max_tokens=900,
        n=1,
        stop=None,
        temperature=0.5,
    )
    respuesta = response.choices[0].text
    return respuesta


def obtener_respuesta_noAPI(mensaje):
    openai.api_key = API_KEY
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt="Respondeme en una línea a: " + mensaje,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    )
    respuesta = response.choices[0].text
    return respuesta


def main():
    bd = RequestLog("TFG.db")

    bd.create_table()

    hilo1 = threading.Thread(target=conexiones, )  # Iniciamos el gestor de conexiones del server
    hilo2 = threading.Thread(target=Scripy.main, daemon=True)  # Iniciamos el Script de analisis de datos
    hilo1.start()
    hilo2.start()

    hilo2.join()


if __name__ == '__main__':
    main()
