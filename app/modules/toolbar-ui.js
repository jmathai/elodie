var exports = module.exports = {};

var menubar = require('menubar'),
    menu = require('menu'),
    tray = require('tray'),
    config = require('./config.js'),
    loadUrl = null;
var os = require('os')

var s_dir = __dirname.substr(0,__dirname.lastIndexOf(os.platform() == 'win32' ? '\\' : '/')) + 
                              (os.platform() == 'win32' ? '\\html' : '/html');
                                              
exports.app = app = menubar(
  {
    preloadWindow: true,
    dir: s_dir,
    index: 'index.html',
    pages: {
      'blank': 'blank.html',
      'config': 'config.html',
      'location': 'location.html'
    },
    width: 400,
    height: 500,
    'window-position': 'trayCenter',
	'frame': os.platform() == 'win32' ? true : false,
	'always-on-top': os.platform() == 'win32' ? true : false
  }
);

exports.ready = function() {
  console.log('app is ready');

  var template = [{
    label: "Application",
    submenu: [
        { label: "Quit", accelerator: "Command+Q", click: function() { app.quit(); }}
    ]}, {
    label: "Edit",
    submenu: [
        { label: "Undo", accelerator: "CmdOrCtrl+Z", selector: "undo:" },
        { label: "Redo", accelerator: "Shift+CmdOrCtrl+Z", selector: "redo:" },
        { label: "Cut", accelerator: "CmdOrCtrl+X", selector: "cut:" },
        { label: "Copy", accelerator: "CmdOrCtrl+C", selector: "copy:" },
        { label: "Paste", accelerator: "CmdOrCtrl+V", selector: "paste:" },
        { label: "Select All", accelerator: "CmdOrCtrl+A", selector: "selectAll:" }
    ]}
  ];
  menu.setApplicationMenu(menu.buildFromTemplate(template));

  this.tray.setToolTip('Drag and drop files here');
    console.log(app.getOption('dir'));
  this.tray.setImage(app.getOption('dir') + '/img/logo@18x22xbw.png');
  this.tray.on('clicked', function clicked () {
    console.log('tray-clicked')
  });
  this.tray.on('drop-files', function dropFiles (ev, files) {
    loadUrl = app.getOption('pages')['location'];
    app.showWindow();
    //app.window.openDevTools();
    app.window.webContents.on('did-finish-load', function() {
      app.window.webContents.send('files', files);
      app.window.webContents.send('preview', files);
    });
  });
};

exports.onDropFiles = function(event, args) {
  var files = args;
  loadUrl = app.getOption('pages')['location'];
  app.showWindow();
 
  app.window.webContents.on('did-finish-load', function() {
  app.window.webContents.send('files', files);
  app.window.webContents.send('preview', files);
 });
};
 

exports.createWindow = function() {
  console.log('create-window')
};

exports.afterCreateWindow = function() {
  console.log('after-create-window')
};

exports.show = function() {
  if(!config.hasConfig()) {
    loadUrl = this.getOption('pages')['config'];
  } else if(loadUrl === null) {
    loadUrl = this.getOption('index');
  }

  this.window.loadUrl('file://' + this.getOption('dir') + '/' + loadUrl);
  loadUrl = null;
  //app.window.openDevTools();
};

exports.afterShow = function() {
  console.log('after-show');
};

exports.hide = function() {
  console.log('hide');
};

exports.afterHide = function() {
  console.log('after-hide')
  this.window.loadUrl('file://' + this.getOption('dir') + '/' + this.getOption('pages')['blank']);
};
