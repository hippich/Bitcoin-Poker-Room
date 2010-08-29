//{{{
config.macros.publisher = {

	startMode : 'PublicMode',

	currentMode : 'PublicMode',
	
	spm : false,
	
	defaultColorPalette : config.shadowTiddlers['ColorPalette'],
	
	readOnly : false,

	handler: function(place,macroName,params,wikifier,paramString,tiddler){
		if(!(store.getTiddlerSlice(this.startMode,'readOnly') == 'true') || (params[0] =='force')) {
			var modeTiddlers = store.getTaggedTiddlers('publisherMode');
			var modes = [];
			for(var i=0;i<modeTiddlers.length;i++) {
				var modeName = store.getTiddlerSlice(modeTiddlers[i].title,'Name') || modeTiddlers[i].title;
				modes.push({name : modeTiddlers[i].title, caption: modeName + ' mode '});
			}
			var sel = createTiddlyDropDown(place,this.onchangeselect,modes,this.currentMode);
			addClass(sel,'publisher');
		}
	},
	
	onchangeselect : function(e) {
		config.macros.publisher.changeMode(this.value)
		return false;
	},
	
	changeMode : function(mode,noSwitchTheme) {
		this.currentMode = mode;
		this.spm = store.getTiddlerSlice(mode,'SinglePageMode') == 'true' ? true : false;
		this.readOnly = store.getTiddlerSlice(mode,'readOnly') == 'true' ? true : false;
		this.toggleReadOnly();
		this.toggleSPM();
		this.toggleColorPalette(mode);
		if(!noSwitchTheme)
			story.switchTheme(mode);		
	},
	
	
	toggleColorPalette : function(mode){
		if(store.getTiddler('ColorPalette'))
			return;
		var customPalette = store.getTiddlerSlice(mode,'ColorPalette');
		if(customPalette && (store.tiddlerExists(customPalette) || store.isShadowTiddler(customPalette))){
			config.shadowTiddlers['ColorPalette'] = store.getTiddlerText(customPalette);
		}
		else
			config.shadowTiddlers['ColorPalette'] = this.defaultColorPalette;
		
	},
	
	toggleReadOnly : function(){
		if (this.readOnly){
			config.options.chkHttpReadOnly = true;
			readOnly = true;
		}
		else{
			config.options.chkHttpReadOnly =false;
			readOnly = false;
		}
	},
	
	toggleSPM : function(){
		config.options.chkSinglePageMode = (this.spm)? true : false;
		config.options.chkTopOfPageMode = (this.spm)? true : false;
	},
		
	start : function(){
		config.options.txtTheme = this.startMode;
		showBackstage = store && store.getTiddlerSlice(this.startMode,'showBackstage') == 'false' ? false : showBackstage;
	}

};

config.macros.publisher.start();

Story.prototype.old_publisher_switchTheme = Story.prototype.switchTheme;
Story.prototype.switchTheme = function(theme){
	if(startingUp)
		config.macros.publisher.changeMode(theme,true);
	this.old_publisher_switchTheme(theme);
};

backstage.old_publisher_init = backstage.init;
backstage.init = function(){
	this.old_publisher_init.apply(this,arguments);
	wikify("<<publisher>>",document.getElementById("backstageToolbar"));
};

config.paramifiers.mode = {
	onconfig: function(mode) {
		if (!store.tiddlerExists(mode) && store.tiddlerExists(mode+'Mode'))
           mode += 'Mode';   
		config.macros.publisher.startMode = mode;
		if(store.getTiddlerSlice(mode,'showBackstage') == 'true')
			showBackstage = true;
		story.switchTheme(mode);	
	}
};
//}}}