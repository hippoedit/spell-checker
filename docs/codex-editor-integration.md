# Codex brief: integrate Spell Checker into the HippoEDIT editor release pipeline

Use this document when the HippoEDIT editor/build repository is available to Codex. The goal is to connect the existing editor release process to the canonical Spell Checker artifact and the existing website publication workflows without creating parallel release systems.

## Objective

Automate the release path end-to-end so one accepted editor release can, when appropriate:

1. build the editor and Spell Checker binaries;
2. create or reuse the canonical Spell Checker Release;
3. bind the installer to exactly those plugin bytes;
4. create the final editor installers;
5. update the website product/plugin release contracts;
6. run the existing website plugin publisher when needed;
7. run the existing website `Publish Product Release` workflow;
8. verify public installer/update/plugin state.

The result must preserve repository ownership boundaries and immutable artifact provenance.

## Canonical owners

Treat these as separate SSoTs:

- **Editor/build repository** — editor source, Spell Checker source/build, installer assembly and editor release orchestration.
- **`hippoedit/spell-checker`** — versioned distributable Spell Checker artifact. `tools/package_release.py` is the canonical packager/validator.
- **`hippoedit/website/config/product-release.json`** — website product-release routing/integrity contract for accepted installers.
- **`hippoedit/website/config/resource-sources.json`** — website-side routing registry for canonical plugin inputs.
- **`hippoedit/website/.github/workflows/product-release-publish.yml`** — existing downstream publisher for accepted editor installers.
- **`hippoedit/website/.github/workflows/plugins-publish.yml`** — existing complete plugin publisher.

Do not move ownership between these repositories merely to make orchestration easier.

## Current known state

Spell Checker publication is already unified with the normal plugin pipeline:

- canonical repository: `hippoedit/spell-checker`;
- current canonical release: `v2.0.86`;
- current asset: `spell-checker-2.0.86.zip`;
- current SHA-256: `0e1a5b2ea5b1e70cf17b8f3eb73cb008e621aa9cd3e5ac680cf9d737d2b3dd34`;
- stable plugin ID: `CE3B04B4-AD3F-4827-A629-4C5149C4DAA4`;
- canonical payload paths: `x32u/SpellChecker.dll`, `x64/SpellChecker.dll`.

`hippoedit/website` no longer contains a Spell Checker DLL/PDB snapshot.

The website already has a downstream editor installer publication workflow. `Publish Product Release` expects a website GitHub Release tag with installer assets plus matching `config/product-release.json`, validates size/SHA-256/PE version, uploads stable production installers and smoke-checks their URLs. Do not replace this workflow.

## Before changing anything

Repository-first verification is mandatory.

1. Identify the current editor repository, default/release branch, exact HEAD and existing release/build workflows.
2. Locate:
   - editor version source;
   - x32 Unicode/x64 build targets;
   - Spell Checker project/build outputs;
   - installer project/scripts;
   - current release/tag creation logic;
   - any existing upload/deployment/website update automation.
3. Determine whether an existing editor release workflow already creates GitHub releases or updates `hippoedit/website`. Extend it if present; do not add a second independent release pipeline.
4. Verify current `hippoedit/spell-checker/main`, its latest Release, `package-info.xml`, `tools/package_release.py` and CI.
5. Verify current `hippoedit/website/main`, `config/product-release.json`, `config/resource-sources.json`, `product-release-publish.yml` and `plugins-publish.yml`.
6. Anchor every plan and change to exact commit SHAs/tags. Never use historical chat state as current repository truth.

## Required integration behavior

### 1. Build once

Use the editor's accepted release build to produce the editor/installer inputs and Spell Checker DLLs. Do not rebuild Spell Checker independently later just for publication.

The x32 Unicode and x64 DLLs passed to the canonical packager must be the same binaries intended for installer assembly.

### 2. Decide whether Spell Checker needs a release

Do **not** couple plugin version to editor version.

Compare the release-candidate Spell Checker payload with the currently canonical plugin release. The exact implementation may use member SHA-256 values or another byte-exact comparison.

- If both variants are byte-identical and the existing compatibility contract remains valid, reuse the current Spell Checker tag and website pin.
- If either binary changes, or the compatibility contract must change, create a new plugin release.

Never create a no-op plugin release just because HippoEDIT itself received a new version.

### 3. Create the canonical Spell Checker artifact

When a new plugin release is required:

1. update `hippoedit/spell-checker/package-info.xml` with the new plugin `<version>` and correct minimum editor `<required>` value;
2. run the canonical command from that repository:

```bash
python3 tools/package_release.py \
  --x32u <editor-build-x32u>/SpellChecker.dll \
  --x64 <editor-build-x64>/SpellChecker.dll \
  --output-dir dist
```

3. require the packager to pass GUID/version/path validation;
4. publish `dist/spell-checker-<plugin-version>.zip` as the single binary asset of immutable tag `v<plugin-version>`;
5. download that Release asset again and verify its SHA-256 against the locally produced artifact;
6. record tag, asset name, release commit and SHA-256 for downstream consumers.

Do not copy the packager into the editor repository. Invoke/use the canonical owner implementation.

### 4. Bind installer assembly to the plugin Release

Preferred implementation: installer assembly downloads/extracts the newly created or reused canonical Spell Checker Release and consumes `x32u/SpellChecker.dll` / `x64/SpellChecker.dll` from it.

If current build tooling requires the local editor build outputs instead, enforce byte identity before installer creation:

- calculate SHA-256 of both local installer-bound DLLs;
- calculate SHA-256 of both members from the canonical Release;
- fail unless they match exactly.

There must be no successful release path where the installer ships plugin bytes different from the independently installable plugin artifact.

### 5. Build and freeze editor installers

Build the final Unicode x86/x64 installers after the Spell Checker artifact decision/binding is complete.

For each final installer record at least:

- filename;
- exact editor version;
- size in bytes;
- SHA-256;
- relevant PE/version verification result.

These exact bytes become the inputs to the existing website product-release publication stage.

### 6. Prepare `hippoedit/website`

Update `config/product-release.json` with the new editor release state and exact installer integrity metadata using the current schema and routing model. Do not redesign the product-release registry as part of this integration.

Create the website GitHub Release/tag expected by `Publish Product Release` and attach exactly the installer files referenced by the active product-release contract.

If—and only if—a new Spell Checker release was created, update `config/resource-sources.json` to pin:

- `repository: hippoedit/spell-checker`;
- new immutable `ref/tag`;
- exact asset name;
- exact SHA-256.

If Spell Checker did not change, leave this registry entry unchanged.

### 7. Verification and publication order

Use this order unless current repository evidence proves an existing owner workflow requires a safer equivalent order:

1. editor build/tests and installer verification GREEN;
2. new Spell Checker artifact/Release verified, if changed;
3. installer-bound plugin bytes verified against the canonical Release;
4. website config changes committed and exact-head website CI GREEN;
5. standard complete plugin publisher GREEN and live plugin download verified, if Spell Checker changed;
6. existing website `Publish Product Release` workflow GREEN;
7. stable public installer URLs GREEN;
8. editor update metadata/redirect behavior verified for the new release;
9. record release evidence with exact SHAs/tags/workflow run IDs.

Production publication must not start if any earlier ownership/integrity gate is red.

## Expected implementation shape

Prefer the smallest integration into the editor's existing release orchestration. A good implementation usually consists of:

- one editor-side orchestration step/script that decides whether the plugin changed and calls the canonical Spell Checker packaging/release contract;
- one installer-binding verification/consume step;
- one website-update step that writes exact product/plugin pins from produced artifact metadata;
- calls/dispatches to the existing website publication workflows;
- explicit output metadata passed between stages instead of scraping logs.

If the editor repo already has release manifest/output metadata, extend it rather than inventing another manifest.

## Do not do these things

- Do not restore `download/plugins/spell_checker/**` in `hippoedit/website`.
- Do not create a SpellChecker-specific website publisher.
- Do not duplicate `tools/package_release.py` in another repository.
- Do not make the plugin version automatically equal the editor version.
- Do not mutate/re-upload an existing released tag with different bytes.
- Do not package different plugin bytes for installer and independent plugin update.
- Do not upload installers directly to FTP from a new editor workflow if the existing website `Publish Product Release` can own that step.
- Do not hardcode plugin counts or special-case Spell Checker in the website plugin publisher.
- Do not treat an old installer, old website snapshot or chat summary as current SSoT when repository/release evidence is available.

## Acceptance criteria

The integration is complete only when a dry-run or real release candidate proves both branches:

**Spell Checker unchanged**

- editor release succeeds without creating a new plugin release;
- installer contains bytes identical to the existing canonical plugin Release;
- `resource-sources.json` remains unchanged;
- editor product release publishes through the existing website flow.

**Spell Checker changed**

- a new immutable canonical plugin Release is created from the accepted editor build outputs;
- installer consumes or byte-verifies that exact artifact;
- website pins the new tag/asset/SHA-256;
- standard plugin publisher publishes it successfully;
- editor installers publish successfully through `Publish Product Release`;
- public plugin and installer checks both succeed.

All success claims must be backed by fresh exact-head CI/workflow evidence.

## Relevant documentation

- `hippoedit/spell-checker/docs/release.md`
- `hippoedit/spell-checker/package-info.xml`
- `hippoedit/spell-checker/tools/package_release.py`
- `hippoedit/website/docs/plugin-publication.md`
- `hippoedit/website/config/resource-sources.json`
- `hippoedit/website/config/product-release.json`
- `hippoedit/website/.github/workflows/plugins-publish.yml`
- `hippoedit/website/.github/workflows/product-release-publish.yml`
