/***
|''Name:''|WebDavPlugin|
|''Description:''|Allows a TiddlyWiki to be saved to a WebDav server|
|''Author:''|Saq Imtiaz ( lewcid@gmail.com )|
|''Co-author:''|Loic Dachary|
|''Source:''|http://tw.lewcid.org/#WebDavPlugin|
|''Code Repository:''|http://tw.lewcid.org/svn/plugins|
|''Version:''|1.0|
|''Date:''|17/11/2007|
|''License:''|[[Creative Commons Attribution-ShareAlike 3.0 License|http://creativecommons.org/licenses/by-sa/3.0/]]|
|''~CoreVersion:''|2.2.3|

***/
// /%
//!BEGIN-PLUGIN-CODE
DAV = {
	run : function(type,u,data,cb,params,headers){
		var callback = function(status,params,responseText,url,xhr) {
			url = url.indexOf("nocache=") < 0 ? url : url.substring(0,url.indexOf("nocache=")-1);
			if(params.length){
				params.shift().apply(this,[status,params,responseText,url,xhr]);
			}
		};	
		params = params||[];
		params.unshift(cb);		
		var r = doHttp.apply(this,[type,u,data,null,null,null,callback,params,headers]);
		if (typeof r == "string")
			alert(r);
		return r;
	},
	
	get : function(url,cb,params){
		return DAV.run("GET",url,null,cb,params,null);
	},

	put : function(url,cb,params,data) {
		return DAV.run("PUT",url,data,cb,params,null);
	},

	move : function(url,cb,params,destination) {
		return DAV.run("MOVE",url,null,cb,params,{"Destination":destination,"Overwrite":"T"});
	}, 

	copy : function(url,cb,params,destination) {
		return DAV.run("COPY",url,null,cb,params,{"Destination":destination,"Overwrite":"T","Depth":0});
	},
	
	propfind : function(url,cb,params,prop,depth){	// !!!
		var xml = '<?xml version="1.0" encoding="UTF-8" ?>' +
			'<D:propfind xmlns:D="DAV:">' +
			'<D:prop>'+
			'<D:'+prop+'/>'+
			'</D:prop>'+
			'</D:propfind>';
		return DAV.run("PROPFIND",url,xml,cb,params,{"Content-type":"text/xml","Depth":depth?depth:0});
	},
	
	makeDir : function(url,cb,params){
		return DAV.run("MKCOL",url,null,cb,params,null);
	},

	options : function(url,cb,params){
		return DAV.run("OPTIONS",url,null,cb,params,null);
	},
	
	safeput : function(url,cb,params,data){
		firstcb = function(status,p,responseText,u,xhr){
			if(status)
				DAV.move(u,cb,p,u.replace("-davsavingtemp",""));
			else
				cb.apply(firstcb,arguments);
		};
		return DAV.put(url+"-davsavingtemp",firstcb,params,data);
	}	
};

config.DavSaver = {
	defaultFileName : 'index.html',
	messages : {
		startSaveMessage : 'saving to server...',
		endSaveMessage : 'TiddlyWiki successfuly saved to server',
		overwriteNewerPrompt : 'The remote file has changed since you last loaded or saved it.\nDo you wish to overwrite it?',
		getModDateError : "Could not get last modified date",
		raceError: "Save failed because the remote file is newer than the one you are trying to save"
	},
	errors:{
		raceconflict : 'The save failed because your file is out of date',
		getlastmodified : 'The save was aborted because the last modified date of the file could not be retrieved',
		davenabled : 'The server does not support WebDav',
		saverss : 'There was an error saving the rss file, the save was aborted',
		saveempty: 'There was an error saving the empty file, the save was aborted',
		savemain : 'Save failed! There was an error saving the main TW file',
		savebackup: 'Save failed! There was an error creating a backup file',
		makebackupdir: 'Save failed! The backup directory could not be created'		
	},
	timestamp: new Date().toGMTString(),
	orig_saveChanges: saveChanges,
	saver : null
};

DavSaver = function(){
	
	this.Q = [];	

	this.reset = function(){
		config.DavSaver.saver = null;
	};
	this.runQ = function(){
		if(this.Q.length){
			this.Q.shift().apply(this,arguments);
		}
		else
			this.reset();
	};
	this.posDiv = null;
	this.original = null;
	
	this.getOriginalPath = function(){
		var p = document.location.toString();
		p = convertUriToUTF8(p,config.options.txtFileSystemCharSet);
		var argPos = p.indexOf("?");
		if(argPos != -1)
			p = p.substr(0,argPos);
		var hashPos = p.indexOf("#");
		if(hashPos != -1)
			p = p.substr(0,hashPos);		
		if (p.charAt(p.length-1) == "/")
			p = p + config.DavSaver.defaultFileName;
		return p;
	};
	
	this.originalPath = this.getOriginalPath();
	this.backupPath = null;
	this.emptyPath = null;
	this.rssPath = null;
	this.throwError = function(er){
		clearMessage();
		this.reset();
		alert(config.DavSaver.errors[er]);   //clear message, reset and delete
	};
};

DavSaver.prototype.getOriginal = function(){
	var	callback = function(status,params,original,url,xhr) {
		var that = params[0];
		if(status){
			var p = that.posDiv = locateStoreArea(original);
			if(!p || (p[0] == -1) || (p[1] == -1)) {
				alert(config.messages.invalidFileError.format([url]));
				return;
			}
			that.original = original;
			that.runQ();
		}
		else
			that.throwError('getOriginal');
	};
	
	DAV.get(this.originalPath,callback,[this]);	
};

DavSaver.prototype.checkRace = function(){
	var callback = function(status,params,responseText,url,xhr){
		var that = params[0];
		if(status){
			var lastmod = responseText.match(/<(\w*?):getlastmodified>(.*?)<\/\1:getlastmodified>/)[2];
			if(Date.parse(lastmod) > Date.parse(config.DavSaver.timestamp)){
				if (confirm(config.DavSaver.messages.overwriteNewerPrompt))
					that.runQ();
				else
					that.throwError('raceconflict');
			}
			else	
				that.runQ();
		}
		else
			that.throwError('getlastmodified');
	};
	
	DAV.propfind(this.originalPath,callback,[this],"getlastmodified",0);	
};

DavSaver.prototype.isDavEnabled = function(){
	var callback = function(status,params,responseText,url,xhr){
		that = params[0];
		if(status && !! xhr.getResponseHeader("DAV")){
			that.runQ();
			}
		else
			that.throwError('davenabled');
	};
	DAV.options(this.originalPath,callback,[this]);		
};

DavSaver.prototype.saveRss = function(){
	var callback = function(status,params,responseText,url,xhr){
		var that = params[0];
		if(status){
			displayMessage(config.messages.rssSaved,that.rssPath);
			that.runQ();
		}
		else
			that.throwError('saverss');
	};
	var u = this.originalPath;
	var rssPath = this.rssPath = u.substr(0,u.lastIndexOf(".")) + ".xml";
	DAV.safeput(rssPath,callback,[this],convertUnicodeToUTF8(generateRss()));	
};

DavSaver.prototype.saveEmpty = function(){
	var callback = function(status,params,responseText,url,xhr){
		var that = params[0];
		if(status){
			displayMessage(config.messages.emptySaved,that.emptyPath);
			that.runQ();
		}
		else
			that.throwError('saveempty');
	};
	var u = this.originalPath;
	var emptyPath,p;
	if((p = u.lastIndexOf("/")) != -1)
		emptyPath = u.substr(0,p) + "/empty.html";
	else
		emptyPath = u + ".empty.html";
	this.emptyPath = emptyPath;
	var empty = this.original.substr(0,this.posDiv[0] + startSaveArea.length) + this.original.substr(this.posDiv[1]);
	DAV.safeput(emptyPath,callback,[this],empty);		
};

DavSaver.prototype.saveMain = function(){
	var callback = function(status,params,responseText,url,xhr){
		var that = params[0];
		if(status){
			config.DavSaver.timestamp = xhr.getResponseHeader('Date');
			displayMessage(config.messages.mainSaved,that.originalPath);
			store.setDirty(false);
			that.runQ();
		}
		else
			that.throwError('savemain');		
	};
	var revised = updateOriginal(this.original,this.posDiv);
	DAV.safeput(this.originalPath,callback,[this],revised);
};

DavSaver.prototype.saveBackup = function(){	
	var callback = function(status,params,responseText,url,xhr){
		var that = params[0];
		if(status){
			clearMessage();
			displayMessage(config.messages.backupSaved,that.backupPath);
			that.runQ();
		}
		else
			that.throwError('savebackup');
	};
			
	var backupPath = this.backupPath = getBackupPath(this.originalPath);
	DAV.copy(this.originalPath,callback,[this],this.backupPath);		
};

DavSaver.prototype.makeBackupDir = function(){
	var callback = function(status,params,responseText,url,xhr){
		var that = params[0];
		if(status)
			that.runQ();
		else
			that.throwError('makebackupdir');
	};
	var u = getBackupPath(this.originalPath);
	var backupDirPath = u.substr(0,u.lastIndexOf("/"));
	DAV.makeDir(backupDirPath,callback,[this]); 
};

DavSaver.prototype.save = function(onlyIfDirty,tiddlers){
	if(onlyIfDirty && !store.isDirty())
		return;
	clearMessage();
	displayMessage(config.DavSaver.messages.startSaveMessage);
	var Q = this.Q =[];
	Q.push(this.isDavEnabled);
	Q.push(this.getOriginal);
	Q.push(this.checkRace);
	if (config.options.chkSaveBackups){
		if (config.options.txtBackupFolder!='')
			Q.push(this.makeBackupDir);
		Q.push(this.saveBackup);
	}
	Q.push(this.saveMain);
	if (config.options.chkGenerateAnRssFeed)
		Q.push(this.saveRss);
	if (config.options.chkSaveEmptyTemplate)
		Q.push(this.saveEmpty);
	//Q.push(this.reset);
	this.runQ();
};

window.saveChanges = function(onlyIfDirty,tiddlers)
{	
	var c = config.DavSaver;
	if (document.location.protocol.toString() == "http:"){
		var saver = c.saver = new DavSaver();
		saver.save(onlyIfDirty,tiddlers);		
	}
	else
		return c.orig_saveChanges(onlyIfDirty,tiddlers);
};
//!END-PLUGIN-CODE
// %/