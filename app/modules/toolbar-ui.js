var exports = module.exports = {};

var menubar = require('menubar'),
    menu = require('menu'),
    tray = require('tray'),
    loadUrl = null;

exports.app = app = menubar(
  {
    preloadWindow: true,
    dir: __dirname.substr(0, __dirname.lastIndexOf('/')) + '/html',
    index: 'index.html',
    pages: {
      'blank': 'blank.html',
      'location': 'location.html'
    },
    width: 400,
    height: 500,
    'window-position': 'trayCenter'
  }
);

exports.ready = function() {
  console.log('app is ready')
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

exports.createWindow = function() {
  console.log('create-window')
};

exports.afterCreateWindow = function() {
  console.log('after-create-window')
};

exports.show = function() {
  if(loadUrl === null) {
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
