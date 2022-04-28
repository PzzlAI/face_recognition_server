nuevo repositorio para projectos de puzzleai

```bash
Folder Structure
C:.
|   .gitattributes
|   docker-compose.dev.yml
|   docker-compose.yml
|   readme.txt
|   structure.txt
|   
+---admin_ui
|   |   .dockerignore
|   |   .gitignore
|   |   app.js
|   |   Dockerfile
|   |   package-lock.json
|   |   package.json
|   |   
|   \---views
|       |   login.html
|       |   
|       +---css
|       |       style.css
|       |       
|       +---img
|       |       logo.png
|       |       
|       \---js
|               validation.js
|               
+---db_api
|   |   .dockerignore
|   |   .gitignore
|   |   app.py
|   |   Dockerfile
|   |   implementation_details.txt
|   |   readme.txt
|   |   requirements.txt
|   |   
|   \---utils
|           auxiliary_functions.py
|           models.py
|           __init__.py
|           
+---db_api_test
|       .dockerignore
|       .gitignore
|       app.py
|       docker-compose.yml
|       Dockerfile
|       implementation_details.txt
|       requirements.txt
|       
+---df_api
|   |   .dockerignore
|   |   .gitignore
|   |   app.py
|   |   Dockerfile
|   |   readme.txt
|   |   requirements.txt
|   |   
|   \---utils
|       |   auxiliary_functions.py
|       |   __init__.py
|       |   
|       \---__pycache__
|               auxiliary_functions.cpython-38.pyc
|               __init__.cpython-38.pyc
|               
\---tests
        .gitignore
        endpoint_tests.ipynb
        generate_mock_database.py
        internal_tests.py
```
