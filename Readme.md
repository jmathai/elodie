# Hello, I'm Elodie
~~ *Your Personal EXIF-based Photo, Video and Audio Assistant* ~~

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/jmathai/elodie/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/jmathai/elodie/tree/master) [![Coverage Status](https://coveralls.io/repos/github/jmathai/elodie/badge.svg?branch=master)](https://coveralls.io/github/jmathai/elodie?branch=master) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/jmathai/elodie/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/jmathai/elodie/?branch=master)

<p align="center"><img src ="https://jmathai.s3.amazonaws.com/github/elodie/elodie-folder-anim.gif" /></p>

## Quickstart guide

Getting started takes just a few minutes.

### Install ExifTool

Elodie relies on the great [ExifTool library by Phil Harvey](http://www.sno.phy.queensu.ca/~phil/exiftool/). You'll need to install it for your platform.

Some features for video files will only work with newer versions of ExifTool and have been tested on version 10.20 or higher. Support for HEIC files requires version 11.50 or higher. Check your version by typing `exiftool -ver` and see the [manual installation instructions for ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/install.html#Unix) if needed.

```
# OSX (uses homebrew, http://brew.sh/)
brew install exiftool

# Debian / Ubuntu
apt-get install libimage-exiftool-perl

# Fedora / Redhat
dnf install perl-Image-ExifTool

# Windows users can install the binary
# http://www.sno.phy.queensu.ca/~phil/exiftool/install.html
```

### Clone the Elodie repository

You can clone Elodie from GitHub. You'll need `git` installed ([instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)).

```
git clone https://github.com/jmathai/elodie.git
cd elodie
pip install -r requirements.txt
```

### Give Elodie a test drive

Now that you've got the minimum dependencies installed you can start using Elodie. You'll need a photo, video or audio file and a folder you'd like Elodie to organize them into.

```
# Run these commands from the root of the repository you just cloned.
./elodie.py import --debug --destination="/where/i/want/my/photos/to/go" /where/my/photo/is.jpg
```

You'll notice that the photo was organized into an *Unknown Location* folder. That's because you haven't set up your MapQuest API ([instructions](#using-openstreetmap-data-from-mapquest)).

Now you're ready to learn more about Elodie.

<p align="center"><img src ="creative/logo@300x.png" /></p>

## Slowstart guide

[Read a 3 part blog post on why I was created](https://medium.com/vantage/understanding-my-need-for-an-automated-photo-workflow-a2ff95b46f8f#.dmwyjlc57) and how [I can be used with Google Photos](https://medium.com/@jmathai/my-automated-photo-workflow-using-google-photos-and-elodie-afb753b8c724).

I work tirelessly to make sure your photos are always sorted and organized so you can focus on more important things. By photos I mean JPEG, DNG, NEF and common video and audio files.

You don't love me yet but you will.

I only do 3 things.

* Firstly I organize your existing collection of photos into a customizable folder structure.
* Second I help make it easy for all the photos you haven't taken yet to flow into the exact location they belong.
* Third but not least I promise to do all this without a yucky propietary database that some friends of mine use.

*NOTE: make sure you've installed everything I need before running the commands below. [Instructions](#quickstart-guide) at the top of this page.*

## Let's organize your existing photos

My guess is you've got quite a few photos scattered around. The first thing I'll help you do is to get those photos organized. It doesn't matter if you have hundreds, thousands or tens of thousands of photos; the more the merrier.

Fire up your terminal and run this command which *__copies__* your photos into something a bit more structured.

```
./elodie.py import --destination="/where/i/want/my/photos/to/go" /where/my/photos/are
```

I'm pretty fast but depending on how many photos you have you might want to grab a snack. When you run this command I'll `print` out my work as I go along. If you're bored you can open `/where/i/want/my/photos/to/go` in *Finder* and watch as I effortlessly copy your photos there.

You'll notice that your photos are now organized by date and location. Some photos do not have proper dates or location information in them. I do my best and in the worst case scenario I'll use the earlier of the files access or modified time. Ideally your photos have dates and location in the EXIF so my work is more accurate.

Don't fret if your photos don't have much EXIF information. I'll show you how you can fix them up later on but let's walk before we run.

Back to your photos. When I'm done you should see something like this. Notice that I've renamed your files by adding the date and time they were taken. This helps keep them in chronological order when using most viewing applications. You'll thank me later.

```
├── 2015-06-Jun
│   ├── California
│   │   ├── 2015-06-29_16-34-14-img_3900.jpg
│   │   └── 2015-06-29_17-07-06-img_3901.jpg
│   └── Paris
│       └── 2015-06-30_02-40-43-img_3903.jpg
├── 2015-07-Jul
│   ├── Mountain View
│   │   ├── 2015-07-19_17-16-37-img_9426.jpg
│   │   └── 2015-07-24_19-06-33-img_9432.jpg
└── 2015-09-Sep
│   ├── Unknown Location
    │   ├── 2015-09-27_01-41-38-_dsc8705.dng
    │   └── 2015-09-27_01-41-38-_dsc8705.nef
```

Not too bad, eh? Wait a second, what's *Unknown Location*? If I'm not able to figure out where a photo was taken I'll place it into a folder named *Unknown Location*. This typically happens when photos do not have GPS information in their EXIF. You shouldn't see this for photos taken on a smartphone but it's often the case with digital cameras and SLRs. I can help you add GPS information to those photos and get them organized better. Let me show you how.

### Usage Instructions

You can view these instructions on the command line by typing `./elodie.py import --help`, `./elodie.py update --help` or `./elodie.py generate-db --help`.

#### Import photos

```
Usage: elodie.py import [OPTIONS] [PATHS]...

  Import files or directories by reading their EXIF and organizing them
  accordingly.

Options:
  --destination DIRECTORY  Copy imported files into this directory.
                           [required]
  --source DIRECTORY       Import files from this directory, if specified.
  --file PATH              Import this file, if specified.
  --album-from-folder      Use images' folders as their album names.
  --trash                  After copying files, move the old files to the
                           trash.
  --allow-duplicates       Import the file even if it's already been imported.
  --debug                  Override the value in constants.py with True.
  --exclude-regex TEXT     Regular expression for directories or files to
                           exclude.
  --help                   Show this message and exit.
```

#### Update photos

```
Usage: elodie.py update [OPTIONS] FILES...

  Update a file's EXIF. Automatically modifies the file's location and file
  name accordingly.

Options:
  --album TEXT     Update the image album.
  --location TEXT  Update the image location. Location should be the name of a
                   place, like "Las Vegas, NV".
  --time TEXT      Update the image time. Time should be in YYYY-mm-dd
                   hh:ii:ss or YYYY-mm-dd format.
  --title TEXT     Update the image title.
  --help           Show this message and exit.
```

#### (Re)Generate checksum database

```
Usage: elodie.py generate-db [OPTIONS]

  Regenerate the hash.json database which contains all of the sha256
  signatures of media files. The hash.json file is located at ~/.elodie/.

Options:
  --source DIRECTORY  Source of your photo library.  [required]
  --help              Show this message and exit.
```

#### Verify library against bit rot / data rot

```
Usage: elodie.py verify
```

### Excluding folders and files from being imported

If you have specific folders or files which you would like to prevent from being imported you can provide regular expressions which will be used to match and skip files from being imported.

You can specify an exclusion at run time by using the `--exclude-regex` argument of the `import` command. You can pass multiple `--exclude-regex` arguments and all folder/file paths which match will be (silently) skipped.

If there are certain file or folder paths you *never* want to import then you can also add an `[Exclusions]` section to your `config.ini` file. Similar to the command line argument you can provide multiple exclusions. Here is an example.

```
[Exclusions]
synology_folders=@eaDir
thumbnails=.thumbnails
```

### Create your own folder structure

OK, so what if you don't like the folders being named `2015-07-Jul/Mountain View`? No problem!

You can add a custom folder structure by editing your `config.ini` file (which should be placed under `~/.elodie/config.ini`). If you'd like to use a different folder for your configuration file then set an environment variable named `ELODIE_APPLICATION_DIRECTORY` with the fully qualified directory path.

#### Custom folder examples

Sometimes examples are easier to understand than explainations so I'll start there. If you'd like to understand my magic I explain it in more detail below these examples. You customize your folder structure in the `Directory` section of your `config.ini`. For details of the supported formats see [strftime.org](http://strftime.org/)

```
[Directory]
location=%city, %state
year=%Y
full_path=%year/%location
# -> 2015/Sunnyvale, California

location=%city, %state
month=%B
year=%Y
full_path=%year/%month/%location
# -> 2015/December/Sunnyvale, California

location=%city, %state
month=%m
year=%Y
full_path=%year-%month/%location
# -> 2015-12/Sunnyvale, California

date=%Y
location=%city, %state
custom=%date %album
full_path=%location/%custom
# -> Sunnyvale, California/2015 Birthday Party
```

#### Using fallback folders

There are times when the EXIF needed to correctly name a folder doesn't exist on a photo. I came up with fallback folders to help you deal with situations such as this. Here's how it works.

You can specify a series of folder names by separating them with a `|`. That's a pipe, not an L. Let's look at an example.

```
[Directory]
month=%m
year=%Y
location=%city
full_path=%month/%year/%album|%location|%"Beats me"
```

What this asks me to do is to name the last folder the same as the album I find in EXIF. If I don't find an album in EXIF then I should use the location. If there's no GPS in the EXIf then I should name the last folder `Beats me`.

#### How folder customization works

You can construct your folder structure using a combination of the location, dates and camera make/model. Under the `Directory` section of your `config.ini` file you can define placeholder names and assign each a value. For example, `date=%Y-%m` would create a date placeholder with a value of YYYY-MM which would be filled in with the date from the EXIF on the photo.

The placeholders can be used to define the folder structure you'd like to create. The default structure would look like `2015-07-Jul/Mountain View`.

I have some date placeholders you can customize. You can use any of [the standard Python time directives](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior) to customize the date format to your liking.

* `%day` the day the photo was taken.
* `%month` the month the photo was taken.
* `%year` the year the photo was taken.

I have camera make and model placeholders which can be used to include the camera make and model into the folder path.

* `%camera_make` the make of the camera which took the photo.
* `%camera_model` the model of the camera which took the photo.

I also have a few built-in location placeholders you can use. Use this to construct the `%location` you use in `full_path`.

* `%city` the name of the city the photo was taken. Requires geolocation data in EXIF.
* `%state` the name of the state the photo was taken. Requires geolocation data in EXIF.
* `%country` the name of the country the photo was taken. Requires geolocation data in EXIF.

In addition to my built-in and date placeholders you can combine them into a single folder name using my complex placeholders.

* `%location` can be used to combine multiple values of `%city`, `%state` and `%country`. For example, `location=%city, %state` would result in folder names like `Sunnyvale, California`.
* `%date` can be used to combine multiple values from [the standard Python time directives](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior). For example, `date=%Y-%m` would result in folder names like `2015-12`.
* `%custom` can be used to combine multiple values from anything else. Think of it as a catch-all when `%location` and `%date` don't meet your needs.

#### How file customization works

You can configure how Elodie names your files using placeholders. This works similarly to how folder customization works. The default naming format is what's referred to elsewhere in this document and has many thought through benefits. Using the default will gives you files named like `2015-09-27_01-41-38-_dsc8705.jpg`.


* Minimizes the likelihood of naming conflicts.
* Encodes important EXIF information into the file name.
* Optimizes for sort order when listing in most file and photo viewers.

If you'd like to specify your own naming convention it's recommended you include something that's mostly unique like the time including seconds. You'll need to include a `[File]` section in your `config.ini` file with a name attribute. If a placeholder doesn't have a value then it plus any preceding characters which are not alphabetic are removed.

By default the resulting filename is all lowercased. To change this behavior to uppercasing add capitalization=upper.

```
[File]
date=%Y-%m-%b-%H-%M-%S
name=%date-%original_name-%title.%extension
# -> 2012-05-mar-12-59-30-dsc_1234-my-title.jpg

date=%Y-%m-%b-%H-%M-%S
name=%date-%original_name-%album.%extension
capitalization=upper
# -> 2012-05-MAR-12-59-30-DSC_1234-MY-ALBUM.JPG
```

### Reorganize by changing location and dates

If you notice some photos were incorrectly organized you should definitely let me know. In the example above I put two photos into an *Unknown Location* folder because I didn't find GPS information in their EXIF. To fix this I'll help you add GPS information into the photos' EXIF and then I'll reorganize them.

#### Tell me where your photos were taken
Run the command below if you want to tell me the photos were taken in Las Vegas. You don't have to type all that in though. It's easier to just type `./elodie.py update --location="Las Vegas, NV" ` and select and drag the files from *OS X Finder* into the terminal.

```
./elodie.py update --location="Las Vegas, NV" /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.dng /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.nef
```

You should see this after running that command.

```
└── 2015-09-Sep
│   ├── Las Vegas
    │   ├── 2015-09-27_01-41-38-_dsc8705.dng
    │   └── 2015-09-27_01-41-38-_dsc8705.nef
```

#### Tell me when you took your photos
Run the command below if I got the date wrong when organizing your photos. Similarly to the above command you can drag files from *Finder* into your terminal.

```
./elodie.py update --time="2015-04-15" /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.dng /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.nef
```

That will change the date folder like so.

```
└── 2015-04-Apr
│   ├── Las Vegas
    │   ├── 2015-09-27_01-41-38-_dsc8705.dng
    │   └── 2015-09-27_01-41-38-_dsc8705.nef
```

You can, of course, ask me to change the location and time. I'll happily update the photos and move them around accordingly.

```
./elodie.py update --location="Las Vegas, NV" --time="2015-04-15" /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.dng /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.nef
```

## What about photos I take in the future?

Organizing your existing photos is great. But I'd be lying if I said I was the only one who could help you with that. Unlike other programs I put the same effort into keeping your library organized into the future as I have in getting it organized in the first place.

### Letting me know when you've got more photos to organize

In order to sort new photos that I haven't already organized I need someone to tell me about them. There's no single way to do this. You could use inotify, cron, Automator or my favorite app - Hazel; it doesn't matter.

If you'd like to let me know of a specific photo or group of photos to add to your library you would run one of the following commands. Use fully qualified paths for everything since you won't be running this manually.

```
# I can import a single file into your library.
./elodie.py import --destination="/where/i/want/my/photo/to/go" /full/path/to/file.jpg

# I can also import all the photos from a directory into your library.
./elodie.py import --destination="/where/i/want/my/photo/to/go" /where/my/photos/are
```

## Why not use a database?

Look, it's not that I think databases are evil. One of my friends is a database. It's just that I've been doing this for a long time and I've always used a database for it. In the end they're more trouble than they're worth. I should have listened to my mother when she told me to not date a database.

It's a lot more work to organize photos without a database. No wonder everyone else uses them. But your happiness is my happiness. If a little elbow grease on my part makes you happy then I'm glad to do it.

### A bit on how I do all this without a database

Every photo is essentially a database. So it's more accurate to say I use the thousands of tiny databases you already have and use them to organize your photos.

I'm simple. I put a photo into its proper location. I can update a photo to have the right date or location. The latter triggers the first; creating a nice tidy loop of organizational goodness.

I don't do anything else so don't bother asking.

## EXIF and XMP tags

When I organize photos I look at the embedded metadata. Here are the details of how I determine what information to use in order of precedence.

| Dimension | Fields | Notes |
|---|---|---|
| Date Taken (photo) | EXIF:DateTimeOriginal, EXIF:CreateDate, EXIF:ModifyDate, file created, file modified |   |
| Date Taken (video, audio) | QuickTime:CreationDate, QuickTime:CreateDate, QuickTime:CreationDate-und-US, QuickTime:MediaCreateDate, H264:DateTimeOriginal, file created, file modified |   |
| Location (photo) | EXIF:GPSLatitude/EXIF:GPSLatitudeRef, EXIF:GPSLongitude/EXIF:GPSLongitudeRef  |   |
| Location (video, audio) | XMP:GPSLatitude, Composite:GPSLatitude, XMP:GPSLongitude, Composite:GPSLongitude | Composite tags are read-only |
| Title (photo) | XMP:Title |   |
| Title (video, audio) | XMP:DisplayName |   |
| Album | XMP-xmpDM:Album, XMP:Album | XMP:Album is user defined in `configs/ExifTool_config` for backwards compatability |
| Camera Make (photo, video) | EXIF:Make, QuickTime:Make |   |
| Camera Model (photo, video) | EXIF:Model, QuickTime:Model |   |

## Using OpenStreetMap data from MapQuest

I use MapQuest to help me organize your photos by location. You'll need to sign up for a [free developer account](https://developer.mapquest.com/plans) and get an API key. They give you 15,000 calls per month so I can't do any more than that unless you shell out some big bucks to them. Once I hit my limit the best I'll be able to do is *Unknown Location* until the following month.

Once you sign up you'll have to get an API key and copy it into a file named `~/.elodie/config.ini`. I've included a `config.ini-sample` file which you can copy to `config.ini`.

```
mkdir ~/.elodie
cp config.ini-sample ~/.elodie/config.ini
# now you're ready to add your MapQuest key
```

If you're an english speaker then you will probably want to add `prefer_english_names=True` to the `[MapQuest]` section else you'll have cities named using the local language.

## Questions, comments or concerns?

The best ways to provide feedback is by opening a [GitHub issue](https://github.com/jmathai/elodie/issues) or emailing me at [jaisen@jmathai.com](mailto:jaisen@jmathai.com).
