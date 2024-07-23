# Raw Food Price Prediction Web Application

A web application that predicts the prices of raw food items using ANN Time Series Forecasting, Selenium, Django, React and PostgreSQL.

## Consists of the following main features:

- Price Prediction
- Items Comparison
- Newsletter Subscription (and Unsubscribe)
- Shopping List
- Nutritional Information

![Screenshot 2024-04-23 230032](https://github.com/Shenzzz21/Raw-Food-Price-Prediction-Web-Application/assets/141328474/ac3301db-b144-48cf-8d31-139f1daabb3e)

![Screenshot 2024-04-24 002339](https://github.com/Shenzzz21/Raw-Food-Price-Prediction-Web-Application/assets/141328474/ccee2b09-c02e-415c-aac2-61ca994fa743)

![Screenshot 2024-04-19 215550](https://github.com/Shenzzz21/Raw-Food-Price-Prediction-Web-Application/assets/141328474/593e94d0-ff8b-4300-afc6-6f10f09acb6e)

![Screenshot 2024-04-19 205243](https://github.com/Shenzzz21/Raw-Food-Price-Prediction-Web-Application/assets/141328474/ffb02108-2d87-4157-aad7-52157b7fff1f)

![Screenshot 2024-04-19 230250](https://github.com/Shenzzz21/Raw-Food-Price-Prediction-Web-Application/assets/141328474/18959a9e-a8e9-4947-ab37-a828999a5189)

## Getting started for Windows

- Download Python ( https://www.python.org/downloads/ )
- Download Node.js ( https://nodejs.org/en/download )
- Download PostgreSQL ( https://www.postgresql.org/download/ )
- Download Visual Studio Code ( https://code.visualstudio.com/download )
- Download 7Zip ( https://www.7-zip.org/download.html )

## Setting up Project

- Download the Project File and extract it using 7Zip.
- Make sure the main folder is "AgroCost" and sub folders are "backend" and "frontend".
- Do not rename any other existing folder except main folder to "AgroCost" if required.

## Setting up database: PostgreSQL

- Open pgAdmin (PostgreSQL).
- Set up your database by entering credentials.
- Create new database named "agrocost_db".

## Installing Virtual Environment

- Open Command Prompt as administrator.
- Type "pip install virtualenv".

## Opening Project in Visual Studio Code

- Open Visual Studio.
- Go to the Top-Left of Visual Code and click on "File".
- From the dropdown, click on "Open Folder".
- New window will pop up and select the project folder "AgroCost".
- The project will load into Visual studio Code.

## Setting up Virtual Environment

Opening new Terminals for frontend and backend:
- In the VS Code, click on "Terminal" in the same bar as "File".
- Dropdown will apear and click on New Terminal.

To create new virtual Environment:
- Type "virtualenv env" in the terminal to create new virtual environment named "env".
- A new env is created in the project folder.

## Setting up backend

Change the directory to backend and download the required packages:
- Type "env\Scripts\activate" to activate the virtual environment for backend.
- Type "cd backend" in the terminal to change directory to backend.
- Type "pip install -r requirements.txt" to install all the packages listed in the requirements.txt file.

To configure the database:
- Navigate to settings.py file in the backend folder.
- Set the user and password, along with the name of the database.

To make migration:
- Type "python manage.py makemigrations"

To migrate to database:
- Type "python manage.py migrate"

To run backend server:
- Type "python manage.py runserver"

To create superuser/admin:
- Type "python manage.py createsuperuser" and fill all the required sections to create superuser

## Setting up frontend

Change the directory to frontend and download the required packages:
- Open up a new terminal.
- Type "env\Scripts\activate" to activate the virtual environment for frontend.
- Type "cd frontend" to change directory to frontend.
- Type "npm install" to install all the dependencies(packages) listed in the package.json file.
- After successfully installing all the packages, type "npm start" to run the frontend server.

Note: If you encounter error while installing the packages, type "npm install --force" to force and re-install all packages.
