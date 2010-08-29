/***
|''Name:''|ActiveMenuLinksPlugin|
|''Description:''||
|''Author:''|Saq Imtiaz ( lewcid@gmail.com )|
|''Source:''|http://tw.lewcid.org/#ActiveMenuLinksPlugin|
|''Code Repository:''|http://tw.lewcid.org/svn/plugins|
|''Version:''|2.0 pre-release|
|''Date:''||
|''License:''|[[Creative Commons Attribution-ShareAlike 3.0 License|http://creativecommons.org/licenses/by-sa/3.0/]]|
|''~CoreVersion:''|2.2.3|
!!Usage:
*
***/ 
// /%
//!BEGIN-PLUGIN-CODE
Story.prototype.refreshTiddler_activelink = Story.prototype.refreshTiddler;
Story.prototype.refreshTiddler = function (title,template,force)
{
	var theTiddler = Story.prototype.refreshTiddler_activelink.apply(this,arguments);
	if (!theTiddler)
		return theTiddler;
	this.highlightActiveLinks();
	return theTiddler;
}

Story.prototype.highlightActiveLinks = function()
{
	var menu = document.getElementById("menu");
	var links = menu.getElementsByTagName("a");
	for (var i=0; i<links.length; i++){
		if (!links[i].getAttribute("tiddlyLink"))
			return;
		if (document.getElementById(this.idPrefix+(links[i].getAttribute("tiddlylink"))))
			addClass(links[i],"activeLink");
		else
			removeClass(links[i],"activeLink");
	}
}

Story.prototype.closeTiddler_activelink = Story.prototype.closeTiddler;
Story.prototype.closeTiddler = function(title,animate,unused)
{
	this.closeTiddler_activelink.apply(this,arguments);
	this.highlightActiveLinks();
}
//!END-PLUGIN-CODE
// %/