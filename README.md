# elodie
pip install exifread
pip install LatLon
pip install requests

brew install exiftool

Need config.ini for reverse lookup

Need pyexiv2. Here's how to install on OS X using homebrew...on your own to use other tools.

Sourced from http://stackoverflow.com/a/18817419/1318758

May need to run these.
brew rm $(brew deps pyexiv2)
brew rm pyexiv2

Definietly need to run these
brew install boost --build-from-source
brew install pyexiv2
