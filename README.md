# A/B testing Powered by Thompson Sampling


## Description

This project is designed to create a Dockerized setup that includes a PostgreSQL database, pgAdmin for database administration, a model container, and an API container. It simplifies the development, deployment, and management of these elements through a unified Docker Compose setup.

## Prerequisites

Before getting started, ensure you have the following prerequisites installed:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. Clone the repository:
   
   git clone <repository_url>
   
2. Navigate to the project directory:
   
   cd <project_directory>
   

3. Build and start the Docker containers(It can take up to 5 minutes to build the containers):
   
    
```bash
docker-compose build
docker-compose up
```

   

## Usage

- Access pgAdmin for PostgreSQL management: [http://localhost:5050]
- Access the API: [http://0.0.0.0:8000/docs]   
