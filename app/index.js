var ipc = require('ipc'),
    toolbarUi = require('./modules/toolbar-ui.js'),
    broadcast = require('./modules/broadcast.js');

toolbarUi.app.on('ready', toolbarUi.ready);
toolbarUi.app.on('create-window', toolbarUi.createWindow);
toolbarUi.app.on('after-create-window', toolbarUi.afterCreateWindow); 
toolbarUi.app.on('show', toolbarUi.show); 
toolbarUi.app.on('after-show', toolbarUi.afterShow);
toolbarUi.app.on('hide', toolbarUi.show);
toolbarUi.app.on('after-hide', toolbarUi.afterHide);

ipc.on('import-photos', broadcast.importPhotos);
ipc.on('update-config', broadcast.updateConfig);
ipc.on('update-photos', broadcast.updatePhotos);
ipc.on('launch-finder', broadcast.launchFinder);
ipc.on('launch-url', broadcast.launchUrl);
ipc.on('program-quit', broadcast.programQuit);
ipc.on('load-update-photos', toolbarUi.onDropFiles);