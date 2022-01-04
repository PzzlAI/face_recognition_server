import uvicorn
from fastapi import FastAPI, File, UploadFile, Body, Form
from deepface import DeepFace
import os
import shutil
from starlette.testclient import TestClient
from pymongo import MongoClient
import datetime
from bson.json_util import dumps

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

    print("recibiendo imagen")
    image_path = "./db/" + company_code + "/" + employee_code

    # guardar archivo como jpg en tmp folder
    with open(f"{IMAGEDIR}image.jpg", "wb") as image:
        shutil.copyfileobj(file.file, image)
    
    # encontrar imagenes parecidas en carpeta de imagenes
    metrics = ["cosine", "euclidean", "euclidean_l2"]
    models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

    df = DeepFace.find(img_path = r"./tmp/image.jpg", db_path = image_path, distance_metric = metrics[0], model_name = models[1], enforce_detection = False)

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
                db = get_db(company_code)

                collection = db["colaboradores"]

                collaborator = { "employee_code": employee_code}
                x = collection.find_one(collaborator)


                return {"access": True, "status": "found, face recognized", "name": x["nombre_completo"]}
            else:
                return {"access": False, "status": "found, face not recognized", "name": None}
        else:
            return {"access": False, "status": "no similar faces found", "name": None}
        
    except Exception as e:
        return(e)



    # finally:
    #     if db and type(db)==MongoClient:
    #         db.close()

@app.post('/marcacion')
async def recognize_person(company_code: str = Form(...), employee_code: str = Form(...), file: UploadFile = File(...), latitude: str = Form(...), longitude: str = Form(...)):
    print("recibiendo imagen")
    image_path = "./db/" + company_code + "/" + employee_code

    # guardar archivo como jpg en tmp folder
    with open(f"{IMAGEDIR}image.jpg", "wb") as image:
        shutil.copyfileobj(file.file, image)
    
    # encontrar imagenes parecidas en carpeta de imagenes
    metrics = ["cosine", "euclidean", "euclidean_l2"]
    models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

    df = DeepFace.find(img_path = r"./tmp/image.jpg", db_path = image_path, distance_metric = metrics[0], model_name = models[1], enforce_detection = False)

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
                db = get_db(company_code)

                marcaciones = db["marcaciones"]

                collaborator = { "employee_code": employee_code}
                current_date = datetime.datetime.now()
                marcacion = { "$push": { "marcaciones": {"latitude": latitude, "longitude": longitude, "date": current_date} } }
                marcaciones.update_one(collaborator, marcacion)

                return {"access": True, "status": "found, face recognized"}
            else:
                return {"access": False, "status": "found, face not recognized"}
        else:
            return {"access": False, "status": "no similar faces found"}
        
    except Exception as e:
        return(e)


@app.post('/leer_marcaciones')
async def leer_marcaciones(company_code, employee_code):

    db = get_db(company_code)
    marcaciones = db["marcaciones"]
    collaborator = { "employee_code": employee_code}
    x = marcaciones.find_one(collaborator)

    lista_marcaciones = []

    for i in x["marcaciones"]:
        print(i)
        print("latitude: " + str(i["latitude"]) + " longitude: " + str(i["longitude"]) + " date: " + str(i["date"]))
        item = {"latitude": str(i["latitude"]), "longitude": str(i["longitude"]), "date": str(i["date"]) }
        lista_marcaciones.append(item)


    return{"marcaciones": lista_marcaciones}


# iniciar servidor
if __name__ == '__main__':
    print("running on port 8000")
    uvicorn.run(app, host = '0.0.0.0', port = 8000)
