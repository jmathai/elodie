var __constants__ = {
  baseUrl : 'http://localhost:5000'
};

var __process__ = {};

if(typeof(require) === 'function') {
  var ipc = require('ipc');
  ipc.on('files', function(files) {
    __process__.files = files;
  });
  ipc.on('preview', function(files) {
    handlers.renderPreview(files);
  });
  ipc.on('update-import-success', function(args) {
    //var response = JSON.parse(args['stdout']);
    handlers.setSuccessTitle();
    handlers.removeProgressIcons();
    handlers.addSuccessImportMessage(args);
  });
  ipc.on('update-photos-success', function(args) {
    var response = JSON.parse(args['stdout']);
    handlers.setSuccessTitle();
    handlers.removeProgressIcons();
    handlers.updateStatus(response);
  });

  function Broadcast() {
    this.send = function(name, message) {
      ipc.send(name, message);
    };
  }
}

function Handlers() {
  var self = this;
  var broadcast = new Broadcast();
  this.click = {};
  this.submit = {};
  this.change = {};
  // CHANGE
  this.change.fileSelected = function(ev) {
    var el = ev.target,
        dir = el.value.substr(el.value.lastIndexOf("\\")+1),
        tgt = document.querySelector(el.dataset.display);
    tgt.innerHTML = dir;
  };
  // CLICK
  this.click.selectFile = function(ev) {
    var el = ev.target,
        tgt = document.querySelector(el.dataset.for);
    ev.preventDefault();
    tgt.click();
  };
  this.click.launchFinder = function(ev) {
    var el = ev.target,
        tgt = el.dataset.path;
    ev.preventDefault();
    broadcast.send('launch-finder', tgt);
  };
  // SUBMIT
  this.submit.importPhotos = function(ev) {
    var el = ev.target,
        cls = el.className,
        params;
    ev.preventDefault();
    document.querySelector('button.push i').className = 'icon-spin animate-spin';

    params = {};
    params['source'] = document.querySelector('input[name="source"]').value
    params['destination'] = document.querySelector('input[name="destination"]').value
    broadcast.send('import-photos', params);
  };
  this.submit.updatePhotos = function(ev) {
    var el = ev.target,
        cls = el.className,
        params;
    ev.preventDefault();
    document.querySelector('button.push i').className = 'icon-spin animate-spin';

    params = {};
    params['location'] = document.querySelector('input[id="location-field"]').value;
    params['datetime'] = document.querySelector('input[id="datetime-field"]').value;
    params['album'] = document.querySelector('input[id="album-field"]').value;
    params['title'] = document.querySelector('input[id="title-field"]').value;

    if(params['location'].length === 0 && params['datetime'].length === 0 && params['album'].length === 0 && params['title'].length === 0)
      return;

    params['files'] = __process__.files;
    broadcast.send('update-photos', params);
  };

  this.addSuccessImportMessage = function(args) {
    document.querySelector('.import-success').innerHTML = 'Your photos were successfully imported. <a href="#" class="launchFinder" data-path="'+args['destination'] +'">View them here</a>.';
  };

  this.dispatch = function(ev) {
    var classes = ev.target.className.split(' ');
    for(i=0; i<classes.length; i++) {
      if(typeof(self[ev.type][classes[i]]) !== 'undefined') {
        self[ev.type][classes[i]](ev);
      }
    }
  };

  this.removeProgressIcons = function() {
    var els = document.querySelectorAll('i.icon-spin');
    for(el in els) {
      els[el].className = '';
    }
  };

  this.renderPreview = function(files) {
    html = '<label>You selected ' + (files.length > 1 ? 'these photos' : 'this photo') + '</label>';
    for(var i=0; i<files.length && i<16; i++) {
      if(files[i].match(/(mov|mp4|3gp|avi)/i) === null) {
        html += '<div class="center-cropped" style="background-image:url(\'file://'+files[i]+'\');" title="'+files[i]+'"></div>';
      } else {
        html += '<div class="center-cropped video"></div>';
      }
    }
    if(files.length >= 16) {
      html += '<br>...and ' + (files.length -16) + ' more.';
    }
    document.querySelector('.preview').innerHTML = html;
  };

  this.setSuccessTitle = function() {
    var el = document.querySelector('.titlebar i').className = 'icon-happy';
  };

  this.updateStatus = function(response) {
    var el = document.querySelector('.status'),
        source, destination, html;

    console.log('update status');
    console.log(response);;
    
    if(response.length > 0) {
      html = '<label>Status</label><ul>';
      for(i=0; i<response.length; i++) {
        source = response[i]['source'] || null;
        destination = response[i]['destination'] || null;
        sourceFileName = source.substr(source.lastIndexOf('/')+1);
        if(destination === null) {
          html += '<li><i class="icon-unhappy"></i> ' + sourceFileName + '</li>';
        } else {
          html += '<li><i class="icon-happy"></i> ' + sourceFileName + '<div class="destination" title="'+destination+'">'+destination+'</div></li>';
        }
      }
      html += '</ul>';
      el.innerHTML = html;
      el.style.display = 'block';
    }
  };
}
var handlers = new Handlers();
window.addEventListener('click', handlers.dispatch);
window.addEventListener('submit', handlers.dispatch);
window.addEventListener('change', handlers.dispatch);
