# Acknowledgements

SpectraMatrix was built as an original local workbench for spectral modeling experiments. During planning and design, we studied several open-source projects and documentation resources for architecture, workflow, and repository-structure ideas.

This file is intended to make those influences visible and to keep the public repository transparent.

## Architecture And Workflow References

- [lightning-hydra-template](https://github.com/ashleve/lightning-hydra-template)
  - License: MIT License, copyright (c) 2021 ashleve.
  - What we learned from it: experiment configuration discipline, reproducible ML project layout, task-oriented training workflows, and separation between source code, configs, logs, and generated artifacts.
  - SpectraMatrix does not include copied Lightning-Hydra-Template source code.

- [bulletproof-react](https://github.com/alan2207/bulletproof-react)
  - License: MIT License, copyright (c) 2024 Alan Alickovic.
  - What we learned from it: frontend project organization, feature-oriented structure, and application-level maintainability practices.
  - SpectraMatrix does not include copied Bulletproof React source code.

- [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
  - License: MIT License, copyright (c) 2019 Sebastián Ramírez.
  - What we learned from it: FastAPI application structure, local API ergonomics, and full-stack project conventions.
  - SpectraMatrix does not include copied Full Stack FastAPI Template source code.

  

## Runtime Dependencies And Vendored Assets

SpectraMatrix depends on or interoperates with common open-source tools and libraries, including Python, FastAPI, Uvicorn, NumPy, PyTorch, and Swift tooling on macOS.

The local browser workbench vendors UI assets so it can run offline in lab environments:

- Tabler Core CSS, MIT License.
- Tabler Icons webfont, MIT License.

See:

```text
packages/spectral_core/src/spectral_core/api/static/vendor/README.md
```

## License Notes

SpectraMatrix itself is released under the MIT License. See `LICENSE`.

The references above are acknowledged as design and learning references. If future development copies source code, configuration files, documentation text, or assets from a third-party project, the copied material should retain the original copyright and license notices according to that project's license.
