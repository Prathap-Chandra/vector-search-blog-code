# Vector Search
A brief description of the project.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

## Requirements

To run this project, you need to have the following installed on your machine:

- Docker: Install Docker by following the instructions provided on the [official Docker documentation](https://docs.docker.com/get-docker/).
- Python: Install Python by following the instructions on the [official Python website](https://www.python.org/downloads/).
- Node.js: Install Node.js by following the instructions on the [official Node.js website](https://nodejs.org/en/download/).

## Installation

**Note:** Currently, due to some issues with the backend, I couldn't dockerize the project. Therefore, to run the project, please follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/Prathap-Chandra/vector-search-blog-code
    ```

2. Start the React app:
    - Navigate to the frontend folder:
        ```bash
        cd frontend
        ```
    - Run the React app using Vite on port 5173:
        ```bash
        npm run dev
        ```

3. Start the Python Server:
    - Navigate to the backend folder:
        ```bash
        cd backend
        ```
    - Create and activate a virtual environment:
        ```bash
        # For macOS (and Linux/Ubuntu)
        python3 -m venv venv
        source venv/bin/activate

        # For Windows
        python -m venv venv
        .\venv\Scripts\activate
        ```
    - Run the Python app using Flask on port 5000.

4. Start the Qdrant - Vector Database:
    - Pull the Qdrant Docker image:
        ```bash
        docker pull qdrant/qdrant
        ```
    - Run the Qdrant Docker image with the specified port mappings and volume mounts. Replace `$(pwd)` with your host path, such as `/home/prathap/Desktop/Codebase/Personal/docker-volumes/qdrant_storage`:
        ```bash
        docker run -d --name vector-database -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
        ```
    - That's it. Your database should be up and running; you can confirm this by visiting http://localhost:6333/dashboard in your browser.  

- Please note that this is a temporary solution, and eventually, the project will be dockerized. Once dockerized, you will only need to run the compose file to start the servers.

## Usage

Once your frontend, backend, and database are up and running, you should run a script to seed the data. To do that:

- Navigate to the backend folder:
    ```bash
    cd backend
    ```
- You'll find an `app` folder inside which there is a `seed_data` folder. Inside the `seed_data` folder, you can find images and pdfs folders. Copy all the images and pdfs to their respective folders. Once copied, run the below command to extract the embeddings of images and pdfs and store them in Qdrant:
    ```bash
    python3 script.py
    ```
