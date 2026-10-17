# Spell Checker release process

`hippoedit/spell-checker` owns the distributable Spell Checker plugin artifact. Editor source/build ownership may live elsewhere; this repository owns the versioned binary release contract.

## Inputs

A release uses:

- `package-info.xml` from this repository;
- the x32 Unicode `SpellChecker.dll` produced by the editor build;
- the x64 `SpellChecker.dll` produced by the editor build.

The plugin ID is stable. The plugin `<version>` is independent from the HippoEDIT editor version. `<required>` is the minimum compatible editor version and does not need to equal the plugin version.

## Build the canonical artifact

Update `package-info.xml` first when the plugin version or minimum editor requirement changes, then run:

```bash
python3 tools/package_release.py \
  --x32u path/to/x32u/SpellChecker.dll \
  --x64 path/to/x64/SpellChecker.dll \
  --output-dir dist
```

The command fails unless both DLLs:

- are PE files (`MZ`);
- contain the stable Spell Checker plugin GUID;
- expose `FileVersion` equal to the manifest plugin version;
- expose `ProductVersion` equal to the manifest plugin version.

It also requires the manifest to install exactly the current canonical binary paths:

```text
x32u/SpellChecker.dll
x64/SpellChecker.dll
```

The output is `dist/spell-checker-<version>.zip` containing `package-info.xml` and those two DLLs. ZIP member ordering, timestamps and storage mode are fixed so identical inputs produce identical bytes and SHA-256.

## Publish

Publish the generated ZIP as the single binary asset of tag `v<version>`. Record the SHA-256 printed by the packager.

After publication:

1. download the Release asset and verify its SHA-256;
2. make installer assembly consume the release payload, or compare the installer-bound DLL SHA-256 values to the release members and fail on mismatch;
3. pin the same tag, asset name and SHA-256 in `hippoedit/website/config/resource-sources.json`;
4. run the standard complete plugin publisher;
5. verify live plugin discovery/download.

Do not rebuild or repackage a published tag with different bytes. If the plugin payload changes, advance the plugin version and create a new release.

## Current editor product-release boundary

The website already automates the downstream publication of accepted editor installers through `hippoedit/website/.github/workflows/product-release-publish.yml` (`Publish Product Release`). That workflow starts from two prerequisites that already exist:

- a GitHub Release tag in `hippoedit/website` containing the installer assets named by the active product-release contract;
- matching version, artifact names, sizes and SHA-256 values in `hippoedit/website/config/product-release.json`.

It then verifies installer size/SHA-256 and PE version, uploads the accepted x32 Unicode/x64 installers to their stable production download paths, and smoke-checks the public URLs.

This is **not yet the whole editor release pipeline**. The current website workflow does not build the editor or installers, decide whether Spell Checker changed, create the canonical Spell Checker Release, make installer assembly consume that artifact, update the website product/plugin registries, or create the website GitHub Release that `Publish Product Release` consumes. Those are the upstream integration steps that still need to be connected in the editor build repository.

## Target end-to-end editor release flow

When the editor build repository becomes available, extend its existing release process rather than creating a parallel release system. The target flow is:

1. **Build editor and plugin outputs.** Produce the release-candidate x32 Unicode/x64 editor binaries and the corresponding Spell Checker DLLs from the same accepted build inputs.
2. **Determine whether Spell Checker changed.** Compare the produced plugin payload with the currently pinned canonical Spell Checker Release. Editor-version changes alone do not require a new plugin version or release.
3. **Create the plugin artifact only when needed.** If the Spell Checker payload changed, update `package-info.xml` as required, run `tools/package_release.py`, create immutable `hippoedit/spell-checker@v<plugin-version>`, and download/verify the release asset. If the payload is byte-identical and still compatible, reuse the existing plugin release.
4. **Bind installer assembly to the canonical plugin artifact.** Prefer assembling the installer from the downloaded canonical ZIP members. If the existing build layout makes that impractical, byte-verify the installer-bound DLLs against the canonical Release and fail the build on any mismatch.
5. **Build the final editor installers.** Produce the accepted Unicode x86/x64 installers, validate their PE/product version, size and SHA-256, and preserve those exact bytes as release inputs.
6. **Prepare website product release state.** Update `hippoedit/website/config/product-release.json` for the new editor release and create the corresponding website GitHub Release containing the exact installer assets expected by that contract.
7. **Prepare website plugin state when Spell Checker changed.** Update `hippoedit/website/config/resource-sources.json` to pin the new Spell Checker tag/asset/SHA-256. If Spell Checker did not change, leave the existing pin untouched.
8. **Run repository verification.** Require editor/build verification plus exact-head CI for every modified owner repository before production publication.
9. **Publish plugins when needed.** If the Spell Checker pin changed, run the existing standard complete plugin publisher. Do not add a SpellChecker-specific website publisher.
10. **Publish the editor release.** Dispatch the existing website `Publish Product Release` workflow with the prepared release tag. It remains the owner of installer upload to stable production paths and public installer smoke checks.
11. **Verify live state.** Confirm stable installer URLs, editor update metadata/redirects, and—when changed—the live Spell Checker discovery/download path.
12. **Record anchored evidence.** Keep the editor commit/release version, Spell Checker tag/SHA-256 when applicable, website commit, workflow run IDs and resulting public checks as the release evidence set.

The orchestration may eventually be a single editor-side release workflow, but ownership must remain distributed: the editor build owns build outputs, `hippoedit/spell-checker` owns the plugin artifact, and `hippoedit/website` owns public product/plugin publication state.

## Automation invariants

Future automation must preserve these rules:

- do not publish a new Spell Checker release merely because the editor version changed;
- never maintain another website-local Spell Checker DLL/PDB snapshot;
- never publish different bytes under an existing Spell Checker tag;
- never let installer-bound Spell Checker bytes diverge from the canonical plugin Release;
- do not duplicate `tools/package_release.py` logic in the editor or website repositories;
- do not replace `Publish Product Release` or the standard plugin publisher with editor-specific FTP/publication code;
- pin every cross-repository artifact with an immutable tag/asset and SHA-256;
- fail before production publication if any owner repository, digest or binary-version gate disagrees.

## Codex handoff

`docs/codex-editor-integration.md` is the execution brief for the future editor-repository integration. Give that document to Codex when the editor build repository is available. Codex must first inspect the repository's existing build/release orchestration and extend the current owner flow rather than inventing a second one.

## Bootstrap exception

`v2.0.86` was a one-time bootstrap from already accepted HippoEDIT 2.0.86 Unicode x86/x64 installers. That reverse dependency is historical only. Future releases establish the plugin artifact before or as part of installer assembly.
