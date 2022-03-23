import uvicorn
from fastapi import FastAPI, File, UploadFile, Body, Form, BackgroundTasks, Depends
from typing import Optional
from deepface import DeepFace
import os
import shutil
from starlette.testclient import TestClient
from pymongo import MongoClient
from datetime import datetime
import time
from pytz import timezone
from bson.json_util import dumps
from bson.objectid import ObjectId
from pydantic import BaseModel
from fastapi_utils.tasks import repeat_every
import requests
import json
import random
import utils.auxiliary_functions as auxiliary_functions


class clock_in_list_model(BaseModel):
    company_code: str
    employee_code: str
    start: int
    amount: Optional[int] = 20

marcaciones_sin_procesar = []

app = FastAPI(dependencies=[Depends(auxiliary_functions.get_api_key)])

client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")


IMAGEDIR = "./tmp/"

# def connect_to_mongo_client():
#     client = MongoClient(host='test_mongodb',
#                          port=27017, 
#                          username='root', 
#                          password='pass',
#                         authSource="admin")
#     return client

def get_db(company_code):
    dbnames = client.list_database_names()
    if company_code in dbnames:   
        db = client[company_code]
        return db
    else:
        return False


@app.get('/')
def ping_server():
    return "DeepFace api is running!"

@app.post('/verify')
async def recognize_person(company_code: str = Form(...), employee_code: str = Form(...), file: UploadFile = File(...)):
    db = get_db(company_code)
    if not db:
        return{"code": 1001, "status": "compañia no existe"}

    collection = db["colaboradores"]

    collaborator = { "employee_code": employee_code}
    x = collection.find_one(collaborator)
    if not x:
        return{"access": False, "code": 1002, "status": "colaborador no existe"}

    
    
    print("recibiendo imagen")
    image_path = "./db/" + company_code + "/" + employee_code

    # if not os.path.isdir(image_path):
    #     return "employee doesnt exist"

    # guardar archivo como jpg en tmp folder
    with open(f"{IMAGEDIR}image.jpg", "wb") as image:
        shutil.copyfileobj(file.file, image)
    
    # encontrar imagenes parecidas en carpeta de imagenes
    metrics = ["cosine", "euclidean", "euclidean_l2"]
    models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]
    try:
        df = DeepFace.find(img_path = r"./tmp/image.jpg", db_path = image_path, distance_metric = metrics[0], model_name = models[1])
    except ValueError as e:
        if str(e) == "Face could not be detected. Please confirm that the picture is a face photo or consider to set enforce_detection param to False.":
            return{"access": False, "code": 3001, "status": "face could not be detected", "name": None}


    # borrar imagenes de tmp folder
    for filename in os.listdir(IMAGEDIR):
        file_path = os.path.join(IMAGEDIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    try:
        if(not df.empty):
            print(df.head())
            if df['Facenet_cosine'][0] < 0.4:     
                return {"access": True, "code": 4001, "status": "found, face recognized", "name": x["nombre_completo"]}
            else:
                return {"access": False, "code": 3002, "status": "found, face not recognized", "name": None}
        else:
            return {"access": False, "code": 3002, "status": "no similar faces found", "name": None}
        
    except Exception as e:
        print(e)
        return{"access": False, "code": 8003, "status": e, "name": None}

@app.post('/verify_admin')
async def recognize_person(company_code: str = Form(...), employee_code: str = Form(...), file: UploadFile = File(...)):
    db = get_db(company_code)
    if not db:
        return{"code": 1001, "status": "compañia no existe"}

    collection = db["administradores"]

    collaborator = { "employee_code": employee_code}
    x = collection.find_one(collaborator)
    if not x:
        return{"code": 1003, "status": "administrador no existe"}

    
    
    print("recibiendo imagen")
    image_path = "./db/" + company_code + "/" + employee_code

    # if not os.path.isdir(image_path):
    #     return "employee doesnt exist"

    # guardar archivo como jpg en tmp folder
    with open(f"{IMAGEDIR}image.jpg", "wb") as image:
        shutil.copyfileobj(file.file, image)
    
    # encontrar imagenes parecidas en carpeta de imagenes
    metrics = ["cosine", "euclidean", "euclidean_l2"]
    models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]
    try:
        df = DeepFace.find(img_path = r"./tmp/image.jpg", db_path = image_path, distance_metric = metrics[0], model_name = models[1])
    except ValueError as e:
        if str(e) == "Face could not be detected. Please confirm that the picture is a face photo or consider to set enforce_detection param to False.":
            return{"access": False, "code": 3001, "status": "face could not be detected", "name": None}


    # borrar imagenes de tmp folder
    for filename in os.listdir(IMAGEDIR):
        file_path = os.path.join(IMAGEDIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    try:
        if(not df.empty):
            print(df.head())
            if df['Facenet_cosine'][0] < 0.4:     
                return {"access": True, "code": 4001, "status": "found, face recognized", "name": x["nombre_completo"]}
            else:
                return {"access": False, "code": 3002, "status": "found, face not recognized", "name": None}
        else:
            return {"access": False, "code": 3002, "status": "no similar faces found", "name": None}
        
    except Exception as e:
        print(e)
        return{"access": False, "code": 8003, "status": e, "name": None}




    # finally:
    #     if db and type(db)==MongoClient:
    #         db.close()

def process_request_server(marcacion):
    print("processing punchin")
    utc = datetime.strptime(str(marcacion["DATETIME"]), '%Y-%m-%d %H:%M:%S')
    # de utc a local del servidor
    tz = timezone('America/Panama')
    local_date = utc.astimezone(tz)
    response = requests.post(
                'http://68.183.20.19/janustime/public/API/aplicacion/checkin2',
                json =  {
                        "ID_EMPRESA" : marcacion["ID_EMPRESA"],
                        "CODIGO_HUELLA" : marcacion["CODIGO_HUELLA"],
                        "DATETIME" : str(local_date),
                        "LAT" : marcacion["LAT"],
                        "LONG" : marcacion["LONG"]
                        }
    )
    print(response)
    print(response.json())
    if response.ok:
        print("processed code: {}, id: {}, date: {}, lat: {}, lon: {}".format(marcacion["ID_EMPRESA"], marcacion["CODIGO_HUELLA"], local_date, marcacion["LAT"], marcacion["LONG"]))
        db = get_db(marcacion["ID_EMPRESA"])
        marcaciones = db["marcaciones"]
        collaborator = { "employee_code": marcacion["CODIGO_HUELLA"]}
        marcacion = { "$push": { "marcaciones": {"latitude": marcacion["LAT"], "longitude": marcacion["LONG"], "date": marcacion["DATETIME"]} } }
        marcaciones.update_one(collaborator, marcacion)
    else:
        print("unable to process, adding to queue")
        db = client["marcaciones_pendientes"]
        marcaciones_pendientes = db["marcaciones"]
        marcaciones_pendientes.insert_one(marcacion)

def process_request_test(marcacion):
    print("processing punchin")
    print(marcacion)
    random_number = random.randint(0, 10)
    time.sleep(2)

    if random_number > 5:
        print("processed code:{}, id: {}, date: {}, lat: {}, lon: {}".format(marcacion["ID_EMPRESA"], marcacion["CODIGO_HUELLA"], marcacion["DATETIME"], marcacion["LAT"], marcacion["LONG"]))
        db = get_db(marcacion["ID_EMPRESA"])
        marcaciones = db["marcaciones"]
        collaborator = { "employee_code": marcacion["CODIGO_HUELLA"]}
        marcacion = { "$push": { "marcaciones": {"latitude": marcacion["LAT"], "longitude": marcacion["LONG"], "date": marcacion["DATETIME"]} } }
        marcaciones.update_one(collaborator, marcacion)
    else:
        print("unable to process, adding to queue")
        db = client["marcaciones_pendientes"]
        marcaciones_pendientes = db["marcaciones"]
        marcaciones_pendientes.insert_one(marcacion)


@app.on_event("startup")
@repeat_every(seconds = 60 * 10) # every ten minutes
def reprocess_punchin():
    try:
        marcaciones_pendientes_list = []

        db = client["marcaciones_pendientes"]
        marcaciones_pendientes = db["marcaciones"]
        
        marcaciones_pendientes_list = list(marcaciones_pendientes.find())
        print(marcaciones_pendientes_list)

        if not marcaciones_pendientes_list:
            print("no pending punchins")
        else:    
            print("processing pending punchins")
            for marcacion in marcaciones_pendientes_list:
                print(marcacion["_id"])
                _id = ObjectId(marcacion["_id"])
                marcaciones_pendientes.delete_one({"_id": _id})
                process_request_server(marcacion)
                
    except Exception as e:
        print(e)

@app.post('/marcacion')
async def recognize_person(background_tasks: BackgroundTasks, company_code: str = Form(...), employee_code: str = Form(...), file: UploadFile = File(...), latitude: str = Form(...), longitude: str = Form(...)):
    # creo que estas pruebas no se tienen que hacer porque en esta posicion ya se hizo el 
    # login, pero lo voy a dejar por ahora. 
    
    db = get_db(company_code)
    if not db:
        return{"code": 1001, "status": "compañia no existe"}
    
    print("recibiendo imagen")
    image_path = "./db/" + company_code + "/" + employee_code

    if not os.path.isdir(image_path):
        return{"code": 1002, "status": "colaborador no existe"}

    # guardar archivo como jpg en tmp folder
    with open(f"{IMAGEDIR}image.jpg", "wb") as image:
        shutil.copyfileobj(file.file, image)
    
    # encontrar imagenes parecidas en carpeta de imagenes
    metrics = ["cosine", "euclidean", "euclidean_l2"]
    models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

    try:
        df = DeepFace.find(img_path = r"./tmp/image.jpg", db_path = image_path, distance_metric = metrics[0], model_name = models[1])
    except ValueError as e:
        if str(e) == "Face could not be detected. Please confirm that the picture is a face photo or consider to set enforce_detection param to False.":
            return{"access": False, "code": 3001, "status": "face could not be detected", "name": None}

    # borrar imagenes de tmp folder
    for filename in os.listdir(IMAGEDIR):
        file_path = os.path.join(IMAGEDIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))



    if(not df.empty):
        print(df.head())
        if df['Facenet_cosine'][0] < 0.4:     
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(current_date)
            marcacion = {
                "ID_EMPRESA" : company_code,
                "CODIGO_HUELLA" : employee_code,
                "DATETIME" : str(current_date),
                "LAT" : latitude,
                "LONG" : longitude
            }

            background_tasks.add_task(process_request_server, marcacion)

            return {"access": True, "code": 4001, "status": "found, face recognized"}
        else:
            return {"access": False, "code": 3002, "status": "found, face not recognized"}
    else:
        return {"access": False, "code": 3002, "status": "no similar faces found"}



@app.post('/leer_marcaciones')
async def leer_marcaciones(clock_in_list_model: clock_in_list_model):

    db = get_db(clock_in_list_model.company_code)

    marcaciones = db["marcaciones"]
    collaborator = { "employee_code": clock_in_list_model.employee_code}
    x = marcaciones.find_one(collaborator)
    # por el momento lo mas facil es traer la lista completa a scope y luego hacer los procesos de reversa y slice.
    # esto en realidad es malo, porque en teoria solo hay que traer de mongodb los valores que queremos, pero esta resultando
    # dificil traducir del api de mongodb al api de pymongo. sobretodo con aggregate y project etc. asi que lo arreglare despues.

    # db.marcaciones.find({"employee_code": "2"}, {"marcaciones": { $slice: 20}, "_id": 0, "company_code": 0, "employee_code": 0}).pretty()

    lista_marcaciones = []

    for i in reversed(x["marcaciones"]):
        # transform mongodb date to utc
        print(str(i["date"]))
        utc = datetime.strptime(str(i["date"]), '%Y-%m-%d %H:%M:%S')
        # de utc a local del servidor
        tz = timezone('America/Panama')
        local_date = utc.astimezone(tz)

        print("latitude: " + str(i["latitude"]) + " longitude: " + str(i["longitude"]) + " date: " + str(local_date))
        item = {"latitude": str(i["latitude"]), "longitude": str(i["longitude"]), "date": str(local_date) }
        print(item)
        lista_marcaciones.append(item)
    print(len(lista_marcaciones))

    start = clock_in_list_model.start

    end = start + clock_in_list_model.amount if start + clock_in_list_model.amount < len(lista_marcaciones) else len(lista_marcaciones)

    return{"marcaciones": lista_marcaciones[start:end]}

@app.post("/validar_fotos")
async def validar_fotos(company_code: str = Form(...), employee_code: str = Form(...)):

    directory = "./db/" + company_code + "/" + employee_code
    
    if not os.path.isdir(directory):
        return{"code": 1005, "status": "directorio no existe"}

    img_path = os.path.join(directory, os.listdir(directory)[0])
    print(directory)
    print(img_path)
    try:
        print("should be making the df")
        metrics = ["cosine", "euclidean", "euclidean_l2"]
        models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

        df = DeepFace.find(img_path = img_path, db_path = directory, distance_metric = metrics[0], model_name = models[1])
        print(df)
    except ValueError as e:
        print(e)
        if str(e) == "Face could not be detected. Please confirm that the picture is a face photo or consider to set enforce_detection param to False.":
            # first delete all files.
            print("face not detected")
            shutil.rmtree(directory)

            return{"created": False, "code": 3001, "status": "face could not be detected"}
    
    return{"created": True, "code": 4002, "status": "representations created successfully"}


# iniciar servidor
if __name__ == '__main__':
    print("running on port 8000")
    uvicorn.run(app, host = '0.0.0.0', port = 8000)

