# Google Photos Plugin for Elodie

[![Build Status](https://travis-ci.org/jmathai/elodie.svg?branch=master)](https://travis-ci.org/jmathai/elodie) [![Coverage Status](https://coveralls.io/repos/github/jmathai/elodie/badge.svg?branch=master)](https://coveralls.io/github/jmathai/elodie?branch=master) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/jmathai/elodie/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/jmathai/elodie/?branch=master)

This plugin uploads all photos imported using Elodie to Google Photos. It was created after [Google Photos and Google Drive synchronization was deprecated](https://www.blog.google/products/photos/simplifying-google-photos-and-google-drive/). It aims to replicate my [workflow using Google Photos, Google Drive and Elodie](https://artplusmarketing.com/one-year-of-using-an-automated-photo-organization-and-archiving-workflow-89cf9ad7bddf).

I didn't intend on it, but it turned out that with this plugin you can use Google Photos with Google Drive, iCloud Drive, Dropbox or no cloud storage service while still using Google Photos for viewing and experiencing your photo library.

The hardest part of using this plugin is setting it up. Let's get started.

# Installation and Setup

## Google Photos
Let's start by making sure you have a Google Photos account. If you don't, you should start by [creating your Google Photos account](https://photos.google.com/login).

## Google APIs
Once you've got your Google Photos account created we can enable Google Photos' APIs for your account.

In order to enable Google APIs you need what's called a project. Don't worry about what it is, just create one so you can enable the Google Photos API for it.
1. Go to [Google's developer console](https://console.developers.google.com).
2. If you have a project already then you can skip this step.
   
    If you don't already have a project or would like to create one just for this purpose then you should create it now. In the top bar there's a **project selector** which will open a dialog with a button to create a new project.
3. Now you'll need to [enable the Google Photos API for your project](https://console.developers.google.com/apis/library/photoslibrary.googleapis.com). You should be able to follow that link and click the **Enable API** button. Make sure the project from the prior step is selected.
4. Once you've enabled the Google Photos API you will need to [create an OAuth client ID](https://console.developers.google.com/apis/credentials).
    1. Select **other** as the type of client.
    2. Set up a consent screen if needed. Only you'll be seeing this so put whatever you want into the required fields. Most everything can be left blank.
    3. Download the credentials when prompted or click the download icon on the [credentials page](https://console.developers.google.com/apis/credentials).

## Configure the Google Photos Plugin for Elodie
Now that you're set up with your Google Photos account, have enabled the APIs and configured your OAuth client we're ready to enable this plugin for Elodie.

1. Move the credentials file you downloaded to a permanent location and update your `config.ini` file. You'll need to add a `[Plugins]` section.

          [Plugins]
          plugins=GooglePhotos
        
          [PluginGooglePhotos]
          secrets_file=/full/path/to/saved/secrets_file.json
          auth_file=/full/path/to/save/auth_file.json

    I put `secrets_file.json` (the one you downloaded) in my `~/.elodie` directory. `auth_file.json` will be automatically created so make sure the path is writable by the user running `./elodie.py`.
2. If you did everything exactly correct you should be able to authenticate Elodie to start uploading to Google Photos.
    1. Start by importing a new photo by running `./elodie.py import`.
    2. Run `./elodie.py batch` which should open your browser.
    3. Login and tell Google Photos to allow Elodie the requested permissions to your Google Photos account.
    4. At some point you'll likely see a scary warning screen. This is because your OAuth client is not approved but go ahead and click on **Advanced** and **Go to {Your OAuth client name (unsafe)**.
    5. Return to your terminal and close your browser tab if you'd like.

Assuming you did not see any errors you can go back to your browser and load up Google Photos. If your photos show up in Google Photos then you got everything to work *a lot* easier than I did.

## Automating It All
I'm not going to go into how you can automate this process but much of it is covered by various blog posts I've done in the past.

* [Understanding My Need for an Automated Photo Workflow](https://medium.com/vantage/understanding-my-need-for-an-automated-photo-workflow-a2ff95b46f8f#.dmwyjlc57)
* [Introducing Elodie; Your Personal EXIF-based Photo and Video Assistant](https://medium.com/@jmathai/introducing-elodie-your-personal-exif-based-photo-and-video-assistant-d92868f302ec)
* [My Automated Photo Workflow using Google Photos and Elodie](https://medium.com/swlh/my-automated-photo-workflow-using-google-photos-and-elodie-afb753b8c724)
* [One Year of Using an Automated Photo Organization and Archiving Workflow](https://artplusmarketing.com/one-year-of-using-an-automated-photo-organization-and-archiving-workflow-89cf9ad7bddf)

## Credits
Elodie is an open source project with many [contributors](https://github.com/jmathai/elodie/graphs/contributors) and [users](https://github.com/jmathai/elodie/stargazers) who have reported lots of [bugs and feature requests](https://github.com/jmathai/elodie/issues?utf8=%E2%9C%93&q=).

Google Photos is an amazing product. Kudos to the team for making it so magical.
