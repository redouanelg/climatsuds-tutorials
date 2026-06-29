# climatsuds-tutorials

Source notebooks and a content manifest for the **Learning** tab of the
[ClimatSuds portal](https://climatsuds.ird.fr). Everything in this repo is public.

## How it works

1. You add a Jupyter notebook (`.ipynb`) anywhere in this repo and an entry in
   [`tutorials.json`](tutorials.json).
2. On every push to `main`, a GitHub Actions workflow
   ([`.github/workflows/pages.yml`](.github/workflows/pages.yml)) runs
   `jupyter nbconvert` on every notebook and publishes the rendered HTML to
   **GitHub Pages**, preserving the folder structure, and copies `tutorials.json`
   to the site root:
   - `Data_Access/foo.ipynb` → `https://redouanelg.github.io/climatsuds-tutorials/Data_Access/foo.html`
3. The ClimatSuds front-end fetches `tutorials.json` at runtime and renders one
   card per entry (notebook viewer or Canal-U video). **No front-end change or
   redeploy is needed** when you add/remove content here.

Notebooks are **rendered, not executed** — CI shows the outputs you saved in the
notebook, so no data or credentials are ever needed.

## Add a notebook tutorial

1. Put the `.ipynb` anywhere in the repo (any folder, any depth, or the root).
   - Keep names simple: letters, digits, `-`, `_`. **No spaces or accents.**
   - Optionally add an "Open in Colab" badge inside the notebook itself.
2. Add an entry to `tutorials.json` whose `notebook` field is the file's path
   **relative to the repo root** (case-sensitive — `Data_Access` ≠ `data_access`):

   ```json
   {
     "id": "unique-slug",
     "type": "notebook",
     "tags": ["data-access", "era5", "reanalysis", "temperature", "global"],
     "lang": "en",
     "title": { "en": "English title", "fr": "Titre français" },
     "desc":  { "en": "One-line summary.", "fr": "Résumé en une ligne." },
     "notebook": "Folder/my_notebook.ipynb"
   }
   ```
3. Commit & push to `main`. Within ~1–2 min the card appears on the Learning tab.

## Tags (controlled vocabulary)

Tags are the **sidebar filters** on the Learning tab. **Notebooks** follow a
fixed scheme: **at most 5 tags**, each drawn from the vocabulary below, with
**exactly one `section`** tag (typically one per facet). **Guides** use up to 5
*free-form* topical tags (lowercase kebab-case, not this vocabulary). **Videos
carry no tags** — omit the field. CI runs
[`scripts/validate_tutorials.py`](scripts/validate_tutorials.py) and **fails the
build** if an entry breaks these rules.

| facet         | allowed values |
|---------------|----------------|
| `section`     | `data-access`, `getting-started`, `analysis`, `visualization`, `modeling` |
| `dataset`     | `era5`, `imerg`, `ghcn` |
| `source-type` | `reanalysis`, `satellite`, `station-observations` |
| `variable`    | `temperature`, `precipitation` |
| `region`      | `global`, `africa`, `europe`, `asia`, `americas`, `oceania`, `antarctica` |

Need a value that isn't listed (a new dataset, variable, region…)? Add it to
`VOCAB` in [`scripts/validate_tutorials.py`](scripts/validate_tutorials.py) in the
same commit, then use it. Check locally first: `python scripts/validate_tutorials.py`.

## Add a video tutorial (Canal-U)

Videos are not stored here — only referenced. On the Canal-U video page, open
**Partager → Intégrer** and copy the iframe **src** URL, then add an entry:

```json
{
  "id": "platform-overview",
  "type": "video",
  "lang": "fr",
  "title": { "en": "Platform overview", "fr": "Présentation de la plateforme" },
  "desc":  { "en": "A short tour.", "fr": "Une visite rapide." },
  "canalu": "https://www.canal-u.tv/.../embed"
}
```

## Add a guide (external link)

Guides are externally hosted pages (e.g. a Quarto site) — referenced, not stored.
Add an entry with the page `url` and up to 5 free-form topical tags:

```json
{
  "id": "hydro-climatic-modelling-workflow",
  "type": "guide",
  "tags": ["hydrology", "modelling", "bias-correction", "floods"],
  "lang": "en",
  "title": { "en": "English title", "fr": "Titre français" },
  "desc":  { "en": "One-line summary.", "fr": "Résumé en une ligne." },
  "url": "https://example.quarto.pub/my-guide/"
}
```

## Remove a tutorial

Delete its entry from `tutorials.json` and the card disappears. For notebooks,
also delete the `.ipynb` if you want to stop publishing its HTML.

## `tutorials.json` field reference

The file is a single object: `{ "tutorials": [ … ] }`.

| field            | applies to | notes |
|------------------|------------|-------|
| `id`             | all        | unique, stable slug |
| `type`           | all        | `"notebook"`, `"video"` or `"guide"` |
| `tags`           | notebooks, guides | notebooks: controlled vocabulary, one per facet (see [Tags](#tags-controlled-vocabulary)); guides: up to 5 free-form tags; videos: none |
| `lang`           | all        | `"en"` or `"fr"` (informational) |
| `title` / `desc` | all        | objects with `en` and `fr` keys (bilingual) |
| `notebook`       | notebooks  | path to the `.ipynb` relative to repo root |
| `canalu`         | videos     | Canal-U iframe embed URL |
| `url`            | guides     | link to the externally hosted guide (e.g. Quarto) |

`tutorials.json` is validated in CI by
[`scripts/validate_tutorials.py`](scripts/validate_tutorials.py) — malformed JSON,
missing fields, an out-of-vocabulary notebook tag, more than 5 tags, or a guide
without a `url` fail the build before anything is published.

## Where it shows up

- Pages site: https://redouanelg.github.io/climatsuds-tutorials/
- Manifest: https://redouanelg.github.io/climatsuds-tutorials/tutorials.json
- Front-end Learning tab: `/tutorials` on the ClimatSuds portal
