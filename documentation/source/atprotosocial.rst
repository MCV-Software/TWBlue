.. _atprotosocial_bluesky:

**************************************
ATProtoSocial (Bluesky) Integration
**************************************

TWBlue now supports the AT Protocol (ATProto), the decentralized social networking protocol that powers Bluesky. This allows you to interact with your Bluesky account directly within TWBlue.

Adding an ATProtoSocial Account
===============================

To connect your Bluesky account to TWBlue, you will need your user **handle** and an **App Password**.

1.  **User Handle**: This is your unique Bluesky identifier, often in the format ``@username.bsky.social`` or a custom domain you've configured (e.g., ``@yourname.com``).
2.  **App Password**: Bluesky uses App Passwords for third-party applications like TWBlue instead of your main account password. You need to generate an App Password from your Bluesky account settings.
    *   Go to Bluesky Settings (usually accessible from the Bluesky app or website).
    *   Navigate to the "App passwords" section (this might be under "Advanced" or "Security").
    *   Generate a new App Password. Give it a descriptive name (e.g., "TWBlue").
    *   Copy the generated App Password immediately. It will usually only be shown once.

Once you have your handle and the App Password:

1.  Open TWBlue and go to the Session Manager (Application Menu -> Manage accounts).
2.  Click on "New account".
3.  Select "ATProtoSocial (Bluesky)" from the menu.
4.  A dialog will prompt you to confirm that you want to authorize your account. Click "Yes".
5.  You will then be asked for your Bluesky Handle. Enter your full handle (e.g., ``@username.bsky.social`` or ``username.bsky.social``).
6.  Next, you will be asked for the App Password you generated. Enter it carefully.
7.  If the credentials are correct, TWBlue will log in to your Bluesky account, and the new session will be added to your accounts list.

Key Features
============

Once your ATProtoSocial account is connected, you can use the following features in TWBlue:

*   **Posting**: Create new posts (often called "skeets") with text, images, and specify language.
*   **Timelines**:
    *   **Home Timeline (Skyline)**: View posts from users you follow.
    *   **User Timelines**: View posts from specific users.
    *   **Mentions & Replies**: These will appear in your Notifications.
*   **Notifications**: Receive notifications for likes, reposts, follows, mentions, replies, and quotes.
*   **User Actions**:
    *   Follow and unfollow users.
    *   Mute and unmute users.
    *   Block and unblock users (blocking is done on your PDS/server).
*   **Quoting Posts**: Quote other users' posts when you create a new post.
*   **User Search**: Search for users by their handle or display name.
*   **Content Warnings**: Create posts with content warnings (sensitive content labels).

Basic Concepts for ATProtoSocial
==================================

*   **DID (Decentralized Identifier)**: A unique, permanent identifier for users and data on the AT Protocol. It doesn't change even if your handle does. You generally won't need to interact with DIDs directly in TWBlue, as handles are used more commonly.
*   **Handle**: Your user-facing address on Bluesky (e.g., ``@username.bsky.social``). This is what you use to log in with an App Password in TWBlue. Handles can be changed, but your DID remains the same.
*   **App Password**: A specific password you generate within your Bluesky account settings for use with third-party applications like TWBlue. This is more secure than using your main account password.
*   **PDS (Personal Data Server)**: Where your account data is stored on the AT Protocol network. Most users are on the main Bluesky PDS (bsky.social), but you could potentially use a different one. TWBlue will typically connect to the default Bluesky PDS.

Further details on specific actions can be found in the relevant sections of this documentation. As Bluesky and the AT Protocol evolve, TWBlue will aim to incorporate new features and refinements.
