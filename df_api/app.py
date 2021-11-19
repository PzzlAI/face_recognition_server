import uvicorn
from fastapi import FastAPI, File, UploadFile, Body
from deepface import DeepFace
import os
import shutil
from starlette.testclient import TestClient

app = FastAPI()


IMAGEDIR = "./tmp/"

@app.post('/verify')
async def recognize_person(company_code: str, employee_code: str, image: UploadFile = File(...)):

    print("recibiendo imagen")
    image_path = "./db/" + company_code + "/" + employee_code

    # guardar archivo como jpg en tmp folder
    with open(f"{IMAGEDIR}image.jpg", "wb") as f:
        f.write(image.file)
    
    # encontrar imagenes parecidas en carpeta de imagenes
    metrics = ["cosine", "euclidean", "euclidean_l2"]
    models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

    df = DeepFace.find(img_path = r"./tmp/image.jpg", db_path = image_path, distance_metric = metrics[0], model_name = models[1])

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


    # respuesta del servidor
    if(not df.empty):
        print(df.head())

    try:
        if(not df.empty):
            print(df.head())
            if df['VGG-Face_cosine'][0] < 0.4:
                location = df['identity'][0].replace('./images\\', '').split('/')
                name = location[0]
                print("persona encontrada en base de datos, su nombre es %s" % (name))
                return {"status" : name}
            else:
                print("persona no encontrada en base de datos")
                return {"status" : "person not found in database!"}
        else:
            print("persona no encontrada en base de datos")
            return {"status" : "person not found in database!"}
        
    except:
        print("error de inferencia")

# iniciar servidor
if __name__ == '__main__':
    print("running on port 8000")
    uvicorn.run(app, host = '0.0.0.0', port = 8000)