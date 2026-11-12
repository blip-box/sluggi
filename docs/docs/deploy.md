# Documentation site

This site is built with [MkDocs](https://www.mkdocs.org/) and the
[mkdocs-shadcn](https://github.com/asiffer/mkdocs-shadcn) theme from the
`docs/` folder of the repository, and published to GitHub Pages at
<https://blip-box.github.io/sluggi/>.

## Deployment

Every push to `main` deploys the site: `.github/workflows/deploy-docs.yml`
builds it and publishes the result through GitHub Pages. There is no manual
deployment step, and `mkdocs gh-deploy` is not used.

## Preview locally

The docs build has its own dependencies, pinned in the workflow rather than
in `uv.lock`:

```bash
pip install mkdocs-shadcn==0.5.0 bottle==0.13.2 pymdown-extensions==10.14.3 pygments==2.19.1
cd docs && mkdocs serve
```

The configuration is
[`docs/mkdocs.yml`](https://github.com/blip-box/sluggi/blob/main/docs/mkdocs.yml).
