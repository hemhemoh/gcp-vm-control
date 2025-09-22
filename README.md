# Google Cloud Server Manager

**A production-ready full-stack cloud infrastructure management platform built with FastAPI, Streamlit, and Google Cloud Platform APIs.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue.svg)](https://docker.com)
[![GCP](https://img.shields.io/badge/Google_Cloud-Integrated-orange.svg)](https://cloud.google.com)

## 🎯 Project Overview

An enterprise-grade web application that provides centralized management of Google Cloud Compute Engine instances with real-time monitoring, automated notifications, and comprehensive audit logging. Features a modern REST API backend with an intuitive web interface for non-technical stakeholders.

**Live Demo**: https://app.hemhemoh.com/

## 🛠️ Technology Stack

### Backend Architecture
- **FastAPI** - High-performance async API framework with automatic OpenAPI documentation
- **SQLModel** - Type-safe database ORM with Pydantic integration
- **SQLite** - Embedded database with ACID compliance
- **Google Cloud SDK** - Native GCP API integration for compute resource management
- **Background Tasks** - Asynchronous operation monitoring and retry mechanisms
- **SMTP Integration** - Automated email notification system

### Frontend & DevOps
- **Streamlit** - Interactive web interface with real-time updates
- **Docker & Docker Compose** - Containerized microservices architecture
- **RESTful API Design** - Clean separation of concerns with proper HTTP semantics
- **Session Management** - Secure credential handling without persistent storage

### Cloud & Infrastructure
- **Google Cloud Platform** - Compute Engine API integration
- **Service Account Authentication** - Secure GCP resource access
- **Multi-zone Support** - Cross-regional instance management
- **Error Handling** - Comprehensive exception management with user-friendly messages

## ⚡ Key Features

- **🚀 Instance Lifecycle Management** - Start, stop, and monitor GCP instances across multiple zones
- **📊 Real-time Dashboard** - Live status updates with automatic refresh capabilities
- **🔔 Smart Notifications** - Email alerts for operation success/failure with retry logic
- **🗄️ Audit Trail** - Complete operation logging with parent-child job relationships
- **🔐 Secure Authentication** - Dynamic service account key upload with session-based security
- **🐳 Production Ready** - Fully containerized with Docker Compose orchestration
- **📱 Responsive UI** - Modern web interface optimized for various screen sizes
- **⚡ Async Processing** - Non-blocking background task execution

## 🏗️ System Architecture

```
┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│   Streamlit     │ ◄──────────────► │    FastAPI      │
│   Frontend      │                  │    Backend      │
└─────────────────┘                  └─────────────────┘
                                              │
                                              ▼
┌─────────────────┐                  ┌─────────────────┐
│   SQLite DB     │                  │  Google Cloud   │
│   (Audit Log)   │                  │   Compute API   │
└─────────────────┘                  └─────────────────┘
```

## 🚀 Quick Start

**Prerequisites**: Docker, Docker Compose, GCP Account with Compute Engine enabled

```bash
# Clone and deploy
git clone https://github.com/hemhemoh/gcp-vm-control
cd gcp-vm-control

# Configure email notifications
echo "SENDER=your-email@gmail.com" > .env
echo "PASSWORD=your-app-password" >> .env

# Launch application stack
docker-compose up --build -d

# Access applications locally
# Frontend: http://localhost:8501
# API Docs: http://localhost:9001/docs
```

## 📋 API Documentation

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/load_config` | Upload service account credentials |
| `GET` | `/list-server` | Retrieve all instances across zones |
| `POST` | `/start-server` | Initialize instance startup sequence |
| `POST` | `/end-server` | Execute instance shutdown procedure |
| `GET` | `/server-status` | Query specific instance state |

**Auto-generated API documentation available at `/docs`**

## 🗃️ Data Models

### Database Schema
```python
# Parent-Child Job Tracking
ParentJob {
    id: int (PK)
    name: str (indexed)
    zone: str (indexed) 
    status: OperationStatus (indexed)
    type: OperationType (indexed)
    is_successful: bool (indexed)
}

ChildJob {
    id: int (PK)
    parent_id: int (FK)
    is_successful: bool
    request_time: datetime
    start_time: datetime
    end_time: datetime
}
```



## 🧪 Development Workflow

```bash
# Local development setup
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Run backend with hot reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 9001

# Run frontend with auto-refresh
streamlit run frontend/app.py --server.port 8501
```

This project demonstrates proficiency in modern Python web development, cloud platform integration, containerized deployment, and production-ready software architecture.