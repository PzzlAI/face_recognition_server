import uvicorn
from fastapi import FastAPI, File, UploadFile, Body, Form
from typing import Optional
from deepface import DeepFace
import os
import shutil
from starlette.testclient import TestClient
from pymongo import MongoClient
from datetime import datetime
from pytz import timezone
from bson.json_util import dumps
from pydantic import BaseModel

class clock_in_list_model(BaseModel):
    company_code: str
    employee_code: str
    start: int
    amount: Optional[int] = 20

app = FastAPI()


IMAGEDIR = "./tmp/"

def get_db(company_code):
    client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")
                        
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
        return "company doesnt exist"

    
    
    print("recibiendo imagen")
    image_path = "./db/" + company_code + "/" + employee_code

    if not os.path.isdir(image_path):
        return "employee doesnt exist"

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
            return{"access": False, "code": 4, "status": "face could not be detected", "name": None}


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

                collection = db["colaboradores"]

                collaborator = { "employee_code": employee_code}
                x = collection.find_one(collaborator)

                # if its not a colaborator then it must be an administrator. 
                if not x:
                    collection = db["administradores"]
                    x = collection.find_one(collaborator)


                return {"access": True, "code": 1, "status": "found, face recognized", "name": x["nombre_completo"]}
            else:
                return {"access": False, "code": 2, "status": "found, face not recognized", "name": None}
        else:
            return {"access": False, "code": 3, "status": "no similar faces found", "name": None}
        
    except Exception as e:
        return(e)



    # finally:
    #     if db and type(db)==MongoClient:
    #         db.close()

@app.post('/marcacion')
async def recognize_person(company_code: str = Form(...), employee_code: str = Form(...), file: UploadFile = File(...), latitude: str = Form(...), longitude: str = Form(...)):
    # creo que estas pruebas no se tienen que hacer porque en esta posicion ya se hizo el 
    # login, pero lo voy a dejar por ahora. 
    
    db = get_db(company_code)
    if not db:
        return "company doesnt exist"
    
    print("recibiendo imagen")
    image_path = "./db/" + company_code + "/" + employee_code

    if not os.path.isdir(image_path):
        return "employee doesnt exist"

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
            return{"access": False, "code": 4, "status": "face could not be detected", "name": None}

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

                marcaciones = db["marcaciones"]

                collaborator = { "employee_code": employee_code}

                tz = timezone('America/Panama')
                current_date = datetime.now(tz)
                marcacion = { "$push": { "marcaciones": {"latitude": latitude, "longitude": longitude, "date": current_date} } }
                marcaciones.update_one(collaborator, marcacion)

                return {"access": True, "code": 1, "status": "found, face recognized"}
            else:
                return {"access": False, "code": 2, "status": "found, face not recognized"}
        else:
            return {"access": False, "code": 3, "status": "no similar faces found"}
        
    except Exception as e:
        return(e)


@app.post('/leer_marcaciones')
async def leer_marcaciones(clock_in_list_model: clock_in_list_model):

    db = get_db(clock_in_list_model.company_code)

    marcaciones = db["marcaciones"]
    collaborator = { "employee_code": clock_in_list_model.employee_code}
    x = marcaciones.find_one(collaborator)
    # por el momento lo mas facil es traer la lista completa a scope y luego hacer los procesos de reversa y slice.
    # esto en realidad es malo, porque en teoria solo hay que traer de mongodb los valores que queremos, pero esta resultando
    # dificil traducir del api de mongodb al api de pymongo. sobretodo con aggregate y project etc. asi que lo arreglare despues.

    lista_marcaciones = []

    for i in reversed(x["marcaciones"]):
        print("latitude: " + str(i["latitude"]) + " longitude: " + str(i["longitude"]) + " date: " + str(i["date"]))
        item = {"latitude": str(i["latitude"]), "longitude": str(i["longitude"]), "date": str(i["date"]) }
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
        return{"code": 5, "status": "directory doesnt exist"}

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

            return{"created": False, "code": 4, "status": "face could not be detected"}
    
    return{"created": True, "code": 6, "status": "representations created successfully"}


# iniciar servidor
if __name__ == '__main__':
    print("running on port 8000")
    uvicorn.run(app, host = '0.0.0.0', port = 8000)
