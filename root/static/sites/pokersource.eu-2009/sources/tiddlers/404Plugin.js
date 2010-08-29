/***
|''Name:''|404Plugin|
|''Description:''||
|''Author:''|Saq Imtiaz ( lewcid@gmail.com )|
|''Source:''|http://tw.lewcid.org/#404Plugin|
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
config.views.wikified.defaultText= "{{fourohfour{\nThe page '%0' doesn't exist.\n\n Try browsing or searching for what you were looking for.\n}}}";

setStylesheet(".fourohfour {text-align:center; font-family:'Lucida Grande', Verdana, Sans-Serif; font-size:1.2em; font-weight:bold; font-style:normal;}","404Styles");

//!END-PLUGIN-CODE
// %/