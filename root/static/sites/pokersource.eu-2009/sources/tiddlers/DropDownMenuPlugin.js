/***
|''Name:''|DropDownMenuPlugin|
|''Description:''|Create dropdown menus from unordered lists|
|''Author:''|Saq Imtiaz ( lewcid@gmail.com )|
|''Source:''|http://tw.lewcid.org/#DropDownMenuPlugin|
|''Code Repository:''|http://tw.lewcid.org/svn/plugins|
|''Version:''|2.1|
|''Date:''|11/04/2007|
|''License:''|[[Creative Commons Attribution-ShareAlike 3.0 License|http://creativecommons.org/licenses/by-sa/3.0/]]|
|''~CoreVersion:''|2.2.5|

!!Usage:
* create a two-level unordered list using wiki syntax, and place {{{<<dropMenu>>}}} on the line after it.
* to create a vertical menu use {{{<<dropMenu vertical>>}}} instead.
* to assign custom classes to the list, just pass them as parameters to the macro {{{<<dropMenu className1 className2 className3>>}}}

!!Features:
*Supports just a single level of drop-downs, as anything more usually provides a poor experience for the user.
* Very light weight, about 1.5kb of JavaScript and 4kb of CSS.
* Comes with two built in css 'themes', the default horizontal and vertical. 

!!Customizing:
* to customize the appearance of the menu's, you can either add a custom class as described above or, you can edit the CSS via the StyleSheetDropDownMenu shadow tiddler.

!!Examples:
* [[DropDownMenuDemo]]

***/
// /%
//!BEGIN-PLUGIN-CODE
config.macros.dropMenu={

	dropdownchar: "\u25bc",

	handler : function(place,macroName,params,wikifier,paramString,tiddler){
		list = findRelated(place.lastChild,"UL","tagName","previousSibling");
		if (!list)
			return;
		addClass(list,"suckerfish");
		if (params.length){
			addClass(list,paramString);
		}
		this.fixLinks(list);
	},
	
	fixLinks : function(el){
		var els = el.getElementsByTagName("li");
		for(var i = 0; i < els.length; i++) {
			if(els[i].getElementsByTagName("ul").length>0){
				var link = findRelated(els[i].firstChild,"A","tagName","nextSibling");
				if(!link){
					var ih = els[i].firstChild.data;
					els[i].removeChild(els[i].firstChild);
					var d = createTiddlyElement(null,"a",null,null,ih+this.dropdownchar,{href:"javascript:;"});
					els[i].insertBefore(d,els[i].firstChild);
				}
				else{
					link.firstChild.data = link.firstChild.data + this.dropdownchar;
					removeClass(link,"tiddlyLinkNonExisting");
				}
			}
			els[i].onmouseover = function() {
				addClass(this, "sfhover");
			};
			els[i].onmouseout = function() {
				removeClass(this, "sfhover");
			};
		}
	}	
};

config.shadowTiddlers["StyleSheetDropDownMenuPlugin"] = 
	 "/*{{{*/\n"+
	 "/***** LAYOUT STYLES -  DO NOT EDIT! *****/\n"+
	 "ul.suckerfish, ul.suckerfish ul {\n"+
	 "	margin: 0;\n"+
	 "	padding: 0;\n"+
	 "	list-style: none;\n"+
	 "	line-height:1.4em;\n"+
	 "}\n\n"+
	 "ul.suckerfish  li {\n"+
	 "	display: inline-block; \n"+
	 "	display: block;\n"+
	 "	float: left; \n"+
	 "}\n\n"+
	 "ul.suckerfish li ul {\n"+
	 "	position: absolute;\n"+
	 "	left: -999em;\n"+
	 "}\n\n"+
	 "ul.suckerfish li:hover ul, ul.suckerfish li.sfhover ul {\n"+
	 "	left: auto;\n"+
	 "}\n\n"+
	 "ul.suckerfish ul li {\n"+
	 "	float: none;\n"+
	 "	border-right: 0;\n"+
	 "	border-left:0;\n"+
	 "}\n\n"+
	 "ul.suckerfish a, ul.suckerfish a:hover {\n"+
	 "	display: block;\n"+
	 "}\n\n"+
	 "ul.suckerfish li a.tiddlyLink, ul.suckerfish li a, #mainMenu ul.suckerfish li a {font-weight:bold;}\n"+
	 "/**** END LAYOUT STYLES *****/\n"+
	 "\n\n"+
	 "/**** COLORS AND APPEARANCE - DEFAULT *****/\n"+
	 "ul.suckerfish li a {\n"+
	 "	padding: 0.5em 1.5em;\n"+
	 "	color: #FFF;\n"+
	 "	background: #0066aa;\n"+
	 "	border-bottom: 0;\n"+
	 "	font-weight:bold;\n"+
	 "}\n\n"+
	 "ul.suckerfish li:hover a, ul.suckerfish li.sfhover a{\n"+
	 "	background: #00558F;\n"+
	 "}\n\n"+
	 "ul.suckerfish li:hover ul a, ul.suckerfish li.sfhover ul a{\n"+
	 "	color: #000;\n"+
	 "	background: #eff3fa;\n"+
	 "	border-top:1px solid #FFF;\n"+
	 "}\n\n"+
	 "ul.suckerfish ul li a:hover {\n"+
	 "	background: #e0e8f5;\n"+
	 "}\n\n"+
	 "ul.suckerfish li a{\n"+
	 "	width:9em;\n"+
	 "}\n\n"+
	 "ul.suckerfish ul li a, ul.suckerfish ul li a:hover{\n"+
	 "	display:inline-block;\n"+
	 "	width:9em;\n"+
	 "}\n\n"+
	 "ul.suckerfish li {\n"+
	 "	border-left: 1px solid #00558F;\n"+
	 "}\n"+
	 "/***** END COLORS AND APPEARANCE - DEFAULT *****/\n"+
	 "\n\n"+
	 "/***** LAYOUT AND APPEARANCE: VERTICAL *****/\n"+
	 "ul.suckerfish.vertical li{\n"+
	 "	width:10em;\n"+
	 "	border-left: 0px solid #00558f;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical ul li, ul.suckerfish.vertical li a, ul.suckerfish.vertical li:hover a, ul.suckerfish.vertical li.sfhover a {\n"+
	 "	border-left: 0.8em solid #00558f;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical li a, ul.suckerfish.vertical li:hover a, ul.suckerfish.vertical li.sfhover a,  ul.suckerfish.vertical li.sfhover a:hover{\n"+
	 "	width:8em;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical {\n"+
	 "	width:10em; text-align:left;\n"+
	 "	float:left;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical li a {\n"+
	 "	padding: 0.5em 1em 0.5em 1em;\n"+
	 "	border-top:1px solid  #fff;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical, ul.suckerfish.vertical ul {\n"+
	 "	line-height:1.4em;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical li:hover ul, ul.suckerfish.vertical li.sfhover ul { \n"+
	 "	margin: -2.4em 0 0 10.9em;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical li:hover ul li a, ul.suckerfish.vertical li.sfhover ul li a {\n"+
	 "	border: 0px solid #FFF;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical li:hover a, ul.suckerfish.vertical li.sfhover a{\n"+
	 "	padding-right:1.1em;\n"+
	 "}\n\n"+
	 "ul.suckerfish.vertical li:hover ul li, ul.suckerfish.vertical li.sfhover ul li {\n"+
	 "	border-bottom:1px solid  #fff;\n"+
	 "}\n\n"+
	 "/***** END LAYOUT AND APPEARANCE: VERTICAL *****/\n"+
	 "/*}}}*/";
store.addNotification("StyleSheetDropDownMenuPlugin",refreshStyles);
//!END-PLUGIN-CODE
// %/
