# Deploying Documentation

Easily publish your documentation site for `sluggi` using MkDocs and GitHub Pages.

---

## Deploy to GitHub Pages (Manual)

1. Ensure `mkdocs-material` is installed:
   ```bash
   pip install mkdocs-material
   ```
2. Commit all changes to your repository.
3. Deploy:
   ```bash
   mkdocs gh-deploy
   ```
   This will build and deploy your docs to GitHub Pages.

Your documentation will be available at:
```
https://blip-box.github.io/sluggi/
```

---

## Deploy Automatically with GitHub Actions (Recommended)

- Use the official [MkDocs Deploy Action](https://github.com/marketplace/actions/deploy-mkdocs-to-github-pages) for CI/CD.
- Example workflow: `.github/workflows/deploy-docs.yml`

---

!!! info "Local preview & troubleshooting"
    - Preview locally with `mkdocs serve`
    - For advanced configuration, see [`mkdocs.yml`](https://github.com/blip-box/sluggi/blob/main/mkdocs.yml) and the [MkDocs Material documentation](https://squidfunk.github.io/mkdocs-material/).
