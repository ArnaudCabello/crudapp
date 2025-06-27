# Flask CRUD App with MySQL and Docker
This is a full-stack Flask CRUD application with MySQL database integration, RESTful API endpoints, and Docker support.

## Features
- Create, Read, Update, Delete (CRUD) users
- REST API + HTML interface
- MySQL database (via Docker)
- Integration tests using `pytest`

  ## Requirements
- Docker & Docker Compose
- Python 3.8+
- pip

  ## Running the App
1. Clone the repository: git clone https://github.com/ArnaudCabello/crudapp.git
   cd crudapp

3. In app.py line 9 insert an OPENAI API key to use the agentic AI 
   
4. Run docker-compose up --build

5. Open localhost:5000

6. Run docker-compose run --rm app pytest test_app.py for integration tests


   
