# Guide to Deploying New Changes to Cloud Run

This guide provides the steps to build and deploy a new version of the Data Agent Platform to your existing Google Cloud Run service.

## Prerequisites

1.  **Google Cloud SDK:** Ensure the `gcloud` CLI is installed and you are authenticated.
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
2.  **Docker:** Ensure Docker Desktop is running on your machine.
3.  **Project Configuration:** Make sure you are in the correct Google Cloud project.
    ```bash
    gcloud config set project dataagentplatform
    ```

## Deployment Steps

Follow these steps from the root directory of the project each time you want to deploy an update.

### Step 1: Set Environment Variables

Open your terminal and run the following commands to set the necessary environment variables. These are used to tag your Docker image correctly and target the right Cloud Run service.

```bash
export PROJECT_ID="dataagentplatform"
export REGION="europe-west4"
export REPO_NAME="data-agent-platform-repo"
export IMAGE_NAME="data-agent-platform"
export IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest"
```

### Step 2: Build the Docker Image

Build the new version of your application into a Docker image. The `--platform linux/amd64` flag is crucial to ensure the image is compatible with Cloud Run.

```bash
docker build --platform linux/amd64 -t ${IMAGE_TAG} .
```

### Step 3: Push the Docker Image

Push the newly built image to your Google Artifact Registry repository.

```bash
docker push ${IMAGE_TAG}
```

### Step 4: Deploy to Cloud Run

Deploy the new image to the existing `data-agent-platform` service on Cloud Run. This command updates the service to use the new image you just pushed. It keeps all the existing settings (like environment variables, memory, etc.) but deploys the new container.

```bash
gcloud run deploy data-agent-platform \
  --image=${IMAGE_TAG} \
  --region=${REGION} \
  --project=${PROJECT_ID}
```

---

That's it! After the `gcloud run deploy` command completes, the new version of your application will be live.
