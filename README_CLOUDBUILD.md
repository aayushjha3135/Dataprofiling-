Deploying with Cloud Build (no local Docker)

Overview

This project includes `cloudbuild.yaml` which instructs Cloud Build to:
- build a Docker image from your repository,
- push the image to Container Registry (gcr.io),
- deploy the image to Cloud Run as service `data-profiling-ai` in `us-central1`,
  and set the environment variables so the app uses your bucket `synthetic-data-194769473145`.

Options to run the build

A) Use the Google Cloud Console (no CLIs required locally)
1. Open the Cloud Console: https://console.cloud.google.com/cloud-build/builds
2. Click "Run build" > "Create build"
3. Choose "Upload a .zip file" and upload a zip of your repository (or select a connected Cloud Source Repository/GitHub repo)
4. For "Build configuration" choose "Cloud Build configuration file (yaml or json)" and ensure the path is `cloudbuild.yaml`.
5. Start the build. Cloud Build will run the steps in `cloudbuild.yaml`.
6. After the deploy step completes, Cloud Run will contain the `data-profiling-ai` service; click the service to open the URL.

B) Use `gcloud` from a machine (requires gcloud installed)
1. From the project directory run (this submits the local source to Cloud Build):

```powershell
gcloud auth login
gcloud config set project wfargo-cdo25cbh-915
gcloud builds submit --config=cloudbuild.yaml .
```

2. Wait for the build to complete; the Cloud Run URL will be shown in the final step output.

IAM / Permissions required

Ensure the Cloud Build service account has the following roles on the project (replace `PROJECT_ID` with `wfargo-cdo25cbh-915`):
- roles/run.admin (Cloud Run Admin)
- roles/storage.admin (Cloud Storage Admin)
- roles/iam.serviceAccountUser (for deploying with a service account)
- roles/cloudbuild.builds.builder (Cloud Build builder)

You can grant roles via Cloud Console IAM page or via `gcloud`:

```powershell
PROJECT=wfargo-cdo25cbh-915
CB_SA=$(gcloud projects describe $PROJECT --format="value(projectNumber)")"-@cloudbuild.gserviceaccount.com"
# Example (run with your admin account):
# gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$CB_SA" --role="roles/run.admin"
```

Notes and tips

- Cloud Build runs in Google infrastructure and does not require Docker to be installed locally.
- If you prefer Artifact Registry instead of Container Registry (gcr.io), I can provide an updated `cloudbuild.yaml`.
- The deployment sets env var `DEFAULT_BUCKET=synthetic-data-194769473145` so the app will write uploads and profiles there.

Troubleshooting

- If the build fails during the `docker build` step, inspect the Cloud Build logs to see the error and share them with me if you want help debugging.
- If the Cloud Run deploy step fails due to IAM permissions, grant the Cloud Build service account the required roles above.

If you want, I can also:
- create a Cloud Build trigger that deploys on every push to a branch (GitHub/Cloud Source Repos), or
- convert this pipeline to use Artifact Registry (recommended for new projects).

Create a GitHub trigger (recommended)
-----------------------------------

I added `create_trigger.ps1` which automates creating a Cloud Build GitHub trigger. To use it:

1. Make sure `gcloud` is installed and you're authenticated:

```powershell
gcloud auth login
gcloud config set project wfargo-cdo25cbh-915
```

2. Install or confirm the Cloud Build GitHub App is connected to your GitHub account and the target repository. If not, the script will attempt to start the connect flow.

3. Run the trigger creation script (replace placeholders):

```powershell
.\create_trigger.ps1 -RepoOwner "YOUR_GITHUB_OWNER" -RepoName "YOUR_REPO_NAME" -BranchPattern "^main$"
```

This will create a trigger named `data-profiling-ai-trigger` that runs `cloudbuild.yaml` on pushes to the `main` branch.

If you prefer I set up the trigger for a Cloud Source Repository instead of GitHub, tell me the repo name and I can generate the appropriate `gcloud` command or script.
