# Dynamic Data Agent Platform

A multi-agent data analysis platform built with Google Cloud's Agent Development Kit (ADK) for the Google Cloud Agent Development Kit Hackathon 2025.

## Project Overview

This project demonstrates an intelligent data analysis platform that leverages Google Cloud's Agent Development Kit to create a multi-agent system for data processing and analysis. The platform is designed to showcase advanced AI capabilities and multi-agent collaboration.

## Features

- Multi-agent system architecture using ADK
- Dynamic data schema understanding
- Intelligent query processing and optimization
- Cloud-native architecture with Google Cloud integration
- Agent learning and adaptation capabilities
- Cost-optimized cloud resource usage

## Technology Stack

- Google Cloud Agent Development Kit (ADK)
- Google Cloud Platform Services:
  - BigQuery
  - Vertex AI
  - Cloud Storage
- Python
- Dash/Plotly for visualization

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Docker Desktop
- Google Cloud SDK
- Google Cloud Project with BigQuery enabled

### Google Cloud Setup Instructions

1. Create Google Cloud Project:
   - Go to Google Cloud Console: https://console.cloud.google.com/
   - Click on the project dropdown and select "New Project"
   - Name your project "DataAgentPlatform"
   - Click "Create"

2. Enable Required APIs:
   - In the Google Cloud Console:
     - Search for and enable these APIs:
       - BigQuery API
       - Vertex AI API
       - Cloud Storage API
       - Cloud Resource Manager API

3. Create Service Account and Download Credentials:
   - Go to IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Name it "data-agent-platform-service-account"
   - Description: "Service account for Data Agent Platform"
   - Click "Create"
   - Grant the following roles:
     - BigQuery Admin
     - Storage Admin
     - Vertex AI Admin
   - Click "Continue"
   - Click "Create Key"
   - Select JSON format
   - Click "Create"
   - Save the downloaded JSON file as `credentials.json` in your project root directory

4. Set up Environment Variables:
   - Create a `.env` file in your project root directory with:
   ```
   GOOGLE_CLOUD_PROJECT=data-agent-platform
   ```

5. Set up BigQuery Dataset:
   - In BigQuery Console:
     - Create a new dataset named `data_agent_platform`
     - Set location to your preferred region
     - Enable partitioning and clustering for cost optimization

6. Verify Setup:
   - Run this command to verify your credentials:
   ```bash
   gcloud auth application-default print-access-token
   ```

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/diipak/DataAgentPlatform.git
cd DataAgentPlatform
```

2. Create a `credentials.json` file with your Google Cloud credentials:
```bash
gcloud auth application-default login
```

3. Start the application using docker-compose:
```bash
docker-compose up --build
```

The application will be available at http://localhost:8050

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/diipak/DataAgentPlatform.git
cd DataAgentPlatform
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `credentials.json` file with your Google Cloud credentials:
```bash
gcloud auth application-default login
```

5. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:8050

## Hackathon Submission

This project was created specifically for the Google Cloud Agent Development Kit Hackathon 2025 (#adkhackathon). It demonstrates innovative use of ADK tools and Google Cloud services while showcasing multi-agent collaboration and learning capabilities.

## License

MIT License
