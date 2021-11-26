import requests
# import cv2
import names
import random
import os

counter = 0

def generate_mock_companies(endpoint: str, company_count: int):

    global counter
    for i in range(company_count):
        data = {"company_code": i, 
                "employee_code": counter, 
                "username": "admin" + str(counter), 
                "password": "admin" + str(counter) + "pass", 
                "nombre_completo": names.get_full_name()
                }
        counter += 1
        response = requests.post(
            endpoint,
            json = data
        )

        print(response.json())

def generate_mock_administrators(endpoint: str, amount: int, company_count: int):
    global counter
    for i in range(company_count):
        for w in range(counter, counter + amount):
            data = {"company_code": i, 
                    "employee_code": w, 
                    "username": "admin" + str(w), 
                    "password": "admin" + str(w) + "pass", 
                    "nombre_completo": names.get_full_name()
                    }
            counter += 1
            response = requests.post(
                endpoint,
                json = data
            )

            print(response.json())

def generate_mock_collaborators(endpoint: str, amount: int, company_count: int):

    global counter
    people_folder = r'C:/Users/ratatosck/Desktop/pythonScripts/Deepface_benchmark/lfw_test_dataset/'

    

    for i in range(company_count):
        for w in range(amount):
            random_names = random.sample(range(len(os.listdir(people_folder))), 5)
            person = os.listdir(people_folder)[random_names[w]]

            data = {"company_code": i, 
                    "employee_code": counter, 
                    "nombre_completo": person.replace("_", " ")
                    }

            image_folder = os.listdir(people_folder + person)
            files = []
            for image in image_folder:
                image_path = people_folder + person + '/' + image
                files.append(('files', open(image_path, 'rb')))

            counter += 1

            response = requests.post(
                endpoint,
                files=files,
                data= data
            )

            print(response.json())

if __name__ == "__main__":
    company_count = 3
    collaborator_count = 3
    admin_count = 3
    ip = '198.199.82.209'
    # ip = 'localhost'
    generate_mock_companies(endpoint = 'http://' + ip +':5000/create_company', company_count = company_count)
    generate_mock_collaborators(endpoint = 'http://' + ip +':5000/create_collaborator', amount = collaborator_count, company_count = company_count)
    generate_mock_administrators(endpoint = 'http://' + ip +':5000/create_admin', amount = admin_count, company_count = company_count)
