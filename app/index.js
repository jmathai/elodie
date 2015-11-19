var ipc = require('ipc');
var toolbarUi = require('./modules/toolbar-ui.js');
var broadcast = require('./modules/broadcast.js');

toolbarUi.app.on('ready', toolbarUi.ready);
toolbarUi.app.on('create-window', toolbarUi.createWindow);
toolbarUi.app.on('after-create-window', toolbarUi.afterCreateWindow); 
toolbarUi.app.on('show', toolbarUi.show); 
toolbarUi.app.on('after-show', toolbarUi.afterShow);
toolbarUi.app.on('hide', toolbarUi.show);
toolbarUi.app.on('after-hide', toolbarUi.afterHide);

ipc.on('import-photos', broadcast.importPhotos);
ipc.on('update-photos', broadcast.updatePhotos);
ipc.on('launch-finder', broadcast.launchFinder);
ipc.on('program-quit', broadcast.programQuit);
