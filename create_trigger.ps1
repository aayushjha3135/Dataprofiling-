<#
create_trigger.ps1

Creates a Cloud Build trigger that deploys this repository to Cloud Run using cloudbuild.yaml.

Usage (fill in your GitHub repo owner/name):
.\create_trigger.ps1 -RepoOwner "YOUR_GITHUB_OWNER" -RepoName "YOUR_REPO_NAME" -BranchPattern "^main$"

Prerequisites:
- gcloud installed and authenticated (gcloud auth login)
- Your GitHub account connected to Cloud Build (the script will attempt to open the browser to connect if not already connected)
- You must have Owner/Admin access to the repository to install the Cloud Build GitHub App
#>
param(
    [string]$Project = "wfargo-cdo25cbh-915",
    [string]$RepoOwner = "YOUR_GITHUB_OWNER",
    [string]$RepoName = "YOUR_REPO_NAME",
    [string]$BranchPattern = "^main$",
    [string]$TriggerName = "data-profiling-ai-trigger"
)

Write-Host "Creating Cloud Build GitHub trigger for repo: $RepoOwner/$RepoName (project: $Project)"

# Ensure gcloud project is set
gcloud config set project $Project

# Ensure GitHub App connection exists (this will open a browser if needed)
Write-Host "Checking for existing GitHub App connections..."
$connections = gcloud alpha builds connections list --project=$Project --format="value(name)" 2>$null
if (-not $connections) {
    Write-Host "No Cloud Build GitHub connections found. Launching connect flow..."
    gcloud alpha builds connections create github "github-connection" --project=$Project
}

# Create the trigger using the GitHub connection
Write-Host "Creating trigger (this may require that you approve the GitHub App on the repo)..."

# Use 'gcloud beta' if 'alpha' isn't available in your SDK
try {
    gcloud alpha builds triggers create github \
        --name="$TriggerName" \
        --repo-owner="$RepoOwner" \
        --repo-name="$RepoName" \
        --branch-pattern="$BranchPattern" \
        --build-config="cloudbuild.yaml" \
        --project="$Project"
}
catch {
    Write-Host "Falling back to beta command (if alpha is unavailable)..."
    gcloud beta builds triggers create github \
        --name="$TriggerName" \
        --repo-owner="$RepoOwner" \
        --repo-name="$RepoName" \
        --branch-pattern="$BranchPattern" \
        --build-config="cloudbuild.yaml" \
        --project="$Project"
}

Write-Host "Trigger creation finished. Visit Cloud Console -> Cloud Build -> Triggers to verify."