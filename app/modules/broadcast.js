var exports = module.exports = {};
var path = require('path');
var exec = require('child_process').exec,
    config = require('./config.js');

// The main process listens for events from the web renderer.
// When photos are dragged onto the toolbar and photos are requested to be updated it will fire an 'update-photos' ipc event.
// The web renderer will send the list of photos, type of update and new value to apply
// Once this main process completes the update it will send a 'update-photos-completed' event back to the renderer with information
//  so a proper response can be displayed.

exports.importPhotos = function(event, args) {
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

  update_command = path.normalize(__dirname + '/../../dist/elodie/elodie') + ' import --source="' + args['source'] +  '" --destination="' + args['destination'] + '"';
  //update_command = __dirname + '/../../elodie.py import --source="' + args['source'] +  '" --destination="' + args['destination'] + '"';
  
  console.log(update_command);
  exec(update_command, function(error, stdout, stderr) {
    console.log('out ' + stdout);
    console.log('err ' + stderr);
    /*params['error'] = error
    params['stdout'] = '[' + stdout.replace(/\n/g,',').replace(/\,+$/g, '').replace(/\n/g,'') + ']'
    params['stderr'] = stderr
    console.log('parsed')
    console.log(params['stdout'])*/
    event.sender.send('update-import-success', args);
  });
};

exports.updateConfig = function(event, args) {
  var params = args,
      status;
  status = config.writeConfig(params);
  if(status) {
    event.sender.send('update-config-status', true);
  } else {
    event.sender.send('update-config-status', false);
  }
};

// When photos are dragged onto the toolbar and photos are requested to be updated it will fire an 'update-photos' ipc event.
// The web renderer will send the list of photos, type of update and new value to apply
// Once this main process completes the update it will send a 'update-photos-completed' event back to the renderer with information
//  so a proper response can be displayed.
exports.updatePhotos = function(event, args) {
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
  elodie_path = path.normalize(__dirname + '/../../dist/elodie/elodie');
  update_command = elodie_path +' update'
  //update_command = __dirname + '/../../elodie.py update'
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
};

exports.launchFinder = function(event, path) {
  console.log(path);
  var shell = require('shell');
  shell.showItemInFolder(path);
};

exports.launchUrl = function(event, url) {
  console.log(url);
  var shell = require('shell');
  shell.openExternal(url);
};

exports.programQuit = function(event, path) {
  console.log('program-quit');
  //mb.tray.destroy();
  mb.quit();
};
