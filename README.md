# Python Pipeline Microservice

This repository contains a Python Flask microservice (`python-pipeline`) designed for deployment across `dev`, `stage`, and `prod` Kubernetes clusters using a CI/CD pipeline with GitLab runners, Harbor, and ArgoCD. The application is currently deployed to the `dev` cluster in the `python-pipeline` namespace, accessible via `http://python-pipeline.dev.virtualelephant.com`.

## Repository Structure

```
python-pipeline/
├── k8s/
│   ├── argocd/
│   │   ├── python-pipeline-app.yaml         # ArgoCD Application for dev
│   │   ├── python-pipeline-namespace.yaml   # ArgoCD Application for namespace
│   │   ├── python-pipeline-stage-app.yaml   # ArgoCD Application for stage (future)
│   │   ├── python-pipeline-prod-app.yaml    # ArgoCD Application for prod (future)
│   ├── dev/
│   │   ├── python-pipeline-deployment.yaml  # Deployment, Service, Ingress for dev
│   │   ├── python-pipeline-namespace.yaml   # Namespace definition for dev
│   ├── stage/
│   │   ├── python-pipeline-deployment.yaml  # Deployment, Service, Ingress for stage
│   │   ├── python-pipeline-namespace.yaml   # Placeholder for stage
│   ├── prod/
│   │   ├── python-pipeline-deployment.yaml  # Placeholder for prod
│   │   ├── python-pipeline-namespace.yaml   # Placeholder for prod
├── .gitlab-ci.yml                            # GitLab CI pipeline configuration
├── app.py                                   # Flask application
├── Dockerfile                               # Container build instructions
├── README.md                                # This file
├── requirements.txt                         # Python dependencies
```

## Prerequisites

Before deploying the `python-pipeline` application, ensure the following:

1. **GitLab Access**:
   - Access to the repository: `http://gitlab.home.virtualelephant.com/devops1/python-pipeline.git`.
   - A Project Access Token (`devops-user1-gitlab-token`) with `api`, `read_repository`, and `write_repository` scopes.
   - GitLab CI variables set:
     - `GITLAB_USER`: Username for the token (e.g., `devops-user1`).
     - `GITLAB_TOKEN`: Project Access Token value (masked, protected).
     - `HARBOR_USERNAME`: Harbor registry username (masked, protected).
     - `HARBOR_PASSWORD`: Harbor registry password (masked, protected).

2. **Kubernetes Clusters**:
   - `dev` cluster with kubeconfig at `/home/user/.kube/dev-config`.
   - Clusters running InfluxDB, Grafana, Prometheus, and Longhorn.
   - NGINX Ingress controller installed in the `dev` cluster (namespace: `ingress-nginx`).
   - DNS configured for `python-pipeline.dev.virtualelephant.com`.

3. **Harbor Registry**:
   - Registry at `harbor.home.virtualelephant.com`, project `ve-lab`.
   - Image: `harbor.home.virtualelephant.com/ve-lab/python-pipeline-app:<CI_COMMIT_SHA>`.

4. **ArgoCD**:
   - Installed in the `services` namespace on an external Kubernetes cluster.
   - `dev` cluster registered in ArgoCD with server URL `https://dev-cluster-api:6443`.

5. **Tools**:
   - `kubectl` configured with access to the `dev` cluster.
   - `argocd` CLI (optional for manual syncs).
   - Git installed locally.

## Deployment Process

The `python-pipeline` application is deployed to the `dev` cluster’s `python-pipeline` namespace using a GitLab CI pipeline and ArgoCD. Follow these steps to deploy or update the application.

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone http://gitlab.home.virtualelephant.com/devops1/python-pipeline.git
cd python-pipeline
```

### Step 2: Update Application Code (Optional)

To modify the Flask application:

1. Edit `app.py` (e.g., add new endpoints).
2. Update `requirements.txt` if new dependencies are needed (currently `flask==2.0.3`, `werkzeug==2.0.3`).
3. Ensure the `Dockerfile` remains secure (runs as non-root user `appuser`).

Example `app.py`:
```python
#!/usr/bin/env python3
"""Simple Flask web server for a micro-services application."""
import logging
from typing import Dict, Any
from flask import Flask, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check() -> Dict[str, Any]:
    """Return health status of the application."""
    logger.info("Health check requested")
    return jsonify({"status": "healthy", "message": "Application is running"})

@app.route("/", methods=["GET"])
def index() -> Dict[str, Any]:
    """Return a welcome message."""
    logger.info("Index endpoint requested")
    return jsonify({"message": "Welcome to the micro-services demo!"})

def main() -> None:
    """Main entry point for the application."""
    logger.info("Starting Flask application")
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
```

### Step 3: Commit and Push Changes

Commit changes to the `main` branch:

```bash
git add app.py requirements.txt Dockerfile
git commit -m "Update Flask application"
git push origin main
```

### Step 4: Run the GitLab CI Pipeline

The push to `main` triggers the pipeline defined in `.gitlab-ci.yml`:

- **Build Stage**:
  - Builds the container using `Dockerfile`.
  - Pushes to Harbor as `harbor.home.virtualelephant.com/ve-lab/python-pipeline-app:<CI_COMMIT_SHA>`.

- **Deploy_dev Stage**:
  - Updates `k8s/dev/python-pipeline-deployment.yaml` with the new SHA.
  - Commits and pushes to `main` with `[skip ci]` to prevent pipeline loops.

Check the pipeline status in GitLab:
- Go to **CI/CD > Pipelines** at `http://gitlab.home.virtualelephant.com/devops1/python-pipeline`.
- Ensure `build` and `deploy_dev` jobs pass.

### Step 5: Verify ArgoCD Deployment

ArgoCD (in the `services` namespace) syncs the application based on `k8s/argocd/python-pipeline-app.yaml`, which watches `k8s/dev/` for changes.

1. **Check ArgoCD Status**:
   - Log in to the ArgoCD UI.
   - Navigate to the `python-pipeline-app` application.
   - Verify it is **Healthy** and **Synced**.

2. **Manual Sync (if needed)**:
   ```bash
   argocd app sync python-pipeline-app --namespace services
   ```

3. **Verify Resources**:
   - Switch to the `dev` cluster’s kubeconfig:
     ```bash
     export KUBECONFIG=/home/user/.kube/dev-config
     ```
   - Check pods:
     ```bash
     kubectl get pods -n python-pipeline
     ```
     Expected output:
     ```
     NAME                              READY   STATUS    RESTARTS   AGE
     python-pipeline-app-xxx   1/1     Running   0          Xm
     python-pipeline-app-yyy   1/1     Running   0          Xm
     ```
   - Check the Service:
     ```bash
     kubectl get svc -n python-pipeline
     ```
     Expected output:
     ```
     NAME                     TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
     python-pipeline-service   ClusterIP   10.43.180.7   <none>        80/TCP    Xm
     ```
   - Check the Ingress:
     ```bash
     kubectl get ingress -n python-pipeline
     ```
     Expected output:
     ```
     NAME                     CLASS    HOSTS                                ADDRESS   PORT(S)   AGE
     python-pipeline-ingress   nginx    python-pipeline.dev.virtualelephant.com   <ip>      80      Xm
     ```

4. **Verify Application**:
   - Test the health endpoint:
     ```bash
     curl http://python-pipeline.dev.virtualelephant.com/health
     ```
     Expected output:
     ```json
     {"status": "healthy", "message": "Application is running"}
     ```
   - Test the root endpoint:
     ```bash
     curl http://python-pipeline.dev.virtualelephant.com/
     ```
     Expected output:
     ```json
     {"message": "Welcome to the micro-services demo!"}
     ```
   - Check logs:
     ```bash
     kubectl logs -n python-pipeline -l app.kubernetes.io/name=python-pipeline-app
     ```

### Step 6: Monitoring (Optional)

To leverage the `dev` cluster’s Prometheus and Grafana:

1. Add Prometheus metrics to `app.py`:
   - Update `requirements.txt`:
     ```
     flask==2.0.3
     werkzeug==2.0.3
     prometheus_flask_exporter==0.23.1
     ```
   - Update `app.py` to include `PrometheusMetrics` (see repository for example).
   - Commit and push changes.

2. Configure Prometheus to scrape the `/metrics` endpoint:
   ```yaml
   scrape_configs:
     - job_name: python-pipeline-app
       static_configs:
         - targets: ['python-pipeline-service.python-pipeline.svc.cluster.local:80']
   ```

3. Use Grafana to create dashboards for request counts, latency, and errors.

### Troubleshooting

- **Pipeline Fails**:
  - Check logs in GitLab (**CI/CD > Pipelines**).
  - Verify `GITLAB_USER`, `GITLAB_TOKEN`, `HARBOR_USERNAME`, and `HARBOR_PASSWORD` are set correctly (masked, protected).
  - Ensure the `main` branch is accessible to `devops-user1`.

- **ArgoCD OutOfSync**:
  - Check events: `argocd app events python-pipeline-app --namespace services`.
  - Verify manifests in `k8s/dev/python-pipeline-deployment.yaml` (no invalid fields like `template` in `Service` or `Ingress`).
  - Check ArgoCD logs: `kubectl logs -n services -l app.kubernetes.io/name=argocd-server`.

- **Pod Errors**:
  - Check logs: `kubectl logs -n python-pipeline -l app.kubernetes.io/name=python-pipeline-app`.
  - Verify the image exists: `docker pull harbor.home.virtualelephant.com/ve-lab/python-pipeline-app:<CI_COMMIT_SHA>`.

- **Ingress Issues**:
  - Ensure the NGINX Ingress controller is running: `kubectl get pods -n ingress-nginx`.
  - Verify DNS for `python-pipeline.dev.virtualelephant.com`.

### Security Best Practices

- **GitLab**:
  - Protect the `main` branch (**Settings > Repository > Protected branches**) to require approvals.
  - Rotate `devops-user1-gitlab-token` periodically.
- **Kubernetes**:
  - The `Dockerfile` runs as a non-root user (`appuser`).
  - Add an image pull secret if Harbor requires authentication:
    ```bash
    kubectl create secret docker-registry harbor-creds --docker-server=harbor.home.virtualelephant.com --docker-username=$HARBOR_USERNAME --docker-password=$HARBOR_PASSWORD -n python-pipeline
    ```
    Update `k8s/dev/python-pipeline-deployment.yaml`:
    ```yaml
    spec:
      imagePullSecrets:
        - name: harbor-creds
    ```
- **Application**:
  - Dependencies are pinned in `requirements.txt` to avoid supply chain attacks.
  - Use `flake8` for linting: Add a test stage to `.gitlab-ci.yml`.

### Future Steps

- **Stage and Prod Deployment**:
  - Configure `k8s/stage/python-pipeline-deployment.yaml` and `k8s/argocd/python-pipeline-stage-app.yaml` for the `stage` cluster.
  - Add `deploy_stage` and `deploy_prod` jobs to `.gitlab-ci.yml` with manual triggers.
- **Testing**:
  - Add a test stage to `.gitlab-ci.yml` for linting (`flake8`) and unit tests (`pytest`).
- **Monitoring**:
  - Enable Prometheus metrics and create Grafana dashboards.