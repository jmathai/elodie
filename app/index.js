var menubar = require('menubar'),
    menu = require("menu"),
    tray = require('tray'),
    ipc = require('ipc'),
    exec = require('child_process').exec,
    loadUrl = null;

/*
 * The main process listens for events from the web renderer.
 */

// When photos are dragged onto the toolbar and photos are requested to be updated it will fire an 'update-photos' ipc event.
// The web renderer will send the list of photos, type of update and new value to apply
// Once this main process completes the update it will send a 'update-photos-completed' event back to the renderer with information
//  so a proper response can be displayed.
ipc.on('import-photos', function(event, args) {
  var params = args,
      normalize;

  console.log('import-photos');
  console.log(args);
  if(typeof(args['source']) === 'undefined' || args['source'].length === 0 || typeof(args['destination']) === 'undefined' || args['destination'].length === 0) {
    console.log('no source or destination passed in to import-photos');
    event.sender.send('update-import-no-photos', null);
    return;
  }

  args['source'] = args['source'].normalize();
  args['destination'] = args['destination'].normalize();

  update_command = __dirname + '/../dist/elodie/elodie import --source="' + args['source'] +  '" --destination="' + args['destination'] + '"';
  //update_command = __dirname + '/../elodie.py import --source="' + args['source'] +  '" --destination="' + args['destination'] + '"';
  
  console.log(update_command)
  exec(update_command, function(error, stdout, stderr) {
    console.log('out ' + stdout)
    console.log('err ' + stderr)
    /*params['error'] = error
    params['stdout'] = '[' + stdout.replace(/\n/g,',').replace(/\,+$/g, '').replace(/\n/g,'') + ']'
    params['stderr'] = stderr
    console.log('parsed')
    console.log(params['stdout'])*/
    event.sender.send('update-import-success', args);
  });
});

// When photos are dragged onto the toolbar and photos are requested to be updated it will fire an 'update-photos' ipc event.
// The web renderer will send the list of photos, type of update and new value to apply
// Once this main process completes the update it will send a 'update-photos-completed' event back to the renderer with information
//  so a proper response can be displayed.
ipc.on('update-photos', function(event, args) {
  var params = args,
      normalize;

  console.log('update-photos');
  console.log(args);
  if(typeof(args['files']) === 'undefined' || args['files'].length === 0) {
    console.log('no files passed in to update-photos');
    return;
  }

  normalize = function(files) {
    for(var i=0; i<files.length; i++) {
      files[i] = files[i].normalize()
    }
    return files
  }
  files = normalize(args['files'])

  update_command = __dirname + '/../dist/elodie/elodie update'
  //update_command = __dirname + '/../elodie.py update'
  if(args['location'].length > 0) {
    update_command += ' --location="' + args['location'] + '"';
  }
  if(args['album'].length > 0) {
    update_command += ' --album="' + args['album'] + '"';
  }
  if(args['datetime'].length > 0) {
    update_command += ' --time="' + args['datetime'] + '"';
  }
  if(args['title'].length > 0) {
    update_command += ' --title="' + args['title'] + '"';
  }

  update_command += ' "' + files.join('" "') + '"'
  
  console.log(update_command)
  exec(update_command, function(error, stdout, stderr) {
    console.log('out ' + stdout)
    console.log('err ' + stderr)
    params['error'] = error
    params['stdout'] = '[' + stdout.replace(/\n/g,',').replace(/\,+$/g, '').replace(/\n/g,'') + ']'
    params['stderr'] = stderr
    console.log('parsed')
    console.log(params['stdout'])
    event.sender.send('update-photos-success', params);
  });
});

ipc.on('launch-finder', function(event, path) {
  console.log(path);
  var shell = require('shell');
  shell.showItemInFolder(path);
});

ipc.on('program-quit', function(event, path) {
  console.log('program-quit');
  //mb.tray.destroy();
  mb.quit();
});

var mb = menubar(
      {
        preloadWindow: true,
        dir: __dirname + '/html',
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

mb.on('ready', function ready () {
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

  this.tray.setToolTip('Drag and drop files here')
  this.tray.setImage(mb.getOption('dir') + '/img/logo@18x22xbw.png')
  this.tray.on('clicked', function clicked () {
    console.log('tray-clicked')
  })
  this.tray.on('drop-files', function dropFiles (ev, files) {
    loadUrl = mb.getOption('pages')['location'];
    mb.showWindow();
    //mb.window.openDevTools();
    mb.window.webContents.on('did-finish-load', function() {
      mb.window.webContents.send('files', files);
      mb.window.webContents.send('preview', files);
    });
  })
})

mb.on('create-window', function createWindow () {
  console.log('create-window')
})

mb.on('after-create-window', function afterCreateWindow () {
})

var loaded = false;
mb.on('show', function show () {
  if(loadUrl === null) {
    loadUrl = this.getOption('index');
  }
  this.window.loadUrl('file://' + this.getOption('dir') + '/' + loadUrl);
  loadUrl = null;
  //mb.window.openDevTools();
})

mb.on('after-show', function afterShow () {
  console.log('after-show')
})

mb.on('hide', function hide () {
  console.log('hide')
})

mb.on('after-hide', function afterHide () {
  console.log('after-hide')
  this.window.loadUrl('file://' + this.getOption('dir') + '/' + this.getOption('pages')['blank']);
})
