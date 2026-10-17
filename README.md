# HippoEDIT Spell Checker

Canonical distribution repository for the HippoEDIT Spell Checker plugin.

Spell Checker is a normal HippoEDIT plugin that is bundled by default with the editor installer. Its plugin version and release lifecycle are independent from the editor version when compatibility permits.

## Distribution

Versioned GitHub Releases own the canonical binary distribution. Each release publishes one ZIP named `spell-checker-<version>.zip` containing:

- `package-info.xml`
- `x32/SpellChecker.dll` and optional PDB archive
- `x32u/SpellChecker.dll` and optional PDB archive
- `x64/SpellChecker.dll` and optional PDB archive

The HippoEDIT installer and website plugin publisher should consume or byte-verify against the same release artifact.

The initial `1.0.2.4` release is bootstrapped byte-for-byte from the legacy website payload anchored at `hippoedit/website@1fcab5602e8f06bfd3c87d5ea7a441956f74c8ee`.
