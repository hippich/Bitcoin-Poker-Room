/***
|''Name:''|TiddlerSubtitleTweak|
|''Description:''||
|''Author:''|Saq Imtiaz ( lewcid@gmail.com )|
|''Source:''|http://tw.lewcid.org/#TiddlerSubtitleTweak|
|''Code Repository:''|http://tw.lewcid.org/svn/plugins|
|''Version:''|2.0 beta|
|''Date:''||
|''License:''|[[Creative Commons Attribution-ShareAlike 3.0 License|http://creativecommons.org/licenses/by-sa/3.0/]]|
|''~CoreVersion:''|2.2.3|
!!Usage:
*
***/
// /%
//!BEGIN-PLUGIN-CODE
//{{{
window.old_website_getTiddlyLinkInfo = window.getTiddlyLinkInfo;
window.getTiddlyLinkInfo = function(title,currClasses)
{
	var x = window.old_website_getTiddlyLinkInfo.apply(this,arguments);
	x.subTitle = title;
	return x;
}
//}}}
//!END-PLUGIN-CODE
// %/