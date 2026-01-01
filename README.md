# Django App Template 
This Django template includes:
- JET admin interface
- Python slugify package
- Django Tailwind (_node.js and npm required_)
- Python dotenv package
- Basic templating structure
- Basic account functionality (login and logout)

## Instalation
1. Create virtual environment:
    ```
    python -m venv .venv
    ```
2. Activate the environment:
	- Linux/macOS: 
	``` 
	source .venv/bin/activate
	```
	- Windows:
	 ```
	 .venv\Scripts\activate
	 ```
3. Install packages:
	```
	pip install -r requirements.txt
	```
4. Install tailwind dependencies:
	```
	python manage.py tailwind install
	```
5. Migrate:
	```
	python manage.py migrate
	```
	
## Dotenv
In order to use the `dotenv` package, you will need to create a _.env_ file in the root of your project. You can change the location of the file by modifying this line in the `settings.py` file:
```python
# Load environment variables from .env
load_dotenv(os.path.join(BASE_DIR, '.env'))
```
By default, the project settings gets `DEBUG` and `SECRET_KEY` values from _.env_ file.

## Development Server
To run the development server, just run these two commands in separate terminals:
```
python manage.py tailwind start
```
and

```
python manage.py runserver
```

### Running in Docker
To run the development server in Docker, use the following command:
```
docker-compose -f docker/dev/docker-compose.yaml up
```
This will run 3 services:
- MySQL database
- Tailwind compiler
- Django web server
