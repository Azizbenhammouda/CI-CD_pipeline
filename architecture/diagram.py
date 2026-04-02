"""
CI/CD Architecture Diagrams – Simple Web App to Azure Container Apps
Generates three diagrams:
  1. Full architecture overview (dev → GitHub → Azure)
  2. CI pipeline detail (GitHub Actions steps)
  3. CD pipeline detail (deploy to Azure Container Apps)

Run:
    pip install diagrams
    python cicd_diagrams.py

Outputs three PNG files in the current directory.
"""

from diagrams import Diagram, Cluster, Edge

# ─── Cloud / Azure ────────────────────────────────────────────────────────────
from diagrams.azure.compute import ContainerApps, ContainerRegistries
from diagrams.azure.database import DatabaseForPostgresqlServers
from diagrams.azure.network import LoadBalancers

# ─── On-prem / OSS ────────────────────────────────────────────────────────────
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.vcs import Github
from diagrams.onprem.container import Docker

# ─── Programming ──────────────────────────────────────────────────────────────
from diagrams.programming.framework import React
from diagrams.programming.language import NodeJS

# ─── Generic ──────────────────────────────────────────────────────────────────
from diagrams.generic.compute import Rack  # developer laptop stand-in

# ──────────────────────────────────────────────────────────────────────────────
# Shared diagram attributes
# ──────────────────────────────────────────────────────────────────────────────
GRAPH_ATTRS = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.6",
    "splines": "ortho",
}

# ──────────────────────────────────────────────────────────────────────────────
# 1. FULL ARCHITECTURE OVERVIEW
# ──────────────────────────────────────────────────────────────────────────────
def diagram_overview():
    with Diagram(
        "Full Architecture Overview – Web App CI/CD to Azure",
        filename="01_overview",
        show=False,
        graph_attr=GRAPH_ATTRS,
        direction="LR",
    ):
        # Developer workstation
        with Cluster("Developer workstation"):
            backend_code = NodeJS("Node.js / Express\nbackend")
            frontend_code = React("React\nfrontend")

        # GitHub platform
        with Cluster("GitHub"):
            repo = Github("Source repo\n(main branch)")
            ghcr = Docker("GHCR\nghcr.io/…")

            with Cluster("GitHub Actions"):
                ci = GithubActions("CI workflow\nci.yaml")
                cd = GithubActions("CD workflow\ncd.yaml")

        # Azure
        with Cluster("Azure"):
            lb = LoadBalancers("Public HTTPS\nendpoint")

            with Cluster("Azure Container Apps"):
                aca_backend = ContainerApps("Backend\nContainer App")
                aca_frontend = ContainerApps("Frontend\nContainer App")

            db = DatabaseForPostgresqlServers("PostgreSQL\n(optional)")

        # ─── Edges ───────────────────────────────────────────────────────────
        backend_code >> Edge(label="git push") >> repo
        frontend_code >> Edge(label="git push") >> repo

        repo >> Edge(label="triggers") >> ci
        ci >> Edge(label="push :sha tag") >> ghcr

        ghcr >> Edge(label="triggers") >> cd
        cd >> Edge(label="az containerapp update") >> aca_backend
        cd >> Edge(label="az containerapp update") >> aca_frontend

        lb >> aca_frontend
        lb >> aca_backend
        aca_backend >> Edge(label="queries") >> db


# ──────────────────────────────────────────────────────────────────────────────
# 2. CI PIPELINE DETAIL
# ──────────────────────────────────────────────────────────────────────────────
def diagram_ci():
    with Diagram(
        "CI Pipeline – Lint → Test → Build → Push",
        filename="02_ci_pipeline",
        show=False,
        graph_attr=GRAPH_ATTRS,
        direction="LR",
    ):
        with Cluster("Trigger: push / pull_request"):
            repo = Github("GitHub repo\n(any branch)")

        with Cluster("GitHub Actions runner (ubuntu-latest)"):

            with Cluster("Backend job"):
                b_checkout = GithubActions("Checkout\ncode")
                b_install  = NodeJS("npm ci\n(install deps)")
                b_lint     = GithubActions("npm run lint\n(ESLint)")
                b_test     = GithubActions("npm test\n(Jest / Mocha)")
                b_build    = Docker("docker build\n–t backend:$SHA")
                b_push_b   = Docker("docker push\nghcr.io/…/backend:$SHA")

            with Cluster("Frontend job"):
                f_checkout = GithubActions("Checkout\ncode")
                f_install  = React("npm ci\n(install deps)")
                f_lint     = GithubActions("npm run lint\n(ESLint)")
                f_test     = GithubActions("npm test\n(Vitest / Jest)")
                f_build    = Docker("docker build\n-f frontend.Dockerfile")
                f_push_f   = Docker("docker push\nghcr.io/…/frontend:$SHA")

        ghcr = Docker("GitHub Container\nRegistry (GHCR)")

        # ─── Edges ───────────────────────────────────────────────────────────
        repo >> Edge(label="triggers") >> b_checkout
        b_checkout >> b_install >> b_lint >> b_test >> b_build >> b_push_b

        repo >> Edge(label="triggers") >> f_checkout
        f_checkout >> f_install >> f_lint >> f_test >> f_build >> f_push_f

        b_push_b >> ghcr
        f_push_f >> ghcr


# ──────────────────────────────────────────────────────────────────────────────
# 3. CD PIPELINE DETAIL
# ──────────────────────────────────────────────────────────────────────────────
def diagram_cd():
    with Diagram(
        "CD Pipeline – Pull → Deploy to Azure Container Apps",
        filename="03_cd_pipeline",
        show=False,
        graph_attr=GRAPH_ATTRS,
        direction="LR",
    ):
        with Cluster("Trigger: CI workflow completed\n(main branch only)"):
            ci_done = GithubActions("CI workflow\n✓ success")

        with Cluster("GitHub Actions runner (ubuntu-latest)"):

            with Cluster("Deploy job"):
                checkout  = GithubActions("Checkout\ncode")
                az_login  = GithubActions("az login\n(OIDC / Service Principal)")
                pull_b    = Docker("docker pull\nbackend:$SHA")
                pull_f    = Docker("docker pull\nfrontend:$SHA")
                deploy_b  = ContainerApps("az containerapp update\n–– backend")
                deploy_f  = ContainerApps("az containerapp update\n–– frontend")
                smoke     = GithubActions("Smoke test\ncurl /healthz")

        ghcr = Docker("GHCR\nghcr.io/…:$SHA\n(immutable image)")

        with Cluster("Azure Container Apps Environment"):
            aca_b = ContainerApps("Backend\nContainer App")
            aca_f = ContainerApps("Frontend\nContainer App")

        # ─── Edges ───────────────────────────────────────────────────────────
        ci_done >> Edge(label="triggers") >> checkout
        checkout >> az_login >> pull_b
        az_login >> pull_f

        ghcr >> Edge(label="image pull") >> pull_b
        ghcr >> Edge(label="image pull") >> pull_f

        pull_b >> deploy_b >> aca_b
        pull_f >> deploy_f >> aca_f

        deploy_b >> smoke
        deploy_f >> smoke

        aca_b >> Edge(label="HTTPS /api") >> smoke
        aca_f >> Edge(label="HTTPS /") >> smoke


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating diagram 1/3: Full Architecture Overview …")
    diagram_overview()
    print("  ✓  Saved → 01_overview.png")

    print("Generating diagram 2/3: CI Pipeline Detail …")
    diagram_ci()
    print("  ✓  Saved → 02_ci_pipeline.png")

    print("Generating diagram 3/3: CD Pipeline Detail …")
    diagram_cd()
    print("  ✓  Saved → 03_cd_pipeline.png")

    print("\nAll diagrams generated successfully.")
    print("Open the .png files to view your CI/CD architecture.")