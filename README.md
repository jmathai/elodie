# Hello, I'm Elodie

I work tirelessly to make sure your photos are always sorted and organized so you can focus on more important things. By photos I mean JPEG, DNG, NEF and common video files.

You don't love me yet but you will.

I only do 3 things.
* Firstly I organize your existing collection of photos.
* Second I help make it easy for all the photos you haven't taken yet to flow into the exact location they belong.
* Third but not least I promise to do all this without a yucky propietary database that some colleagues of mine use.

*NOTE: make sure you've installed me and my friends before running the commands below. [Instructions](#install-everything-you-need) at the bottom of this page.*

## The dream setup I am optimized for

I'm most helpful when I'm fully utilized to keep your photos organized. My parents had ambitious aspirations for me even when I was growing in my momma's belly . They're dreamers and so am I.

Here's dada's (very asynchronous) setup.
* Specify a folder in his Dropbox to store the organized photo library.
* Set up a Hazel rule to notify me when photos arrive in `~/Downloads` so I can import them.
  * The rule waits 1 minute before processing the photo which gives him a chance to move it elsewhere if it's not something he wants in the library.
* Use AirDrop to transfer files from his or momma's iPhone to his laptop. That goes to `~/Downloads` for the Hazel rule to process.
  * AirDrop is fast, easy for momma to use and once the transfer is finished they don't have to stick around. I'll move it to Dropbox and Dropbox will sync it to their servers.
* Periodically recategorize photos by fixing their location or date or by adding them to an album.
* Have a Synology at home set to automatically sync down from Dropbox.
 
This setup means dada can quickly get photos off his or momma's phone and know that they'll be organized and backed up by the time they're ready to view them.

## Let's organize your existing photos

My guess is you've got quite a few photos scattered around. The first thing I'll help you do is to get those photos organized. It doesn't matter if you have hundreds, thousands or tens of thousands of photos; the more the merrier.

Fire up your terminal and run this command which *__copies__* your photos into something a bit more structured.

```
./elodie.py --type=photo --source="/where/my/photos/are" --destination="/where/i/want/my/photos/to/go"
```

I'm pretty fast but depending on how many photos you have you might want to grab a snack. When you run this command I'll `print` out my work as I go along. If you're bored you can open `/where/i/want/my/photos/to/go` in *Finder* and watch as I effortlessly copy your photos there.

You'll notice that your photos are now organized by date and location. Some photos do not have proper dates or location information in them. I do my best and in the worst case scenario I'll use the earlier of the files access or modified time. Ideally your photos have dates and location in the EXIF so my work is more accurate.

Don't fret if your photos don't have much EXIF information. I'll show you how you can fix them up later on but let's walk before we run.

Back to your photos. When I'm done you should see something like this.

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

### Reorganize by changing location and dates

If you notice some photos were incorrectly organized you should definitely let me know. In the example above I put two photos into an *Unknown Location* folder because I didn't find GPS information in their EXIF. To fix this I'll help you add GPS information into the photos' EXIF and then I'll reorganize them.

#### Tell me where your photos were taken
Run the command below if you want to tell me the photos were taken in Las Vegas. You don't have to type all that in though. It's easier to just type `./update.py --location="Las Vegas, NV" ` and select and drag the files from *OS X Finder* into the terminal.

```
./update.py --location="Las Vegas, NV" /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.dng /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.nef
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
./update.py --time="2015-04-15" /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.dng /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.nef
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
./update.py --location="Las Vegas, NV" --time="2015-04-15" /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.dng /where/i/want/my/photos/to/go/2015-09-Sep/Unknown\ Location/2015-09-27_01-41-38-_dsc8705.nef
```

## What about photos I take in the future?

Organizing your existing photos is great. But I'd be lying if I said I was the only one who could help you with that. Unlike other programs I put the same effort into keeping your library organized into the future as I have in getting it organized in the first place.

### Letting me know when you've got more photos to organize

In order to sort new photos that I haven't already organized I need someone to tell me about them. There's no single way to do this. You could use inotify, cron, Automator or my favorite app - Hazel; it doesn't matter.

If you'd like to let me know of a specific photo or group of photos to add to your library you would run one of the following command. Use fully qualified paths for everything since you won't be running this manually.

```
# I can import a single file into your library.
/full/path/to/import.py --type=photo --file="/full/path/to/file.jpg" --destination="/where/i/want/my/photo/to/go"

# I can also import all the photos from a directory into your library.
/full/path/to/import.py --type=photo --source="/where/my/photos/are" --destination="/where/i/want/my/photo/to/go"
```

## Why not use a database?

Look, it's not that I think databases are evil. One of my friends is a database. It's just that I've been doing this for a long time and I've always used a database for it. In the end they're more trouble than they're worth. I should have listened to my mother when she told me to not date a database.

It's a lot more work to organize photos without a database. No wonder everyone else uses them. But your happiness is my happiness. If a little elbow grease on my part makes you happy then I'm glad to do it.

### A bit on how I do all this without a database

Every photo is essentially a database. So it's more accurate to say I use the thousands of tiny databases you already have and use them to organize your photos.

I'm simple. I put a photo into its proper location. I can update a photo to have the right date or location. The latter triggers the first; creating a nice tidy loop of organizational goodness.

I don't do anything else so don't bother asking.

## Install everything you need

You'll need to clone this repository and install a few dependencies. Let's start by cloning.

```
git clone git@github.com:jmathai/elodie.git
```

The commands on this page assume you're running them from the root of this repository. I don't have any submodules but you'll need to install the following packages.

```
pip install LatLon
pip install requests
```

You'll need *pyexiv2* which isn't available through `pip`. Thankfully it's available view homebew for OS X. If you're running another operating system you're sort of on your own but my pal Google should be able to help. Some folks may be able to simply run these commands. The first is a drag and can take up to 30 minutes. Don't say I didn't warn you.

```
brew install boost --build-from-source
brew install pyexiv2
```

If you have problems you can run the following commands which the fine folks at StackOverflow [suggested to me once](http://stackoverflow.com/a/18817419/1318758).

### Using OpenStreetMap data from MapQuest

I use MapQuest to help me organize your photos by location. You'll need to sign up for a [free developer account](https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free) and get an API key. They give you 15,000 calls per month so I can't do any more than that unless you shell out some big bucks to them. Once I hit my limit the best I'll be able to do is *Unknown Location* until the following month.

Once you sign up you'll have to get an API key and copy it into a file named `config.ini` at the root of the repository. I've included a `config.ini-sample` file which you can copy to `config.ini`.
