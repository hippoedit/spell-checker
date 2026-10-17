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

## Bootstrap exception

`v2.0.86` was a one-time bootstrap from already accepted HippoEDIT 2.0.86 Unicode x86/x64 installers. That reverse dependency is historical only. Future releases establish the plugin artifact before or as part of installer assembly.
