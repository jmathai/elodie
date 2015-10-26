var __constants__ = {
  baseUrl : 'http://localhost:5000'
};

var __process__ = {};

var ipc = require('ipc');
ipc.on('files', function(files) {
  __process__.files = files;
});
ipc.on('preview', function(files) {
  handlers.renderPreview(files)
});
ipc.on('update-photos-success', function(args) {
  handlers.setSuccessTitle()
  handlers.removeProgressIcons()
});

function Broadcast() {
  this.send = function(name, message) {
    ipc.send(name, message);
  };
}

function Handlers() {
  var self = this;
  var broadcast = new Broadcast();
  this.addAlbum = function(ev) {
    var alb = document.querySelector('input[id="album-field"]').value,
        progress = document.querySelector('button[class~="addAlbum"] i');

    progress.className = 'icon-spin animate-spin'
    if(typeof(__process__.files) !== 'object' && __process__.files.length === 0) {
      return;
    }

    console.log(__process__.files);
    progress.className = 'icon-spin animate-spin'
    broadcast.send('update-photos', {album: alb, files: __process__.files});
  };

  this.addLocation = function(ev) {
    var loc = document.querySelector('input[id="location-field"]').value,
        progress = document.querySelector('button[class~="addLocation"] i');

    if(typeof(__process__.files) !== 'object' && __process__.files.length === 0) {
      return;
    }

    console.log(__process__.files);
    progress.className = 'icon-spin animate-spin'
    broadcast.send('update-photos', {location: loc, files: __process__.files});
  };

  this.dispatch = function(ev) {
    var classes = ev.target.className.split(' ');
    for(i=0; i<classes.length; i++) {
      if(typeof(self[classes[i]]) !== 'undefined') {
        self[classes[i]](ev);
      }
    }
  };

  this.removeProgressIcons = function() {
    var els = document.querySelectorAll('i.icon-spin');
    for(el in els) {
      els[el].className = ''
    }
  };

  this.renderPreview = function(files) {
    html = '<label>You selected ' + (files.length > 1 ? 'these photos' : 'this photo') + '</label>'
    for(var i=0; i<files.length; i++) {
      html += '<div class="center-cropped" style="background-image:url(\'file://'+files[i]+'\');" title="'+files[i]+'"></div>'
    }
    document.querySelector('.preview').innerHTML = html
  };

  this.setSuccessTitle = function() {
    var el = document.querySelector('.titlebar i').className = 'icon-happy'
  };
}
var handlers = new Handlers();
document.addEventListener('click', handlers.dispatch);
