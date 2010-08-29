/***
|''Name:''|JapaneseTranslation|
|''Description:''|Translation of TiddlyWiki into Japanese|
|''Author:''|FURUKAWA, Masashi(Zephyr)|
|''Source:''|http://flow.dip.jp/mt/archives/u/twmemo.html#JapaneseTranslation|
|''Version:''|0.3.0|
|''Date:''|Mar. 26, 2007|
|''License:''|[[Creative Commons Attribution-ShareAlike 2.1 Japan License|http://creativecommons.org/licenses/by-sa/2.1/jp/]]|
|''~CoreVersion:''|2.1.3|
TiddlyWikiを日本語化するプラグインです。
http://trac.tiddlywiki.org/tiddlywiki/wiki/Translations に書いてあるように、svn.tiddlywiki.orgからlocale.en.jsを持ってきて作り直しました。
しかし、svn版は既に現行バージョンとは違うようで、エラーが出たり明らかに使われていない所はコメントや未訳のままにしてあります。
以前の日本語化プラグインはOldJapaneseTranslationにあります。
元のライセンスがCCのBY-SAなので、それに相当する日本語版のCCライセンスにしてあります。また、原著作者のクレジットもそのまま残してあります。
***/

/***
|''Name:''|EnglishTranslationPlugin|
|''Description:''|Translation of TiddlyWiki into English|
|''Author:''|MartinBudden (mjbudden (at) gmail (dot) com)|
|''Source:''|www.???.com |
|''Subversion:''|http://svn.tiddlywiki.org/Trunk/association/locales/core/en/locale.en.js |
|''Version:''|0.3.0|
|''Date:''|Mar 4, 2007|
|''Comments:''|Please make comments at http://groups.google.co.uk/group/TiddlyWikiDev |
|''License:''|[[Creative Commons Attribution-ShareAlike 2.5 License|http://creativecommons.org/licenses/by-sa/2.5/ ]]|
|''~CoreVersion:''|2.1.3|
***/

/*{{{*/
//--
//-- Translateable strings
//--

// Strings in "double quotes" should be translated; strings in 'single quotes' should be left alone

config.locale = "ja"; // W3C language tag

if (config.options.txtUserName == "YourName")
	merge(config.options,{
		txtUserName: "お名前"});

config.tasks = {
	save: {text: "save", tooltip: "Save your changes to this TiddlyWiki", action: saveChanges},
	sync: {text: "同期", tooltip: "他のTiddlyWikiファイルやサーバと同期をとります", content: '<<sync>>'},
	importTask: {text: "取り込み", tooltip: "他のTiddlyWikiファイルやサーバからtiddlerやプラグインを取り込みます", content: '<<importTiddlers>>'},
	tweak: {text: "tweak", tooltip: "Tweak the appearance and behaviour of TiddlyWiki", content: '<<options>>'},
	plugins: {text: "プラグイン", tooltip: "プラグインを管理します", content: '<<plugins>>'}
};

// Options that can be set in the options panel and/or cookies
/*
config.optionsDesc = {
	txtUserName: "Username for signing your edits",
	chkRegExpSearch: "Enable regular expressions for searches",
	chkCaseSensitiveSearch: "Case-sensitive searching",
	chkAnimate: "Enable animations",
	chkSaveBackups: "Keep backup file when saving changes",
	chkAutoSave: "Automatically save changes",
	chkGenerateAnRssFeed: "Generate an RSS feed when saving changes",
	chkSaveEmptyTemplate: "Generate an empty template when saving changes",
	chkOpenInNewWindow: "Open external links in a new window",
	chkToggleLinks: "Clicking on links to open tiddlers causes them to close",
	chkHttpReadOnly: "Hide editing features when viewed over HTTP",
	chkForceMinorUpdate: "Don't update modifier username and date when editing tiddlers",
	chkConfirmDelete: "Require confirmation before deleting tiddlers",
	chkInsertTabs: "Use the tab key to insert tab characters instead of moving between fields",
	chkShowTiddlerDetails: "Always show the tiddler details panel when displaying a tiddler",
	txtBackupFolder: "Name of folder to use for backups",
	txtMaxEditRows: "Maximum number of rows in edit boxes",
	txtFileSystemCharSet: "Default character set for saving changes"
	};
*/

merge(config.messages,{
	customConfigError: "プラグインの読み込みで問題が発生しました。詳細はPluginManager参照",
	pluginError: "エラー: %0",
	pluginDisabled: "'systemConfigDisable'タグにより実行が禁止されました",
	pluginForced: "'systemConfigForce'タグにより強制的に実行されました",
	pluginVersionError: "このプラグインの実行にはより新しいバージョンのTiddlyWikiが必要です",
	nothingSelected: "選択されていません。一つ以上選択してください",
	savedSnapshotError: "このTiddlyWikiは正常に保存されていません。詳細は http://www.tiddlywiki.com/#DownloadSoftware をご覧ください",
	subtitleUnknown: "",
	undefinedTiddlerToolTip: "'%0'tiddlerはまだ作成されていません",
	shadowedTiddlerToolTip: "'%0'tiddlerはまだ作成されていませんが、隠し既定値があります",
	tiddlerLinkTooltip: "%0 - %1, %2",
	externalLinkTooltip: "(外部リンク) %0",
	noTags: "タグの付いたtiddlerはありません",
	notFileUrlError: "変更を保存するには、このTiddlyWikiをファイルに保存(ダウンロード)する必要があります",
	cantSaveError: "変更を保存できません。以下の理由が考えられます:\n- ブラウザが保存に対応していない (Firefox, Internet Explorer, Safari そして Opera は正しく設定されていれば保存できます)\n- TiddlyWikiファイルのPath名に不正な文字が含まれている\n- TiddlyWikiファイルを移動または名前を変更された",
	invalidFileError: "元のファイル '%0' は妥当なTiddlyWikiのファイルではありません",
	backupSaved: "バックアップを保存しました",
	backupFailed: "バックアップの保存に失敗しました",
	rssSaved: "RSSフィードを保存しました",
	rssFailed: "RSSフィードの保存に失敗しました",
	emptySaved: "空テンプレートを保存しました",
	emptyFailed: "空テンプレートの保存に失敗しました",
	mainSaved: "TiddlyWikiファイルを保存しました",
	mainFailed: "TiddlyWikiファイルの保存に失敗しました。変更内容は保存されていません",
	macroError: "マクロ<<%0>>でエラー",
	macroErrorDetails: "マクロ<<%0>>実行中にエラー発生:\n%1",
	missingMacro: "マクロがありません",
	overwriteWarning: "'%0'tiddlerは既に存在します。OKで上書きします",
	unsavedChangesWarning: "WARNING! TiddlyWikiの変更が保存されていません\n\nOKで保存します\nCANCELで変更を破棄します",
	confirmExit: "--------------------------------\n\nTiddlyWikiの変更が保存されていません。このまま続けると変更が失われます\n\n--------------------------------",
	saveInstructions: "SaveChanges",
	unsupportedTWFormat: "TiddlyWiki書式 '%0' は未サポートです",
	tiddlerSaveError: "tiddler '%0' 保存時にエラー",
	tiddlerLoadError: "tiddler '%0' 読み込み時にエラー",
	wrongSaveFormat: "保存書式 '%0' で保存できません。標準書式で保存します",
	invalidFieldName: "%0 は不正なファイル名です",
	fieldCannotBeChanged: "領域 '%0' を変更できません"});

merge(config.messages.messageClose,{
	text: "確認",
	tooltip: "このメッセージを閉じます"});

/*
config.messages.backstage = {
	open: {text: "backstage", icon: "?", iconIE: "←", tooltip: "Open the backstage area to perform authoring and editing tasks"},
	close: {text: "close", icon: "?", iconIE: "→", tooltip: "Close the backstage area"},
	prompt: "backstage: "
};

config.messages.listView = {
	tiddlerTooltip: "Click for the full text of this tiddler",
	previewUnavailable: "(preview not available)"
};
*/

config.messages.dates.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November","December"];
config.messages.dates.days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
config.messages.dates.shortMonths = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
config.messages.dates.shortDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
// suffixes for dates, eg "1st","2nd","3rd"..."30th","31st"
config.messages.dates.daySuffixes = ["st","nd","rd","th","th","th","th","th","th","th",
		"th","th","th","th","th","th","th","th","th","th",
		"st","nd","rd","th","th","th","th","th","th","th",
		"st"];
config.messages.dates.am = "am";
config.messages.dates.pm = "pm";

merge(config.views.wikified.tag,{
	labelNoTags: "タグ無し",
	labelTags: "タグ: ",
	openTag: "'%0'タグを開く",
	tooltip: "'%0'タグの付いたtiddlerを表示",
	openAllText: "すべて開く",
	openAllTooltip: "以下のtiddlerをすべて開く",
	popupNone: "'%0'タグの付いたtiddlerは他にありません"});

merge(config.views.wikified,{
	defaultText: "'%0'はまだ作成されていません。ダブルクリックで作成できます",
	defaultModifier: "(missing)",
	shadowModifier: "(built-in shadow tiddler)",
	dateFormat: "YYYY年MM月DD日",
	createdPrompt: "作成"});

merge(config.views.editor,{
	tagPrompt: "タグはスペース区切りで入力します。必要なら[[二重の 角カッコで 囲みます]]。既存の",
	defaultText: "'%0'の内容を入力してください"});

merge(config.views.editor.tagChooser,{
	text: "タグ",
	tooltip: "既存のタグを選択して追加します",
	popupNone: "タグが定義されていません",
	tagTooltip: "'%0'タグを追加"});

/*
merge(config.messages,{
	sizeTemplates:
		[
		{unit: 1024*1024*1024, template: "%0\u00a0GB"},
		{unit: 1024*1024, template: "%0\u00a0MB"},
		{unit: 1024, template: "%0\u00a0KB"},
		{unit: 1, template: "%0\u00a0B"}
		]});
*/

merge(config.macros.search,{
	label: "検索",
	prompt: "このTiddlyWiki内を検索します",
	accessKey: "F",
	successMsg: "%0件のtiddlerで%1が見つかりました",
	failureMsg: "%0は見つかりませんでした"});

merge(config.macros.tagging,{
	label: "タグ付け: ",
	labelNotTag: "タグ付け無し",
	tooltip: "'%0'タグを付けたtiddler一覧"});

merge(config.macros.timeline,{
	dateFormat: "YYYY年MM月DD日"});

merge(config.macros.allTags,{
	tooltip: "'%0'タグの付いたtiddlerを表示",
	noTags: "タグの付いたtiddlerはありません"});

config.macros.list.all.prompt = "アルファベット順のtiddler一覧";
config.macros.list.missing.prompt = "リンクされているが定義されていないtiddler一覧";
config.macros.list.orphans.prompt = "リンクされていないtiddler一覧";
config.macros.list.shadowed.prompt = "既定の隠しtiddler";
// config.macros.list.touched.prompt = "Tiddlers that have been modified locally";

merge(config.macros.closeAll,{
	label: "すべて閉じる",
	prompt: "表示されているすべてのtiddler(編集中以外)を閉じます"});

merge(config.macros.permaview,{
	label: "現状URL",
	prompt: "表示されているすべてのtiddlerを取り出すURL(permaview)"});

merge(config.macros.saveChanges,{
	label: "保存",
	prompt: "すべてのtiddlerを保存します",
	accessKey: "S"});

merge(config.macros.newTiddler,{
	label: "新規作成",
	prompt: "新しいtiddlerを作成します",
	title: "New Tiddler",
	accessKey: "N"});

merge(config.macros.newJournal,{
	label: "新規日報",
	prompt: "日時がタイトルの新しいtiddlerを作成します",
	accessKey: "J"});

/*
merge(config.macros.options,{
	wizardTitle: "Tweak advanced options",
	step1Title: "These options are saved in cookies in your browser",
	step1Html: "<input type='hidden' name='markList'></input><br><input type='checkbox' checked='false' name='chkHidden'>Show hidden options</input>",
	unknownDescription: "//(hidden)//",
	listViewTemplate: {
		columns: [
			{name: 'Option', field: 'option', title: "Option", type: 'String'},
			{name: 'Description', field: 'description', title: "Description", type: 'WikiText'},
			{name: 'Name', field: 'name', title: "Name", type: 'String'}
			],
		rowClasses: [
			{className: 'lowlight', field: 'lowlight'} 
			]}
	});
*/

merge(config.macros.plugins,{
	skippedText: "(このプラグインは起動後に追加されたので実行していません)",
	noPluginText: "プラグインがインストールされていません",
	confirmDeleteText: "これらのプラグインを削除してよろしいですか:\n\n%0",
	listViewTemplate : {
		columns: [
			{name: 'Selected', field: 'Selected', rowName: 'title', type: 'Selector'},
			{name: 'Title', field: 'title', tiddlerLink: 'title', title: "Title", type: 'TiddlerLink'},
			{name: 'Forced', field: 'forced', title: "Forced", tag: 'systemConfigForce', type: 'TagCheckbox'},
			{name: 'Disabled', field: 'disabled', title: "Disabled", tag: 'systemConfigDisable', type: 'TagCheckbox'},
			{name: 'Executed', field: 'executed', title: "Loaded", type: 'Boolean', trueText: "Yes", falseText: "No"},
			{name: 'Error', field: 'error', title: "Status", type: 'Boolean', trueText: "Error", falseText: "OK"},
			{name: 'Log', field: 'log', title: "Log", type: 'StringList'}
			],
		rowClasses: [
			{className: 'error', field: 'error'},
			{className: 'warning', field: 'warning'}
			],
		actions: [
			{caption: "次の動作...", name: ''},
			{caption: "systemConfigタグを外す", name: 'remove'},
			{caption: "これらのtiddlerを削除する", name: 'delete'}
			]}
	});

merge(config.macros.toolbar,{
	moreLabel: "more",
	morePrompt: "Reveal further commands"
	});

merge(config.macros.refreshDisplay,{
	label: "再表示",
	prompt: "TiddlyWikiを再表示します"
	});

merge(config.macros.importTiddlers,{
	readOnlyWarning: "読み込み専用のTiddlyWikiには取り込めません。TiddlyWikiファイルをfile://のURLで開いてみてください",
	defaultPath: "http://www.tiddlywiki.com/index.html",
	fetchLabel: "取得",
	fetchPrompt: "TiddlyWikiファイルを取得します",
	fetchError: "TiddlyWikiファイルの取得に問題が発生しました",
	confirmOverwriteText: "これらのtiddlerを上書きしてよろしいですか:\n\n%0",
	wizardTitle: "他のTiddlyWikiファイルからtiddlerを取り込む",
	step1: "手順1: TiddlyWikiファイルの場所を指定",
	step1prompt: "URLまたはパス名を入力: ",
	step1promptFile: "...またはファイルを選択: ",
	step1promptFeeds: "...または既定のフィードを選択: ",
	step1feedPrompt: "選択...",
	step2: "手順2: TiddlyWikiファイル読み込み",
	step2Text: "%0 からファイルを読み込むまでお待ちください",
	step3: "手順3: 取り込むtiddlerの選択",
	step4: "%0個のtiddlerを取り込みました",
	step5: "完了",
	listViewTemplate: {
		columns: [
			{name: 'Selected', field: 'Selected', rowName: 'title', type: 'Selector'},
			{name: 'Title', field: 'title', title: "Title", type: 'String'},
			{name: 'Snippet', field: 'text', title: "Snippet", type: 'String'},
			{name: 'Tags', field: 'tags', title: "Tags", type: 'Tags'}
			],
		rowClasses: [
			],
		actions: [
			{caption: "次の動作...", name: ''},
			{caption: "これらのtiddlerを取り込む", name: 'import'}
			]}
	});

/*
merge(config.macros.sync,{
	listViewTemplate: {
		columns: [
			{name: 'Selected', field: 'selected', rowName: 'title', type: 'Selector'},
			{name: 'Tiddler', field: 'tiddler', title: "Tiddler", type: 'Tiddler'},
			{name: 'Server Type', field: 'serverType', title: "Server type", type: 'String'},
			{name: 'Server Host', field: 'serverHost', title: "Server host", type: 'String'},
			{name: 'Server Workspace', field: 'serverWorkspace', title: "Server workspace", type: 'String'},
			{name: 'Status', field: 'status', title: "Synchronisation status", type: 'String'},
			{name: 'Server URL', field: 'serverUrl', title: "Server URL", text: "View", type: 'Link'}
			],
		rowClasses: [
			],
		buttons: [
			{caption: "Sync these tiddlers", name: 'sync'}
			]},
	wizardTitle: "Synchronize with external servers and files",
	step1Title: "Choose the tiddlers you want to synchronize",
	step1Html: "<input type='hidden' name='markList'></input>", // DO NOT TRANSLATE
	syncLabel: "sync",
	syncPrompt: "Sync these tiddlers",
	hasChanged: "Changed while unplugged",
	hasNotChanged: "Unchanged while unplugged",
	syncStatusList: {
		none: {text: "...", color: "none"},
		changedServer: {text: "Changed on server", color: "#80ff80"},
		changedLocally: {text: "Changed while unplugged", color: "#80ff80"},
		changedBoth: {text: "Changed while unplugged and on server", color: "#ff8080"},
		notFound: {text: "Not found on server", color: "#ffff80"},
		putToServer: {text: "Saved update on server", color: "#ff80ff"},
		gotFromServer: {text: "Retrieved update from server", color: "#80ffff"}
		}
	});

merge(config.macros.viewDetails,{
	label: "...",
	prompt: "Show additional information about this tiddler",
	hideLabel: "(hide details)",
	hidePrompt: "Hide this panel of additional information",
	emptyDetailsText: "There are no extended fields for this tiddler",
	listViewTemplate: {
		columns: [
			{name: 'Field', field: 'field', title: "Field", type: 'String'},
			{name: 'Value', field: 'value', title: "Value", type: 'String'}
			],
		rowClasses: [
			],
		buttons: [
			]}
	});
*/

merge(config.commands.closeTiddler,{
	text: "閉じる",
	tooltip: "このtiddlerを閉じます"});

merge(config.commands.closeOthers,{
	text: "他を閉じる",
	tooltip: "他のtiddlerを全て閉じます"});

merge(config.commands.editTiddler,{
	text: "編集",
	tooltip: "このtiddlerを編集します",
	readOnlyText: "閲覧",
	readOnlyTooltip: "このtiddlerの内容を閲覧します"});

merge(config.commands.saveTiddler,{
	text: "確定",
	tooltip: "編集内容を確定します"});

merge(config.commands.cancelTiddler,{
	text: "編集中止",
	tooltip: "編集内容を破棄します",
	warning: "'%0'の変更を破棄してよろしいですか?",
	readOnlyText: "終了",
	readOnlyTooltip: "通常のtiddler表示にします"});

merge(config.commands.deleteTiddler,{
	text: "削除",
	tooltip: "このtiddlerを削除します",
	warning: "'%0'を削除してよろしいですか?"});

merge(config.commands.permalink,{
	text: "URL",
	tooltip: "このtiddlerのURL(permalink)"});

merge(config.commands.references,{
	text: "参照一覧",
	tooltip: "このtiddlerのリンク元一覧を表示します",
	popupNone: "参照されていません"});

merge(config.commands.jump,{
	text: "移動",
	tooltip: "開いている他のtiddlerに移動"});

/*
merge(config.commands.syncing,{
	text: "syncing",
	tooltip: "Control synchronisation of this tiddler with a server or external file",
	currentlySyncing: "<div>Currently syncing via <span class='popupHighlight'>'%0'</span> to:</div><div>host: <span class='popupHighlight'>%1</span></div><div>workspace: <span class='popupHighlight'>%2</span></div>",
	notCurrentlySyncing: "Not currently syncing",
	captionUnSync: "Stop synchronising this tiddler",
	chooseServer: "Synchronise this tiddler with another server:",
	currServerMarker: "● ",
	notCurrServerMarker: "  "});
*/

merge(config.shadowTiddlers,{
	DefaultTiddlers: "[[TranslatedGettingStarted]]",
	MainMenu: "[[TranslatedGettingStarted]]",
	SiteTitle: "My TiddlyWiki",
	SiteSubtitle: "a reusable non-linear personal web notebook",
	SiteUrl: "http://www.tiddlywiki.com/",
	SideBarOptions: '<<search>><<closeAll>><<permaview>><<newTiddler>><<newJournal "YYYY年MM月DD日">><<saveChanges>><<slider chkSliderOptionsPanel OptionsPanel "設定 ≫" "TiddlyWikiの設定を変更します">>',
	SideBarTabs: '<<tabs txtMainTab "更新順" "更新順に表示する" TabTimeline "全部" "すべてのtiddler" TabAll "タグ" "タグ一覧" TabTags "詳細" "詳細" TabMore>>',
	TabTimeline: '<<timeline>>',
	TabAll: '<<list all>>',
	TabTags: '<<allTags excludeLists>>',
	TabMore: '<<tabs txtMoreTab "定義なし" "定義されていないtiddler" TabMoreMissing "リンク無し" "リンクされていないtiddler" TabMoreOrphans "隠し" "隠しtiddler" TabMoreShadowed>>',
	TabMoreMissing: '<<list missing>>',
	TabMoreOrphans: '<<list orphans>>',
	TabMoreShadowed: '<<list shadowed>>',
	PluginManager: '<<plugins>>',
	ImportTiddlers: '<<importTiddlers>>'});

/*}}}*/