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

## System Architecture

The platform utilizes a multi-agent system built with the Google Cloud Agent Development Kit (ADK). The key agents and their roles are:

*   **SchemaAgent:** Connects to Google BigQuery to discover available datasets and tables. It retrieves and provides detailed schema information (column names, data types) for the user-selected dataset, which is crucial for contextual understanding.
*   **DataAnalystAgent:** This agent is the core query processing unit. It receives a natural language query from the user and the comprehensive schema of the selected dataset (provided by the `SchemaAgent`). It then leverages a Large Language Model (LLM, e.g., Gemini) to translate the natural language query into an optimized BigQuery SQL query. After generating the SQL, it executes the query against the target dataset and returns the structured results.
*   **VisualizationAgent:** Takes the structured data (typically a pandas DataFrame) returned by the `DataAnalystAgent`. It analyzes this data to automatically generate relevant visualizations (e.g., bar charts, histograms, scatter plots using Plotly) and can also extract simple textual insights from the data.
*   **Orchestration:** These agents are integrated within a Dash web application. User interactions trigger callbacks that manage the flow of information: from selecting a dataset, entering a query, invoking the `SchemaAgent`, then the `DataAnalystAgent`, and finally the `VisualizationAgent`, with the results (SQL, data tables, charts, insights) being rendered back to the user interface.

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

## Deploying to Google Cloud Run

This application is containerized and can be deployed to Google Cloud Run.

### Prerequisites for Cloud Run Deployment

1.  **Google Cloud SDK:** Ensure you have `gcloud` CLI installed and authenticated (`gcloud auth login`, `gcloud auth application-default login`).
2.  **Google Cloud Project:** You should have your GCP Project ID ready and the necessary APIs enabled (BigQuery API, Vertex AI API, Cloud Storage API, Cloud Resource Manager API, Artifact Registry API, Cloud Run API). Refer to the "Google Cloud Setup Instructions" section.
3.  **Service Account:** A service account with appropriate permissions (e.g., BigQuery Admin, Vertex AI Admin, Storage Admin) should be created. It's recommended to assign this service account to the Cloud Run service for secure access to other Google Cloud services. Let's assume your service account email is `your-service-account-email@your-project-id.iam.gserviceaccount.com`.
4.  **Enable Artifact Registry:** If not already enabled, run:
    `gcloud services enable artifactregistry.googleapis.com`
5.  **Create an Artifact Registry Docker Repository:**
    `gcloud artifacts repositories create YOUR_REPO_NAME --repository-format=docker --location=YOUR_REGION --description="Docker repository for Data Agent Platform"`
    (Replace `YOUR_REPO_NAME` and `YOUR_REGION`, e.g., `data-agent-platform-repo` and `us-central1`).
6.  **Configure Docker:**
    `gcloud auth configure-docker YOUR_REGION-docker.pkg.dev` (e.g., `us-central1-docker.pkg.dev`)

### Deployment Steps

1.  **Set Environment Variables (Shell):**
    Replace placeholders with your actual values.
    ```bash
    export PROJECT_ID="dataagentplatform"
    export REGION="europe-west4" # e.g., us-central1
    export REPO_NAME="data-agent-platform-repo" # e.g., data-agent-platform-repo
    export IMAGE_NAME="data-agent-platform" # Or your preferred image name
    export IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest"
    export SERVICE_ACCOUNT_EMAIL="data-agent-platform-service-ac@${PROJECT_ID}.iam.gserviceaccount.com"
    # Ensure this service account has roles like BigQuery Admin, Vertex AI User, Storage Object Admin.
    ```

2.  **Build the Docker Image:**
    Navigate to the project root directory (where the Dockerfile is).
    ```bash
    docker build -t ${IMAGE_TAG} .
    ```

3.  **Push the Docker Image to Artifact Registry:**
    ```bash
    docker push ${IMAGE_TAG}
    ```

4.  **Deploy to Cloud Run:**
    ```bash
    gcloud run deploy ${IMAGE_NAME} \
        --image ${IMAGE_TAG} \
        --platform managed \
        --region ${REGION} \
        --service-account ${SERVICE_ACCOUNT_EMAIL} \
        --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID} \ # Pass project ID as env var
        # --allow-unauthenticated \ # Uncomment if you want public access
        --port 8080 # Cloud Run will set the PORT env var to this, Gunicorn will use it.
                    # Or remove --port if your base image expects PORT=8080 by default.
                    # The Dockerfile uses $PORT, so Cloud Run will manage it.
                    # The --port flag on gcloud run deploy specifies the container port to send requests to.
                    # Since our gunicorn command uses $PORT, Cloud Run sets $PORT (often 8080 by default internally)
                    # and gcloud run deploy's --port should match what gunicorn expects OR be omitted if gunicorn uses $PORT.
                    # Let's assume gunicorn inside the container will listen on the $PORT value set by Cloud Run.
                    # The default internal PORT by Cloud Run is often 8080.
                    # The important part is that our Dockerfile CMD uses $PORT.
                    # No --port needed here usually if CMD uses $PORT.

    # Example without --port, relying on Cloud Run's default $PORT which Gunicorn uses:
    gcloud run deploy ${IMAGE_NAME} \
        --image ${IMAGE_TAG} \
        --platform managed \
        --region ${REGION} \
        --service-account ${SERVICE_ACCOUNT_EMAIL} \
        --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID} \
        --allow-unauthenticated # Or remove for private access

    # After deployment, gcloud will provide the URL to access your application.
    ```
    **Note on Environment Variables in Cloud Run:**
    - `GOOGLE_CLOUD_PROJECT` is explicitly set here. Your application code uses this to initialize clients.
    - If your application relies on `GOOGLE_APPLICATION_CREDENTIALS` (e.g., if you were running locally with a service account JSON file), you *do not* need to set this when deploying to Cloud Run if you assign a service account to the Cloud Run service. The service will automatically use the permissions of the assigned service account.

5.  **Accessing the Application:**
    Once deployed, `gcloud` will output a URL for your service. You can also find it in the Google Cloud Console under Cloud Run.

## Hackathon Submission

This project was created specifically for the Google Cloud Agent Development Kit Hackathon 2025 (#adkhackathon). It demonstrates innovative use of ADK tools and Google Cloud services while showcasing multi-agent collaboration and learning capabilities.

## License

MIT License
