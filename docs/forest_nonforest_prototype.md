## Forest / Non-Forest Notebook Prototype

This page links to the prototype notebook for running a forest/non-forest classification workflow with AlphaEarth embeddings and field labels.

## Open the Notebook

- **Notebook in GitHub repo**: [`docs/forest_nonforest_prototype.ipynb`](https://github.com/ulfboge/gold-standard/blob/main/docs/forest_nonforest_prototype.ipynb)
- **Open in Google Colab**: [Launch in Colab](https://colab.research.google.com/github/ulfboge/gold-standard/blob/main/docs/forest_nonforest_prototype.ipynb)

## Important Note

Google Colab opens notebooks from the **GitHub repository**, not from the GitHub Pages site itself.

The GitHub Pages site is still useful because it can provide a stable landing page with the Colab link, setup notes, and project documentation.

## Minimum Files for Manual Colab Upload

If you are not opening directly from GitHub, upload these into `/content/gold-standard/`:

- `docs/forest_nonforest_prototype.ipynb`
- `data/demo/forest_nonforest_training.geojson`

Optional:

- `data/incoming/project.gpkg` if you want the notebook to use a real `aoi` layer

## What the Notebook Produces

The notebook writes outputs under `output/forest_nonforest/`, including:

- a forest probability raster
- a binary forest/non-forest raster
- an optional forest polygons GeoPackage
- an accuracy summary
- a run report containing warnings and errors
