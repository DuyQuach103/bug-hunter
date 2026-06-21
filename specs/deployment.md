# Deployment Specifications - Bug Hunter

This document details the configuration, prerequisites, and step-by-step commands required to deploy the Bug Hunter Flask application to Google Cloud Run.

## Deployment Target Overview

Google Cloud Run is a managed compute platform that automatically scales your stateless containers. It is chosen for hosting Bug Hunter because:
1. **Scale-to-Zero**: Billed only when handling requests, costing $0.00 during idle periods.
2. **Public URL**: Automatically provisions an HTTPS endpoint.
3. **Container-based**: Guarantees identical execution environments between local development and production.

---

## 1. Prerequisites

Before running the deployment commands, you must configure the following:
* **GCP Project**: An active Google Cloud project (e.g. `my-day-2-project`).
* **Billing Account**: An active billing account must be linked to your project.
* **Google Cloud SDK (`gcloud`)**: Installed and authenticated locally:
  ```bash
  gcloud auth login
  gcloud config set project my-day-2-project
  ```

---

## 2. API Activation

Enable the required services in your target project:
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  --project=my-day-2-project
```

---

## 3. Secret Manager Setup (Gemini API Key)

To avoid exposing your Gemini API key in plaintext environment variables, store it securely in GCP Secret Manager:

1. **Create the Secret**:
   ```bash
   gcloud secrets create gemini-api-key --replication-policy="automatic" --project=my-day-2-project
   ```
2. **Add the Secret Value**:
   Extract the key from your local `.env` file and upload it:
   ```bash
   echo -n "YOUR_GEMINI_API_KEY_HERE" | gcloud secrets versions add gemini-api-key --data-file=- --project=my-day-2-project
   ```

---

## 4. Dockerization

The container is built using the project's `Dockerfile`:
* **Base Image**: `python:3.11-slim`
* **WSGI Server**: `gunicorn` (added to `requirements.txt`)
* **Entrypoint**:
  ```dockerfile
  CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 server:app
  ```

---

## 5. Build & Deploy Command

Deploy the service publicly with a budget safety limit of **1 maximum instance** to prevent any unexpected charges:

```bash
gcloud run deploy bug-hunter \
  --source . \
  --project my-day-2-project \
  --region us-central1 \
  --allow-unauthenticated \
  --max-instances 1 \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest
```

### Deployment Parameters:
* `--source .`: Packs local code, uploads it to Cloud Build, compiles the container, and pushes it to Artifact Registry.
* `--allow-unauthenticated`: Makes the endpoint publicly accessible.
* `--max-instances 1`: Limits the service to a single container to guarantee low resource usage and avoid unexpected billing spikes.
* `--set-secrets`: Securely binds the Secret Manager entry to the `GEMINI_API_KEY` environment variable inside the container.

---

## 6. Verification

Once deployment completes, the command will print a Service URL (e.g. `https://bug-hunter-xxxxx-uc.a.run.app`). Verify it responds using `curl`:

```bash
curl -I https://bug-hunter-xxxxx-uc.a.run.app
```
Or open the URL in your browser to access the live dashboard.
