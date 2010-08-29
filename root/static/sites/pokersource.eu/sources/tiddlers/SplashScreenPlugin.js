/***
|''Name:''|SplashScreenPlugin|
|''Description:''|Provides a splash screen, while ~TiddlyWiki is loading|
|''Author:''|Saq Imtiaz ( lewcid@gmail.com )|
|''Source:''|http://tw.lewcid.org/#SplashScreenPlugin|
|''Code Repository:''|http://tw.lewcid.org/svn/plugins|
|''Version:''|2.0|
|''Date:''||
|''License:''|[[Creative Commons Attribution-ShareAlike 3.0 License|http://creativecommons.org/licenses/by-sa/3.0/]]|
|''~CoreVersion:''|2.2.2|

!! Installation:
# Copy the contents of this tiddler to your TiddlyWiki file.
# Tag it as systemConfig.
# Save and reload.
# Save a second time for the SplashScreen to be initialized.
# Next time you reload, the SplashScreen will be visible.

!! Upgrade
To upgrade from a previous version, less than 2.0:
# Delete the tiddler MarkupPreHead
# Delete the SplashScreenPlugin tiddler.
# Save and reload.
# Follow the installation instructions above.
***/
// /%
//!BEGIN-PLUGIN-CODE
window.lewcidAddToMarkupBlock = function(s,blockName,newChunk)
{
    var sep = s.indexOf("<!--%0-END-->".format([blockName]));
    return ( s.substring(0,sep) + "\n" + newChunk + "\n" + s.substring(sep) );
};

config.shadowTiddlers["SplashScreen"] = '<!--{{{-->\n<style type="text/css">#contentWrapper {display:none;}</style><div id="splashScreen" style="border: 3px solid #ccc; text-align: center; width: 320px; margin: 100px auto; padding: 50px; color:#000; font-size: 28px; font-family:Tahoma; background-color:#eee;"><b>[[SiteTitle]]</b> is loading<blink> ...</blink><br><br><span style="font-size: 14px; color:red;">Requires Javascript.</span></div>\n<!--}}}-->';

window.splashscreenAddToMarkupBlock = function(s)
{
	return lewcidAddToMarkupBlock(s,"PRE-BODY",store.getRecursiveTiddlerText("SplashScreen"));
};

updateMarkupBlock_old_splashscreen = window.updateMarkupBlock;
window.updateMarkupBlock = function (s,blockName,tiddlerName)
{
    s = updateMarkupBlock_old_splashscreen.apply(this,arguments);
    if (blockName == "PRE-BODY")
        s = splashscreenAddToMarkupBlock(s);
    return s;
};
//!END-PLUGIN-CODE
// %/