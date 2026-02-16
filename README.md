# 🛡️ Real-Time Misinformation Detector (RAG-Powered)

An end-to-end AI platform designed to verify news veracity by cross-referencing claims with live web data using **Retrieval-Augmented Generation (RAG)**.

---

## 🏗️ Project Structure & Architecture

The system is built with a modular architecture, separating intelligence, interface, and infrastructure.

### 1. ⚙️ Backend: The Intelligence Engine (FastAPI)
The backend manages the complex logic of news analysis and data orchestration:
* **RAG Pipeline**: Integrates **Tavily AI** for real-time web context and **Llama 3.1 8B** (via HuggingFace API) for logical reasoning.
* **Web Scraper**: Built with **BeautifulSoup4**, it extracts clean article content while bypassing simple bot protections.
* **Smart Caching**: Implements a global cache in **SQLite** to reduce latency and API costs.
* **Security**: Handles user authentication using **bcrypt** password hashing.

### 2. 🖼️ Frontend: The Dashboard (Streamlit)
The frontend provides an intuitive and responsive user experience:
* **Data Visualization**: Integration with **Plotly** to generate real-time charts showing the veracity distribution (Fake vs. Real) of analyzed news.
* **Interactive Features**: Supports URL scraping, raw text analysis, and user feedback loops.
* **History Management**: A persistent log of all previous analyses, filtered by user ID.

---

## 🤖 DevOps & MLOps Integration

This project is a production-ready system with a modern lifecycle. 

### MLOps Workflow:
* **Model Inference**: Optimized to run an 8B parameter model on low-resource environments using cloud-based **Inference APIs**.
* **Prompt Engineering**: Solved the "Label-Explanation Mismatch" by implementing strict **Mandatory Labeling Rules**.

### DevOps Workflow:
* **CI/CD Pipeline**: Automated **GitHub Actions** to build and push images to **Amazon ECR**.
* **Containerization**: The entire application is containerized using **Docker**.
* **Orchestration**: Managed via **Kubernetes (K8s)** with defined resource limits.

---

## 🚀 Dual-Mode Deployment

The system supports two primary deployment scenarios:

### 1. 💻 Local Deployment (Development)
* **Fast Setup**: Bundles both Backend and Frontend into a single Docker image.
* **Resource Efficient**: Tuned to run on low-RAM instances using Linux **Swap space**.

### 2. ☁️ Cloud Deployment (AWS/Production)
* **Cloud Infrastructure**: Deployed on **Amazon EC2** using **Kubernetes** manifests.
* **Data Persistence**: Configured with **K8s HostPath Volumes** for SQLite persistence.
* **Security**: API tokens are managed securely via **Kubernetes Secrets**.

---

## 📖 Setup & Deployment Guides
For detailed, step-by-step instructions, please refer to:
👉 **[DEPLOYMENT.md](./DEPLOYMENT.md)**

---

## ⚖️ License

This project is licensed under the **GNU GPLv3 License**. See the license file for details.
