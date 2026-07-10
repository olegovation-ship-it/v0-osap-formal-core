# Upload instructions for the existing GitHub repository

GitHub does not unpack a ZIP uploaded as a repository file.

1. Extract `V0_OSAP_v1_2_Repository_Bootstrap_Package.zip` on a computer or in a file manager.
2. Open the extracted folder.
3. Upload **its contents**, not the enclosing folder and not the ZIP itself, to the root of `olegovation-ship-it/v0-osap-formal-core`.
4. Allow replacement of `README.md`, `.gitignore`, and `LICENSE` with the bootstrap versions.
5. Use the commit message:

```text
Bootstrap V0 OSAP v1.2 formal core, schemas, checker, and proof skeletons
```

6. Open the **Actions** tab and confirm five workflows appear.
7. Do not create a release or Zenodo deposit until all required workflows pass.
