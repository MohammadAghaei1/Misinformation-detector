🚀 Ultra-Detailed Deployment Guide: From VS Code to AWS Cloud

This document is the definitive, step-by-step technical manual for deploying the Misinformation Detection System.
🛠️ Phase 1: Accounts & Software Prerequisites

Ensure you have these accounts and tools ready before starting the deployment process.
1. External AI Accounts

    Tavily AI: Register at Tavily.com to obtain your API Key. This is the system's "Web Browser" for real-time verification.

    Hugging Face: Register at HuggingFace.co and generate a Read Token to access the Llama-3.1-8B-Instruct model.

2. Infrastructure Accounts

    AWS Account: Required for EC2 (Virtual Server) and Amazon ECR (Docker Registry) services.

    GitHub: For hosting source code and executing GitHub Actions for CI/CD automation.

3. Local Machine Software

    VS Code: With the Remote - SSH extension installed for direct AWS server management.

    Docker Desktop: Mandatory for building and testing containers locally to replicate the production environment.

    Python 3.10+: Necessary for local dependency management and script testing.

📥 Phase 2: Local Project Setup
Bash

# 1. Clone the project from your GitHub repository
git clone https://github.com/MohammadAghaei1/Misinformation-detector.git

# 2. Enter the project root directory
cd Misinformation-detector

# 3. Local Installation (For testing & VS Code IntelliSense)
# Note: This is NOT needed on the AWS EC2 server as Docker handles this automatically.
pip install -r requirements.txt

💻 Phase 3: Local Deployment (Dockerized)

    Configure Environment: Create a .env file in the root directory and add your keys:
    Plaintext

    TAVILY_API_KEY=your_tavily_key_here
    HF_TOKEN=your_huggingface_token_here
    HF_MODEL=meta-llama/Llama-3.1-8B-Instruct

    Build and Launch: 
    Bash

    # Build the unified Docker image (Backend + Frontend)
    docker build -t misinfo-app .

    # Run the container mapping ports 8000 (API) and 8501 (Dashboard)
    docker run -d -p 8000:8000 -p 8501:8501 --name misinfo-local --env-file .env misinfo-app

🔑 Phase 4: Connecting VS Code to AWS (Remote-SSH)

To manage your EC2 server professionally, follow these steps:

    Press Ctrl+Shift+P in VS Code and select Remote-SSH: Connect to Host...

    Enter the SSH command replacing the key path and IP with your own:
    Bash

    # Replace <your-ec2-ip> with your NEW AWS Public IP
    ssh -i "C:/path/to/your-key.pem" ec2-user@<your-ec2-ip>

    Once connected, go to File > Open Folder to manage server files directly in your IDE.

🛡️ Phase 5: Security & CI/CD (GitHub Secrets)

Following the project's security architecture, tokens are not entered manually on the server. They are managed via GitHub Repository Secrets.

Go to your GitHub repo Settings > Secrets and variables > Actions and add these EXACT keys:

    AWS_ACCESS_KEY_ID: Your AWS programmatic access ID.

    AWS_SECRET_ACCESS_KEY: Your AWS programmatic secret key.

    AWS_REGION: Your server region (e.g., us-east-1).

    ECR_REPOSITORY: Your ECR repository name (e.g., misinfo_repo).

    EC2_SSH_KEY: The text content of your private .pem key.

    HF_TOKEN & TAVILY_API_KEY: Your AI service tokens.

☁️ Phase 6: Cloud Production (AWS + Kubernetes)
1. Requirements on AWS?

NO MANUAL INSTALLATION IS NEEDED! All libraries from requirements.txt are baked into the Docker image during the build process. Your EC2 server only needs Docker and Kubernetes installed.
2. Customization for New Accounts (BEYOND CRITICAL) ⚠️

If deploying on a different AWS account, you MUST edit k8s_deployment.yaml:
YAML

# Replace '527582557235' with your NEW unique AWS Account ID
image: <NEW_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/misinfo_repo:latest

3. Database Persistence (SQLite)

To prevent your news history from being wiped during code updates, we use a HostPath Volume.

    This maps the physical folder /home/ec2-user/misinfo_data on the EC2 host to the database folder inside the container.

4. Kubernetes Execution (Via VS Code SSH Terminal)
Bash

# Apply Deployment manifest (sets 900Mi RAM limit and pulls image from ECR)
kubectl apply -f k8s_deployment.yaml

# Apply Service manifest (Exposes ports 30001 for Backend and 30002 for Frontend)
kubectl apply -f k8s_service.yaml

🧪 Phase 7: Post-Deployment Verification

To access the dashboard, use the IP address assigned by AWS to your server:

    Frontend Dashboard: http://<YOUR-EC2-IP>:30002/

    Backend Health: http://<YOUR-EC2-IP>:30001/health