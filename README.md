Prerequisites
Docker and Docker Compose

Installation & Running
Clone the repository:

Bash

git clone git@github.com:YOUR_USERNAME/lemon-order-api.git
cd lemon-order-api
Run with Docker Compose:

Bash

docker-compose up --build
Access the API:

Interactive Docs (Swagger): http://localhost:8000/docs

API Endpoint: POST http://localhost:8000/orders

🧪 Testing

Bash

# Run tests inside the container
docker-compose exec api pytest
