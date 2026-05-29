# Changelog

## 0.1.6 - 2026-05-28

### Added
- Added a `verify_ssl` option to the config flow and options flow for SMTP servers with self-signed or otherwise untrusted certificates.
- Added YAML support for `verify_ssl`.

### Fixed
- Made the Email Notifier service account selector target `notify` entities from this integration so the Home Assistant UI can populate the account dropdown more reliably.
- Service calls now raise a Home Assistant error when SMTP delivery still fails after retries instead of only logging the retry attempts.
- Per-message `sender_name` overrides now work even when `from_address` is not also supplied.

## 0.1.5 - 2026-05-28

### Fixed
- Fixed the config UI validation error that showed `expected str` when username or password was left blank.
- Optional SMTP credential fields now default to empty strings in the form and are removed from saved config unless both are filled.
- Removed the old upstream email placeholder from the config flow title placeholders.

## 0.1.4 - 2026-05-28

### Changed
- Updated the integration codeowner metadata to list only `@Wheemer` for this fork.

## 0.1.3 - 2026-05-28

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
