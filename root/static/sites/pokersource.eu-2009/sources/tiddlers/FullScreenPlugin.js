/***
!!custom version for jpoker

|Name|FullScreenPlugin|
|Created by|SaqImtiaz|
|Location|http://tw.lewcid.org/#FullScreenPlugin|
|Version|1.1|
|Requires|~TW2.x|
!Description:
Toggle between viewing tiddlers fullscreen and normally. Very handy for when you need more viewing space.

!Demo:
Click the ↕ button in the toolbar for this tiddler. Click it again to turn off fullscreen.

!Installation:
Copy the contents of this tiddler to your TW, tag with systemConfig, save and reload your TW.
Edit the ViewTemplate to add the fullscreen command to the toolbar.

!History:
*25-07-06: ver 1.1
*20-07-06: ver 1.0

!Code
***/
//{{{
var lewcidFullScreen = false;

config.commands.fullscreen =
{
            text:" ↕ ",
            tooltip:"Fullscreen mode"
};

config.commands.fullscreen.handler = function (event,src,title)
{
            if (lewcidFullScreen == false)
               {
                lewcidFullScreen = true;
                setStylesheet('#sidebar, #header, #stickyfooter,#push, #mainMenu{display:none;} #displayArea{margin:0em 0 0 0 !important;}',"lewcidFullScreenStyle");
               }
            else
               {
                lewcidFullScreen = false;
                setStylesheet(' ',"lewcidFullScreenStyle");
               }
}

config.macros.fullscreen={};
config.macros.fullscreen.handler =  function(place,macroName,params,wikifier,paramString,tiddler)
{
        var label = params[0]||" ↕ ";
        var tooltip = params[1]||"Fullscreen mode";
        createTiddlyButton(place,label,tooltip,config.commands.fullscreen.handler);
}

var lewcid_fullscreen_closeTiddler = Story.prototype.closeTiddler;
Story.prototype.closeTiddler =function(title,animate,slowly)
{
           lewcid_fullscreen_closeTiddler.apply(this,arguments);
           if (story.isEmpty() && lewcidFullScreen == true)
              config.commands.fullscreen.handler();
}


Slider.prototype.lewcidStop = Slider.prototype.stop;
Slider.prototype.stop = function()
{
           this.lewcidStop();
           if (story.isEmpty() && lewcidFullScreen == true)
              config.commands.fullscreen.handler();
}
//}}}
