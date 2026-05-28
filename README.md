[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![Stable](https://img.shields.io/github/release/Wheemer/email_notifier.svg?style=for-the-badge)](https://github.com/Wheemer/email_notifier/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Wheemer/email_notifier/total.svg?style=for-the-badge)](https://github.com/Wheemer/email_notifier/releases)

# Home Assistant Email Notifier

**Sending email notifications from Home Assistant.**

The original project is based on Home Assistant's SMTP integration and adds a UI-based configuration flow for email notification accounts.

This fork keeps that behavior and allows SMTP authentication to be skipped for local relays or SMTP servers that do not require a username and password.

## Fork Changes

- Username and password are optional in the config UI and options UI.
- SMTP authentication is used only when both username and password are provided.
- When username or password is left blank, the SMTP client connects without calling `mail.login()`.
- Blank or incomplete username/password values are not saved in config entry data.
- YAML configuration can omit username and password for unauthenticated SMTP servers.
- The repository declares Home Assistant `2024.4.1` as the minimum supported version for HACS.
- GitHub Actions validate the repository with both HACS validation and Hassfest.

## Features

- Send Home Assistant alerts, notifications, and messages to email recipients.
- UI-based SMTP account configuration.
- Optional SMTP authentication for unauthenticated local relays.
- Backward compatibility with YAML configuration.
- Supports multiple recipients.
- Sends plain text or HTML messages.
- Supports inline images and file attachments, including local paths and remote URLs.
- Options flow to update configurations without reinstalling the integration.
- Detailed error handling and logging for troubleshooting.

## Compatibility

This fork is intended for Home Assistant `2024.4.1` or newer when installed through HACS. Repository validation runs with both the HACS validation action and Home Assistant Hassfest.

## Installation

### HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Wheemer&repository=email_notifier)

Add this repository as a custom HACS repository:

```text
https://github.com/Wheemer/email_notifier
```

Then install **Email Notifier** from HACS and restart Home Assistant.

### Manual

Download the latest release from [Wheemer/email_notifier/releases](https://github.com/Wheemer/email_notifier/releases), copy `custom_components/email_notifier` into `/config/custom_components/`, and restart Home Assistant.

## Configuration

In Home Assistant, go to _Settings_ > _Devices & services_, click _Add integration_, search for _email_, and select **Email Notifier**.

### Configuration Fields

#### SMTP Server
SMTP server used to send notifications.

#### Port (default: 587)
The SMTP server port.

#### Username
Optional username for the SMTP account. If both username and password are provided, the integration authenticates with the SMTP server.

#### Password
Optional password for the SMTP account. If either username or password is left blank, the integration connects without SMTP authentication.

#### Sender Email
Email address used as the sender.

#### Recipient Email(s)
Default recipient address, or a comma-delimited list of recipient addresses. Recipients supplied in a send action override this default.

#### Sender Name
Optional display name for the sender.

#### Encryption (default: starttls)
SMTP encryption mode: `starttls`, `tls`, or `none`.

#### Timeout (default: 15)
SMTP connection timeout in seconds.

## Google Mail

Google Mail requires SMTP authentication and an application-specific password. Fill in both username and password when using Gmail.

You may not be able to create an app password if:

- You do not have 2-step verification enabled on your account.
- You have 2-step verification enabled but have only added a security key as an authentication mechanism.
- Your Google account is enrolled in Google's Advanced Protection Program.
- Your Google account belongs to a Google Workspace that has disabled app passwords.

## Usage

The Email Notifier creates email account entities from which notifications can be sent. Each account has a default recipient list.

### Method A: Notify Action

In an automation, click _Add action_, choose _Notifications_, then select _Send a notification message_. Enter your message and choose one or more Email Notifier sender entities as the target.

```yaml
alias: Send Test Message
description: ""
triggers: []
conditions: []
actions:
  - action: notify.send_message
    data:
      message: "This is a test message from Home Assistant"
    target:
      entity_id: notify.email_notification_sender_1
mode: single
```

### Method B: Email Notifier Service

In an automation, click _Add action_, search for _email_, and select **Email Notifier: Send Email**. Choose the sender account and fill in optional fields such as recipients, subject, HTML, attachments, images, sender name, or reply-to address.

```yaml
alias: Send Test Message
description: ""
triggers: []
conditions: []
actions:
  - action: email_notifier.send
    metadata: {}
    data:
      account: notify.email_notification_sender_0
      recipients: "user@example.com"
      title: "Complete Feature Demo"
      message: "Plain text version of this email"
      html: |
        <html>
          <body>
            <h1 style="color: #0066cc;">Feature Demonstration</h1>
            <p>This email showcases all features:</p>
            <img src="cid:logo.png" width="200"/>
            <ul>
              <li>HTML formatting</li>
              <li>Inline images</li>
              <li>File attachments</li>
              <li>Custom sender info</li>
            </ul>
          </body>
        </html>
      images: |
        https://example.com/logo.png
      attachments: |
        /config/www/report.pdf
        https://example.com/document.pdf
      from_address: "noreply@mydomain.com"
      sender_name: "Home Assistant Demo"
      reply_to: "support@mydomain.com"
```

## HTML Email

HTML emails are sent as multipart MIME with both plain text and HTML versions. Email clients display the HTML version when supported and fall back to plain text otherwise.

```yaml
service: email_notifier.send
data:
  account: notify.email_notification_sender_0
  title: "Alert Notification"
  message: "Plain text fallback"
  html: |
    <html>
      <body>
        <h1 style="color: blue;">Alert</h1>
        <p>This is a <strong>rich HTML</strong> email with formatting.</p>
      </body>
    </html>
  recipients: "user@example.com"
```

## Attachments And Images

Attachments and inline images support both local file paths and remote `http://` or `https://` URLs. Enter one file path or URL per line. Empty lines are ignored and whitespace is trimmed.

```yaml
service: email_notifier.send
data:
  account: notify.email_notification_sender_0
  title: "Camera Alert"
  message: "Motion detected at front door"
  html: |
    <html>
      <body>
        <h1>Motion Detected</h1>
        <img src="cid:camera.jpg" width="600"/>
      </body>
    </html>
  images: |
    /config/www/camera.jpg
    https://example.com/logo.png
  attachments: |
    /config/www/report.pdf
    https://example.com/document.pdf
  recipients: "user@example.com"
```

## Custom Sender Fields

You can override sender details for a single message without changing the configured SMTP account.

```yaml
service: email_notifier.send
data:
  account: notify.email_notification_sender_0
  title: "Security Alert"
  message: "Motion detected at front door"
  from_address: "security@mydomain.com"
  sender_name: "Home Security System"
  reply_to: "support@mydomain.com"
  recipients: "user@example.com"
```

When `sender_name` and `from_address` are both supplied, the displayed sender is formatted like `Home Security System <security@mydomain.com>`.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## License

This integration is published under the GNU General Public License v3.0.

## Attribution

This fork is based on [microteq/email_notifier](https://github.com/microteq/email_notifier) by [@microteq](https://github.com/microteq). Email Notifier is based on the Home Assistant SMTP integration. Thanks also to onoffautomations for adding HTML, attachment, image, and custom sender features upstream.
