from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, session

import cv2
import os
from PIL import Image
import io
import time
from funciones import fecha, verificar_comida
import firebase_admin
from firebase_admin import credentials, firestore, storage
from funciones import fecha
import io
import cv2
from datetime import datetime

# Inicializar la aplicación con SocketIO
app = Flask(__name__)

app.secret_key = 'tu_clave_secreta' 

cred = credentials.Certificate("FIREBASE/comedor.json")
firebase_admin.initialize_app(cred,{
    'storageBucket': 'comedor-e91a3.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()

'''
def upload_to_firebase(image, image_name):
    global dni_global  
    global tipo_comida_global
    global photo_status

    image_stream = io.BytesIO()

    success, encoded_image = cv2.imencode('.jpg', image)
    if not success:
        print("Failed to encode image")
        return
    
    image_stream.write(encoded_image.tobytes()) 
    image_stream.seek(0)
    blob = bucket.blob(f'FOTOS/{image_name}')
    blob.upload_from_file(image_stream, content_type='image/jpeg')  
    blob.make_public()
    print(f"Image uploaded to Firebase: {blob.public_url}")

    # Create a reference to the collection for the current meal type
    collection_ref = db.collection('ASISTENCIA_' + tipo_comida_global)

    # Query to check if a record with the same dni_global and Fecha_hoy already exists
    query = collection_ref.where('dni', '==', str(dni_global)).where('Fecha_hoy', '==', str(fecha())).get()

    if query:  # If the query returns any results, the data already exists
        print("Record already exists, skipping upload")
        return False   

    data = {
        'Fecha_hoy': fecha(),
        'dni': dni_global,
        'fecha': firestore.SERVER_TIMESTAMP,  # Current timestamp
        'foto': blob.public_url
    }

    collection_ref.add(data)
    print("Data added to Firebase:", data)

    # Check the photo status before returning True
    if str(photo_status) == str(True):
        return True

    return False

'''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    
    user_data = session.get('user_data') 
    print(user_data)

    '''
    hoy = datetime.now().strftime('%d/%m/%Y')  # Obtiene la fecha de hoy en formato DD/MM/YYYY

    # Filtrar documentos por fecha y tipo
    coleccion_ref = db.collection(f'ASISTENCIA_ALMUERZO')
    documentos = coleccion_ref.where('Fecha_hoy', '==', hoy).stream()
    
    datos = [doc.to_dict() for doc in documentos]
    print(datos)
    '''
    return render_template('dashboard.html',user_data=user_data)



@app.route('/submit-data', methods=['POST'])
def submit_data():
    data = request.get_json()  # Obtener los datos JSON enviados por el cliente
    input_name = data['name']
    input_password = data['pass']
    input_uuid = data['uuid']

    users_ref = db.collection('User')
    users = users_ref.stream()
    user_list = [user.to_dict() for user in users]

    # Verificar si hay coincidencia con los datos del cliente
    for user_data in user_list:
        stored_username = user_data.get('Username')  # Obtener el Username almacenado
        stored_password = user_data.get('password')  # Obtener el Password almacenado
        stored_uuid = user_data.get('uuid')          # Obtener el UUID almacenado
        
        # Comprobar si el username, password y uuid coinciden
        if stored_username == input_name and stored_password == input_password and stored_uuid == input_uuid:
            print(user_data)
            session['user_data'] = user_data
            return jsonify({
                 "status": "success", 
                 "redirect": url_for('dashboard'),
                 })          

    # Si no hay coincidencias, devolver acceso denegado
    return jsonify({"status": "fail", "message": "Acceso denegado, datos incorrectos"})

@app.route('/Solicitud', methods=['POST'])
def Solicitud():
    

    val = 0
    val1 = 0


    data = request.get_json()
    tipo = verificar_comida()

    if tipo == "Fuera de los tiempos de comida":
        print("FUERA DE SERVICIO")
        return jsonify({"status": "success", "message": "No es hora de Comer"})
    else:
        users_ref = db.collection('ASISTENCIA_'+ tipo)
        users = users_ref.stream()
        user_list = [user.to_dict() for user in users]
        
        users_ref1 = db.collection('Estudiantes')
        users1 = users_ref1.stream()
        user_list2 = [user1.to_dict() for user1 in users1]

        for user_data2 in user_list2: 
                DNI_BD_ESTUDIANTES = user_data2.get('dni')
                if str(DNI_BD_ESTUDIANTES) == str(data):         
                    val = 1
        if val == 1:
            #return jsonify({"status": "success", "redirect": url_for('camera')})
            print("EXISTE EL USUARIO") 
            for user_data in user_list:
                        DNI_VALIDACION = user_data.get('dni')
                        FECHA_BD_ESTUDIANTES = user_data.get('Fecha_hoy')
                        #print ("FECHA: ",FECHA_BD_ESTUDIANTES)
                        #print ("FECHA HOY: ",fecha())
                        if str(DNI_VALIDACION) == str(data) and str(FECHA_BD_ESTUDIANTES) == str(fecha()) :
                            #print("se ha regitrado")
                            val1 = 1
            if val1 == 1:
                print("se ha regitrado")
                val1 = 0
                return jsonify({"status": "success", "message":"ya esta registrado"})
            else:
                print("no se ha registrado") 
                
                session['data'] = {
                    "tipo": tipo,
                    "dni_validacion": data
                }
    
                return jsonify({"status": "success1", "redirect": url_for('camera')})
                
        else:
            print("no existe user")
            return jsonify({"status": "error", "message": "El usuario no existe"})


@app.route('/camera')
def camera():
    data = session.get('data') 
    print(data)
    return render_template("camera.html", data=data)


@app.route('/final')
def final():
    tipo = request.args.get('tipo')
    print("Tipo:", tipo)
    
    return render_template('result.html',tipo=tipo)


@app.route('/actividad')
def actividad():
    tipo = verificar_comida()
    
    if tipo == "Fuera de los tiempos de comida":
        print("FUERA DE SERVICIO")
        return render_template('actividad.html', data="Fuera de los tiempos de comida")
        
    else:  
        return render_template('actividad.html', tipo=tipo)
    
@app.route('/actividad/datos')
def obtener_datos():
    tipo = verificar_comida()
    hoy = datetime.now().strftime('%d/%m/%Y')  # Obtiene la fecha de hoy en formato DD/MM/YYYY

    # Filtrar documentos por fecha y tipo
    coleccion_ref = db.collection(f'ASISTENCIA_{tipo}')
    documentos = coleccion_ref.where('Fecha_hoy', '==', hoy).stream()
    
    datos = [doc.to_dict() for doc in documentos]
    return jsonify(datos)





'''
camera = cv2.VideoCapture(0)  

def gen_frames():  
    margin = 50  
    photo_taken = False  # Mantener el estado de si se ha tomado una foto

    while True:
        success, frame = camera.read()  
        if not success:
            break
        else:
            detector = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
            faces = detector.detectMultiScale(frame, 1.1, 7)
            
            # Solo proceder si se detectan rostros
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    # Ajustar el tamaño del cuadro para hacerlo más grande
                    x = max(0, x - margin)  
                    y = max(0, y - margin)
                    w += 2 * margin
                    h += 2 * margin
                    
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    # Solo tomar la foto si no se ha tomado una previamente
                    if not photo_taken:  
                        time.sleep(3)  # Esperar 3 segundos antes de tomar la foto
                        face_image = frame[y:y+h, x:x+w]
                        image_name = f'face_{int(cv2.getTickCount())}.jpg'
                        
                        # Subir la imagen a Firebase o realizar otra acción
                        upload_to_firebase(face_image, image_name)

                        print("Foto tomada y subida con éxito")  
                        photo_taken = True  # Cambiar el estado a True después de tomar la foto
                        
                        break  # Salir del bucle for después de tomar la foto

            # Reiniciar photo_taken si ya no hay rostros detectados en el siguiente ciclo
            if len(faces) == 0:
                photo_taken = False  # Restablecer para permitir tomar otra foto

            # Codificar el frame actual a JPEG para la transmisión
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


'''




if __name__ == '__main__':

    app.run(debug=False) 

#cap.release()