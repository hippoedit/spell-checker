# HippoEDIT Spell Checker

Canonical distribution repository for the HippoEDIT Spell Checker plugin.

Spell Checker is a normal HippoEDIT plugin that is bundled by default with the editor installer. It can be enabled/disabled independently and may be released independently while its editor compatibility contract permits.

## Current canonical release

The first canonical external release is `2.0.86`, bootstrapped from the exact SpellChecker binaries shipped in the accepted HippoEDIT 2.0.86 Unicode x86 and x64 installers.

The release ZIP is the binary distribution source of truth:

```text
spell-checker-2.0.86.zip
  package-info.xml
  x32u/SpellChecker.dll
  x64/SpellChecker.dll
```

The bootstrap verifies the published installer SHA-256 values, the extracted DLL SHA-256 values, plugin GUID `CE3B04B4-AD3F-4827-A629-4C5149C4DAA4`, and PE file/product version `2.0.86` before creating the Release.

The old website `1.0.2.4` package is historical and is not the source for the current release: its DLLs differ from the binaries shipped with HippoEDIT 2.0.86, and its PDB archives correspond to those old DLLs.

Future editor/installers and the website plugin publisher should consume or byte-verify the same versioned Spell Checker Release artifact rather than maintaining a website-local copy.
