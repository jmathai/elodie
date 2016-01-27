var exports = module.exports = {};
var fs = require('fs'),
    defaultConfigFile = (function() {
      var f = __dirname;
      for(var i=0; i<2; i++) {
        f = f.substr(0, f.lastIndexOf('\\'));
      }
      return f + '\\config.ini-sample';
    })(),
    configFile = (process.env.HOME || process.env.USERPROFILE) + '\\.elodie\\config.ini',
    hasConfig,
    setConfig;

exports.hasConfig = function() {
  console.log(defaultConfigFile);
  console.log(configFile);
  return fs.existsSync(configFile);
};

exports.writeConfig = function(params) {
  var contents;
  try {
    if(exports.hasConfig()) {
      contents = fs.readFileSync(configFile).toString();
    } else {
      contents = fs.readFileSync(defaultConfigFile).toString();
    }

    console.log(contents);
    contents = contents.replace(/key=[\s\S]+$/,'key='+params['mapQuestKey']);
    fs.writeFileSync(configFile, contents);
    return true;
  } catch(e) {
    console.log(e);
    return false;
  }
};
