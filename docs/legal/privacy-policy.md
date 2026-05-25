# Privacy Policy — Sách Thì Thầm Uploader

**Last updated:** 2026-05-25
**Contact:** sang@konek.vn

## Overview

Sách Thì Thầm Uploader ("the App") is a personal command-line automation tool used by a single creator to upload pre-produced Vietnamese audiobook video episodes to the TikTok account of the "Sách Thì Thầm" channel via TikTok's Content Posting API. This Privacy Policy explains what limited data the App handles and how.

## Data the App handles

The App handles only the minimum data required to authenticate with TikTok and post videos:

1. **TikTok OAuth tokens** (access token and refresh token) — issued by TikTok after the creator consents to authorize the App. These tokens are stored exclusively in a local JSON file on the creator's own personal computer. They are never transmitted to any server other than TikTok's official API endpoints.

2. **The creator's `open_id`** — a non-personally-identifying TikTok user identifier returned by TikTok at authorization time. Used only to verify that the App is acting on the intended creator account. Stored locally in the same JSON file.

3. **Video files** prepared by the creator for upload — read from the creator's local disk and transmitted directly to TikTok via the Content Posting API. The App does not retain, copy, share, or analyze these files beyond what is required to perform the upload.

## Data the App does NOT collect

- The App does not collect any data about TikTok end-users, followers, viewers, or third parties.
- The App does not collect, store, or transmit analytics, telemetry, behavioural data, or device fingerprints.
- The App does not request any social-graph scopes (`user.info.profile`, `user.info.stats`, follower lists, etc.).
- The App does not use third-party advertising, tracking pixels, or marketing services.

## Data sharing

The App does not share any data with any third party. The only network destinations the App contacts are TikTok's own official API endpoints (`open.tiktokapis.com`, `www.tiktok.com`) for authentication and content posting.

## Data retention

OAuth tokens are retained on the creator's local computer until the creator revokes them (by deleting the local token file or revoking the App's access in TikTok's app-management settings). No copies are retained elsewhere.

## Security

OAuth tokens are stored in a local JSON file inside the App's working directory. The file is marked as ignored by version control. Access is protected by the security of the creator's local operating system account.

## Children's privacy

The App is intended for use by a single adult creator. The App does not knowingly collect data from anyone under 18.

## Changes to this policy

Any changes to this policy will be reflected on this page with an updated "Last updated" date.

## Contact

For any questions about this policy, contact sang@konek.vn.
