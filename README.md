# Real-time Webchat

This is a simple multi-user, single-room realtime webchat application built using **aiohttp**, **Redis**, and Docker. It features a basic chat room where multiple users can connect and chat in real time. The project demonstrates the use of WebSockets for real-time communication, Redis for pub/sub messaging, and Docker for containerization.

## Project Structure

```
.
├── docker/
│   └── Dockerfile
├── webchat/
│   ├── main.py
│   ├── views.py
│   ├── chat_service.py
│   └── template/
│       └── index.html
├── docker-compose.yml
├── requirements.txt
└── README.md

```

## Features

- Real-time chat functionality using WebSockets.
- User sessions are uniquely identified using randomly generated user names (from the `faker` library).
- Redis is used for pub/sub messaging, ensuring all users connected to the chat room receive messages.

## Prerequisites

- Docker and Docker Compose installed on your machine.

## Setup and Running the Application

1. Clone this repository to your local machine:
    
    ```
    git clone https://github.com/chaews0327/webchat.git
    cd webchat
    ```
    
2. Build and start the application with Docker Compose:
    
    ```
    docker-compose up --build
    ```
    
3. After the containers are up and running, open your browser and navigate to:
    
    ```
    http://localhost:8080
    ```
    
4. Click "Connect" to join the chat and start messaging with other users.

## References

This project refers to:
- [Chat tutorial using aiohttp](https://github.com/aio-libs/aiohttp-demos/tree/master/demos/chat)
- [aiohttp official document](https://docs.aiohttp.org/en/stable/index.html)
- [redis official document](https://redis-py.readthedocs.io/en/stable/)