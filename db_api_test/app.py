from typing import Optional
from fastapi import FastAPI, File, UploadFile,Form
import pymongo
from pymongo import MongoClient
import uvicorn
from pydantic import BaseModel
import shutil
import os
from bson.json_util import dumps
import datetime

app = FastAPI()
# todo: posiblemente refactorizar los procesos de remove y restore, pueden ser juntados en una sola ruta respectivamente.
#       solo que habra que tomar en cuenta la autenticacion en el proceso de remove/restore de admins, ya que solo el super admin
#       debe ser capaz de hacerlo.


class Credentials(BaseModel):
    company_code: str = None
    employee_code: str = None


# todo: hay que setear para que el omega administrador sea el que cree las bases de datos, y hay que definir como va a ser ese proceso.
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

# por ahora se va a utilizar esta funcion para hacer bases de datos de prueba, pero se va a tener que refactorizar para que se haga a traves del omega administrador.
def create_db(company_code):
    client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")
    print(company_code)
    db = client[company_code]
    return db



@app.get('/')
def ping_server():
    return "Face database api running"

# esta ruta solo se va a usar para pruebas, posteriormente se va a formalizar un proceso de creacion de base de datos utilizando el concepto del omega administrador.
# por ahora este proceso tambien requiere la creacion del super administrador, pero esto es sujeto a cambio dependiendo de las decisiones de diseño futuras.
@app.post('/create_company', status_code = 201)
async def create_company(company_code: str, employee_code: str, username: str, password: str):
    db=""
    try:
        db = get_db(company_code)
        if not db:
            os.mkdir("./db/" + company_code)
            db = create_db(company_code)
            collection = db["super_administrador"]
            current_date = datetime.datetime.now()
            super_admin = {"company_code": company_code, "employee_code": employee_code, "username": username, "password": password,"created": current_date, "updated": current_date}
            collection.insert_one(super_admin)
            return ("company " + company_code + " created succesfully with " + employee_code+ " as administrator")


    except Exception as e:
        print(e)
        return "unable to create database for company"
    finally:
        if type(db)==MongoClient:
            db.close()


# determinar si este proceso se hace con imagen inicial o sin image, por ahora esta sin imagen.
@app.post("/create", status_code = 201)
async def create(company_code: str, employee_code: str):
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"
        
        collection = db["colaboradores"]
        directory = "./db/" + company_code + "/" + employee_code
        

        os.mkdir(directory)
        # este es el codigo para crear imagen, por ahora solo se crea el espacio, no se pone imagen.
        # image_path = directory + "/" + employee_code + "_" + str(len(os.listdir(directory))) + ".jpg"
        # with open(image_path,'wb') as image:
        #     shutil.copyfileobj(file.file, image)
        current_date = datetime.datetime.now()
        colaborador = {"company_code": company_code, "employee_code": employee_code, "image_paths": [], "created": current_date, "updated": current_date}
        print(colaborador)
        collection.insert_one(colaborador)
        x = collection.find()
        return(dumps(x))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# todo: refactorizar para aclarar/robustizar el proceso de autenticacion de administrador, ya sea con hashing o viendo si se usa la misma imagen de la persona, sin embargo, esto tendria implicaciones en
# la estructura general del prototipo. 
# tomar en cuenta que se hashea antes de mandar al servidor, osea en el app/browser.
@app.post("/create_admin", status_code = 201)
async def create_admin(company_code: str, employee_code: str, username: str, password: str):
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"
        
        collection = db["administradores"]
        
        current_date = datetime.datetime.now()
        admin = {"company_code": company_code, "employee_code": employee_code, "username": username, "password": password,"created": current_date, "updated": current_date}
        print(admin)
        collection.insert_one(admin)
        x = collection.find()
        return(dumps(x))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# todo: ver si se necesita el update de admin, ya sea por updatear contraseña u otra cosa.

# update funciona para meter imagenes al espacio del colaborador. En el caso de que no exista se crea, pero esto es sujeto a cambio.
@app.post("/update",  status_code=201)
async def update(company_code: str, employee_code: str, file: UploadFile = File(...) ):
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"

        collection = db["colaboradores"]
        directory = "./db/" + company_code + "/" + employee_code
        

        if os.path.isdir(directory):
            image_path = directory + "/" + employee_code + "_" + str(len(os.listdir(directory))) + ".jpg"
            with open(image_path,'wb') as image:
                shutil.copyfileobj(file.file, image)

            employee = { "employee_code": employee_code }
            new_path = { "$push": { "image_paths": image_path }, "$set": {"updated": datetime.datetime.now()} }

            collection.update_one(employee, new_path)
            x = collection.find()
            return(dumps(x))

        # por ahora se va a crear en caso de que no exista, pero eso puede cambiar.
        else:
            os.mkdir(directory)
            image_path = directory + "/" + employee_code + "_" + str(len(os.listdir(directory))) + ".jpg"
            with open(image_path,'wb') as image:
                shutil.copyfileobj(file.file, image)

            current_date = datetime.datetime.now()
            colaborador = {"company_code": company_code, "employee_code": employee_code, "image_paths": [image_path], "created": current_date, "updated": current_date}

            print(colaborador)
            collection.insert_one(colaborador)
            # se retorna toda la base de datos, esto se va a borrar en algun punto, solo esta para desarrollo.
            x = collection.find()
            return(dumps(x))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# retornar colaborador, por el momento esta escrito para utilizar durante desarrollo, pero se refactorizara para uso en produccion.
@app.post("/read",  status_code=201)
async def read(company_code: str, employee_code: str):
    db=""
    try:
        db = get_db(company_code)
        if not db:
            return "company doesnt exist"
        
        collection = db["colaboradores"]

        employee = { "employee_code": employee_code }
        x = collection.find_one(employee)
        print(x)
        return(dumps(x))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()


# retornar lista completa de colaboradores, por el momento esta escrito para ser utilizado durante desarrollo, pero se refactorizara para uso en produccion.
@app.get("/read_all",  status_code=201)
async def read(company_code: str):
    db=""
    try:
        db = get_db(company_code)
        if not db:
            return "company doesnt exist"

        colaboradores = db["colaboradores"].find()
        administradores = db["administradores"].find()
        super_administrador = db["super_administrador"].find()
        colaboradores_borrados = db["colaboradores_borrados"].find()
        administradores_borrados = db["administradores_borrados"].find()

        print(colaboradores)

        full_db = {"colaboradores": colaboradores, "administradores": administradores, "colaboradores_borrados": colaboradores_borrados, "administradores_borrados": administradores_borrados, "super_administrador": super_administrador}

        return(dumps(full_db))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# mover colaboradores a coleccion y directorio separado, aka, papelera de reciclaje.
@app.post("/remove", status_code=201)
async def remove(company_code: str, employee_code: str):
    # revisar este codigo para asegurarme de que no se desincronizen los volumenes en el caso de que un proceso funcione y el otro se trabe.
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code }
        
        # copiar datos de empleado
        employee_document = collection.find_one(employee)
        # insertar en nueva coleccion
        deleted_collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.datetime.now()} }
        deleted_collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        collection.delete_one(employee)

        try:
            # mover imagenes a nueva carpeta asumiendo que el directorio nuevo existe. ./db/(company_code)_deleted/(employee_code)
            shutil.move("./db/"+ company_code + "/" + employee_code, "./db/"+ company_code + "_deleted/" + employee_code)
            return "se removio colaborador exitosamente"
        except OSError as e:
            return("Error: %s - %s." % (e.filename, e.strerror))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# mover administrador a coleccion separada.
# todo: refactorizar para usar la misma ruta de remove para ambos administradores y colaboradores, ya sea con parametros de rutas. /remove_{variable}
@app.post("/remove_admin", status_code=201)
async def remove_admin(company_code: str, employee_code: str):
    # revisar este codigo para asegurarme de que no se desincronizen los volumenes en el caso de que un proceso funcione y el otro se trabe.
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"

        collection = db["administradores"]
        deleted_collection = db["administradores_borrados"]

        employee = { "employee_code": employee_code }
        
        # copiar datos de empleado
        employee_document = collection.find_one(employee)
        # insertar en nueva coleccion
        deleted_collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.datetime.now()} }
        deleted_collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        collection.delete_one(employee)
        return("se removio administrador existosamente")
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# eliminar colaborador completamente.
@app.post("/delete", status_code=201)
async def delete(company_code: str, employee_code: str):
    # revisar este codigo para asegurarme de que no se desincronizen los volumenes en el caso de que un proceso funcione y el otro se trabe.
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"

        collection = db["colaboradores"]

        employee = { "employee_code": employee_code }
        
        collection.delete_one(employee)

        try:
            shutil.rmtree("./db/"+ company_code + "/" + employee_code)
            return "se borros exitosamente"
        except OSError as e:
            return("Error: %s - %s." % (e.filename, e.strerror))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# eliminar administrador completamente.
@app.post("/delete_admin", status_code=201)
async def delete_admin(company_code: str, employee_code: str):
    # revisar este codigo para asegurarme de que no se desincronizen los volumenes en el caso de que un proceso funcione y el otro se trabe.
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"

        collection = db["administrador"]

        employee = { "employee_code": employee_code }
        
        collection.delete_one(employee)
        return("se borro administrador exitosamente")
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()


# todo: hacer ruta para restore, en la que restauramos un colaborador que fue borrado. y posiblemente usar una sola ruta para administradores tambien.
@app.post("/restore", status_code = 201)
async def restore(company_code: str, employee_code: str):
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code }
        
        # copiar datos de empleado
        employee_document = deleted_collection.find_one(employee)
        # insertar en nueva coleccion
        collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.datetime.now()} }
        collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        deleted_collection.delete_one(employee)

        try:
            # mover imagenes a nueva carpeta asumiendo que el directorio nuevo existe. ./db/(company_code)_deleted/(employee_code)
            shutil.move("./db/"+ company_code + "_deleted/" + employee_code, "./db/"+ company_code + "/" + employee_code)

        except OSError as e:
            return("Error: %s - %s." % (e.filename, e.strerror))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

@app.post("/restore_admin", status_code = 201)
async def restore_admin(company_code: str, employee_code: str):
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return "company doesnt exist"

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code }
        
        # copiar datos de empleado
        employee_document = deleted_collection.find_one(employee)
        # insertar en nueva coleccion
        collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.datetime.now()} }
        collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        deleted_collection.delete_one(employee)

    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()


# ---------------------------------------------------------------------#
# solo para propositos de prueba
@app.get("/delete_databases", status_code=201)
async def delete_all():
    db=""
    try:
        client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")

        dbnames = client.list_database_names()

        if dbnames:
            for database in dbnames:
                if not (database == "admin" or database == "local" or database == "config"):
                    client.drop_database(database)

        for f in os.listdir("./db/"):
            shutil.rmtree("./db/" + f)
        return "se borraron exitosamente"
    except OSError as e:
        return("Error: %s - %s." % (e.filename, e.strerror))
    finally:
        if type(db)==MongoClient:
            db.close()

@app.get("/list_databases")
async def list_databases():
    db=""
    try:
        client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")

        dbnames = client.list_database_names()
        print(dbnames)
        return(dbnames)
    except Exception as e:
        return(e)
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

if __name__ == '__main__':
    print("running on port 5000")
    uvicorn.run(app, host = '0.0.0.0', port = 5000)