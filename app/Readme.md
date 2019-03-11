# Hello, I'm Elodie's GUI
~~ *Your Personal EXIF-based Photo, Video and Audio Assistant* ~~

<p align="center"><img src ="../../../blob/master/creative/logo@300x.png" /></p>

You can download [my latest GUI from the releases page](https://github.com/jmathai/elodie/releases).

My GUI taskbar app sits nestled away in your taskbar until you need me.

Let's say you took a few hundred photos in New York City. I'll have put the photos into a folder named *New York City*. You decide you'd rather organize those photos into a folder named *Summer in NYC*. What you'd do is select the photos using Finder and drag them onto my taskbar icon. I'll display a few options and one of them would be to *Create album*. Type in an album name and I'll add this to the EXIF of your photos and move them to a folder with the same name.

*NOTE: I've extensively used the GUI but it's a work in progress.*

## See me in action

Updating EXIF of photos using the GUI taskbar app.

[![IMAGE ALT TEXT](http://img.youtube.com/vi/fF_jGCaMog0/0.jpg)](http://www.youtube.com/watch?v=fF_jGCaMog0 "Updating Photos Using GUI Taskbar App")

## Building the app

You'll need to bundle up the python dependencies and create an electron app using Node.js.

### Bundling the python libraries

First you'll need to [install the python dependencies](../../../#install-everything-you-need).

Once you've done that you'll need to install `pyinstaller`.

```
pip install pyinstaller
```

Next you can `cd` to the root of the repository and run `pyinstaller`.


```
pyinstaller elodie.spec
```

This should create a `dist` folder that bundles all of the dependencies. Now you're ready to build the GUI app.

### Building the GUI app

The GUI app is written using [Node.js](https://github.com/nodejs) and [Electron](https://github.com/atom/electron) and you'll need [electron-packager](https://github.com/maxogden/electron-packager) to create an executable file for your operating system.

I'm going to assume you've got *Node.js* installed. I've successfully built the app using version `5.1.0` on OS X.

```
# use --platform=win32 for Windows or --platform=linux for linux
electron-packager . Elodie --platform=darwin --arch=x64 --electron-version=0.34.2 --overwrite
```

This will create a folder named `Elodie-darwin-x64` which contains the executable. Running the executable should add my face to your taskbar which you can click on or drag photos over.
