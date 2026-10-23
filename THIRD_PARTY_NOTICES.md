# Third-party components

The C++ wrapper uses GNU libstdc++ / PBDS through its installed headers. Those libraries are not copied into this repository.

The documentation bundles **Mermaid 11.12.0**, distributed under the MIT license. Its unmodified bundle is in `assets/vendor/mermaid.min.js`; its license is retained in [assets/vendor/MERMAID-LICENSE.txt](assets/vendor/MERMAID-LICENSE.txt). [provenance.json](assets/vendor/provenance.json) records the source tarball, npm integrity value, and SHA-256 hashes.

Mermaid renders the diagrams; the project’s MIT license does not replace Mermaid’s license. Generated diagram sources and explanatory content are part of this project. The optional Python documentation dependency is installed separately using `requirements-dev.txt`.
