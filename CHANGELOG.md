# Changelog

## Unreleased

### Changed
- Made SMTP username and password optional in the config UI, options UI, and YAML configuration.
- SMTP authentication now runs only when both username and password are provided.
- Blank or incomplete SMTP credentials are removed from saved config data.
- Updated HACS metadata with a minimum Home Assistant version of 2024.4.1.
- Updated GitHub Actions validation to run both HACS validation and Hassfest.
- Updated manifest documentation and issue tracker links for the Wheemer fork.

### Fixed
- Fixed service unload to remove `email_notifier.send` instead of the old `send_email` name.
- Avoid duplicate service registration during setup.
- Removed the SMTP connection probe from entity setup so Home Assistant startup is not blocked by a temporarily unavailable SMTP server.
- Cleaned up mutable default arguments and local attachment path handling in the SMTP API.

### Documentation
- Updated README installation links, badges, fork attribution, and optional SMTP credential behavior.
