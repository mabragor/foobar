/*
 * Ext JS Library 0.20
 * Copyright(c) 2006-2008, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.namespace("Ext.air","Ext.sql");Ext.Template.prototype.compile=function(){var fm=Ext.util.Format;var _2=this.disableFormats!==true;var _3=0;var _4=[];var _5=this;var fn=function(m,_8,_9,_a,_b,s){if(_3!=_b){var _d={type:1,value:s.substr(_3,_b-_3)};_4.push(_d);}
_3=_b+m.length;if(_9&&_2){if(_a){var re=/^\s*['"](.*)["']\s*$/;_a=_a.split(/,(?=(?:[^"]*"[^"]*")*(?![^"]*"))/);for(var i=0,len=_a.length;i<len;i++){_a[i]=_a[i].replace(re,"$1");}
_a=[""].concat(_a);}else{_a=[""];}
if(_9.substr(0,5)!="this."){var _d={type:3,value:_8,format:fm[_9],args:_a,scope:fm};_4.push(_d);}else{var _d={type:3,value:_8,format:_5[_9.substr(5)],args:_a,scope:_5};_4.push(_d);}}else{var _d={type:2,value:_8};_4.push(_d);}
return m;};var s=this.html.replace(this.re,fn);if(_3!=(s.length-1)){var _12={type:1,value:s.substr(_3,s.length-_3)};_4.push(_12);}
this.compiled=function(_13){function applyValues(el){switch(el.type){case 1:return el.value;case 2:return(_13[el.value]?_13[el.value]:"");default:el.args[0]=_13[el.value];return el.format.apply(el.scope,el.args);}}
return _4.map(applyValues).join("");};return this;};Ext.Template.prototype.call=function(_15,_16,_17){return this[_15](_16,_17);};Ext.DomQuery=function(){var _18={},_19={},_1a={};var _1b=/\S/;var _1c=/^\s+|\s+$/g;var _1d=/\{(\d+)\}/g;var _1e=/^(\s?[\/>+~]\s?|\s|$)/;var _1f=/^(#)?([\w-\*]+)/;var _20=/(\d*)n\+?(\d*)/,_21=/\D/;function child(p,_23){var i=0;var n=p.firstChild;while(n){if(n.nodeType==1){if(++i==_23){return n;}}
n=n.nextSibling;}
return null;}
function next(n){while((n=n.nextSibling)&&n.nodeType!=1){}
return n;}
function prev(n){while((n=n.previousSibling)&&n.nodeType!=1){}
return n;}
function children(d){var n=d.firstChild,ni=-1;while(n){var nx=n.nextSibling;if(n.nodeType==3&&!_1b.test(n.nodeValue)){d.removeChild(n);}else{n.nodeIndex=++ni;}
n=nx;}
return this;}
function byClassName(c,a,v){if(!v){return c;}
var r=[],ri=-1,cn;for(var i=0,ci;ci=c[i];i++){if((" "+ci.className+" ").indexOf(v)!=-1){r[++ri]=ci;}}
return r;}
function attrValue(n,_35){if(!n.tagName&&typeof n.length!="undefined"){n=n[0];}
if(!n){return null;}
if(_35=="for"){return n.htmlFor;}
if(_35=="class"||_35=="className"){return n.className;}
return n.getAttribute(_35)||n[_35];}
function getNodes(ns,_37,_38){var _39=[],ri=-1,cs;if(!ns){return _39;}
_38=_38||"*";if(typeof ns.getElementsByTagName!="undefined"){ns=[ns];}
if(!_37){for(var i=0,ni;ni=ns[i];i++){cs=ni.getElementsByTagName(_38);for(var j=0,ci;ci=cs[j];j++){_39[++ri]=ci;}}}else{if(_37=="/"||_37==">"){var _40=_38.toUpperCase();for(var i=0,ni,cn;ni=ns[i];i++){cn=ni.children||ni.childNodes;for(var j=0,cj;cj=cn[j];j++){if(cj.nodeName==_40||cj.nodeName==_38||_38=="*"){_39[++ri]=cj;}}}}else{if(_37=="+"){var _40=_38.toUpperCase();for(var i=0,n;n=ns[i];i++){while((n=n.nextSibling)&&n.nodeType!=1){}
if(n&&(n.nodeName==_40||n.nodeName==_38||_38=="*")){_39[++ri]=n;}}}else{if(_37=="~"){for(var i=0,n;n=ns[i];i++){while((n=n.nextSibling)&&(n.nodeType!=1||(_38=="*"||n.tagName.toLowerCase()!=_38))){}
if(n){_39[++ri]=n;}}}}}}
return _39;}
function concat(a,b){if(b.slice){return a.concat(b);}
for(var i=0,l=b.length;i<l;i++){a[a.length]=b[i];}
return a;}
function byTag(cs,_49){if(cs.tagName||cs==document){cs=[cs];}
if(!_49){return cs;}
var r=[],ri=-1;_49=_49.toLowerCase();for(var i=0,ci;ci=cs[i];i++){if(ci.nodeType==1&&ci.tagName.toLowerCase()==_49){r[++ri]=ci;}}
return r;}
function byId(cs,_4f,id){if(cs.tagName||cs==document){cs=[cs];}
if(!id){return cs;}
var r=[],ri=-1;for(var i=0,ci;ci=cs[i];i++){if(ci&&ci.id==id){r[++ri]=ci;return r;}}
return r;}
function byAttribute(cs,_56,_57,op,_59){var r=[],ri=-1,st=_59=="{";var f=Ext.DomQuery.operators[op];for(var i=0,ci;ci=cs[i];i++){var a;if(st){a=Ext.DomQuery.getStyle(ci,_56);}else{if(_56=="class"||_56=="className"){a=ci.className;}else{if(_56=="for"){a=ci.htmlFor;}else{if(_56=="href"){a=ci.getAttribute("href",2);}else{a=ci.getAttribute(_56);}}}}
if((f&&f(a,_57))||(!f&&a)){r[++ri]=ci;}}
return r;}
function byPseudo(cs,_62,_63){return Ext.DomQuery.pseudos[_62](cs,_63);}
eval("var batch = 30803;");var key=30803;function nodup(cs){if(!cs){return[];}
var len=cs.length,c,i,r=cs,cj,ri=-1;if(!len||typeof cs.nodeType!="undefined"||len==1){return cs;}
var d=++key;cs[0]._nodup=d;for(i=1;c=cs[i];i++){if(c._nodup!=d){c._nodup=d;}else{r=[];for(var j=0;j<i;j++){r[++ri]=cs[j];}
for(j=i+1;cj=cs[j];j++){if(cj._nodup!=d){cj._nodup=d;r[++ri]=cj;}}
return r;}}
return r;}
function quickDiff(c1,c2){var _70=c1.length;if(!_70){return c2;}
var d=++key;for(var i=0;i<_70;i++){c1[i]._qdiff=d;}
var r=[];for(var i=0,len=c2.length;i<len;i++){if(c2[i]._qdiff!=d){r[r.length]=c2[i];}}
return r;}
function quickId(ns,_76,_77,id){if(ns==_77){var d=_77.ownerDocument||_77;return d.getElementById(id);}
ns=getNodes(ns,_76,"*");return byId(ns,null,id);}
function search(_7a,_7b,_7c){_7c=_7c||"select";var n=_7b||document;var q=_7a,_7f,lq;var tk=Ext.DomQuery.matchers;var _82=tk.length;var mm;var _84=q.match(_1e);if(_84&&_84[1]){_7f=_84[1].replace(_1c,"");q=q.replace(_84[1],"");}
while(_7a.substr(0,1)=="/"){_7a=_7a.substr(1);}
while(q&&lq!=q){lq=q;var tm=q.match(_1f);if(_7c=="select"){if(tm){if(tm[1]=="#"){n=quickId(n,_7f,_7b,tm[2]);}else{n=getNodes(n,_7f,tm[2]);}
q=q.replace(tm[0],"");}else{if(q.substr(0,1)!="@"){n=getNodes(n,_7f,"*");}}}else{if(tm){if(tm[1]=="#"){n=byId(n,null,tm[2]);}else{n=byTag(n,tm[2]);}
q=q.replace(tm[0],"");}}
while(!(mm=q.match(_1e))){var _86=false;for(var j=0;j<_82;j++){var t=tk[j];var m=q.match(t.re);if(m){switch(j){case 0:n=byClassName(n,null," "+m[1]+" ");break;case 1:n=byPseudo(n,m[1],m[2]);break;case 2:n=byAttribute(n,m[2],m[4],m[3],m[1]);break;case 3:n=byId(n,null,m[1]);break;case 4:return{firstChild:{nodeValue:attrValue(n,m[1])}};}
q=q.replace(m[0],"");_86=true;break;}}
if(!_86){throw"Error parsing selector, parsing failed at \""+q+"\"";}}
if(mm[1]){_7f=mm[1].replace(_1c,"");q=q.replace(mm[1],"");}}
return nodup(n);}
return{getStyle:function(el,_8b){return Ext.fly(el).getStyle(_8b);},compile:function(_8c,_8d){return function(_8e){return search(_8c,_8e,_8d);};},select:function(_8f,_90,_91){if(!_90||_90==document){_90=document;}
if(typeof _90=="string"){_90=document.getElementById(_90);}
var _92=_8f.split(",");var _93=[];for(var i=0,len=_92.length;i<len;i++){var p=_92[i].replace(_1c,"");if(!_18[p]){_18[p]=Ext.DomQuery.compile(p);if(!_18[p]){throw p+" is not a valid selector";}}
var _97=_18[p](_90);if(_97&&_97!=document){_93=_93.concat(_97);}}
if(_92.length>1){return nodup(_93);}
return _93;},selectNode:function(_98,_99){return Ext.DomQuery.select(_98,_99)[0];},selectValue:function(_9a,_9b,_9c){_9a=_9a.replace(_1c,"");if(!_1a[_9a]){_1a[_9a]=Ext.DomQuery.compile(_9a,"select");}
var n=_1a[_9a](_9b);n=n[0]?n[0]:n;var v=(n&&n.firstChild?n.firstChild.nodeValue:null);return((v===null||v===undefined||v==="")?_9c:v);},selectNumber:function(_9f,_a0,_a1){var v=Ext.DomQuery.selectValue(_9f,_a0,_a1||0);return parseFloat(v);},is:function(el,ss){if(typeof el=="string"){el=document.getElementById(el);}
var _a5=Ext.isArray(el);var _a6=Ext.DomQuery.filter(_a5?el:[el],ss);return _a5?(_a6.length==el.length):(_a6.length>0);},filter:function(els,ss,_a9){ss=ss.replace(_1c,"");if(!_19[ss]){_19[ss]=Ext.DomQuery.compile(ss,"simple");}
var _aa=_19[ss](els);return _a9?quickDiff(_aa,els):_aa;},matchers:[{re:/^\.([\w-]+)/,select:"n = byClassName(n, null, \" {1} \");"},{re:/^\:([\w-]+)(?:\(((?:[^\s>\/]*|.*?))\))?/,select:"n = byPseudo(n, \"{1}\", \"{2}\");"},{re:/^(?:([\[\{])(?:@)?([\w-]+)\s?(?:(=|.=)\s?['"]?(.*?)["']?)?[\]\}])/,select:"n = byAttribute(n, \"{2}\", \"{4}\", \"{3}\", \"{1}\");"},{re:/^#([\w-]+)/,select:"n = byId(n, null, \"{1}\");"},{re:/^@([\w-]+)/,select:"return {firstChild:{nodeValue:attrValue(n, \"{1}\")}};"}],operators:{"=":function(a,v){return a==v;},"!=":function(a,v){return a!=v;},"^=":function(a,v){return a&&a.substr(0,v.length)==v;},"$=":function(a,v){return a&&a.substr(a.length-v.length)==v;},"*=":function(a,v){return a&&a.indexOf(v)!==-1;},"%=":function(a,v){return(a%v)==0;},"|=":function(a,v){return a&&(a==v||a.substr(0,v.length+1)==v+"-");},"~=":function(a,v){return a&&(" "+a+" ").indexOf(" "+v+" ")!=-1;}},pseudos:{"first-child":function(c){var r=[],ri=-1,n;for(var i=0,ci;ci=n=c[i];i++){while((n=n.previousSibling)&&n.nodeType!=1){}
if(!n){r[++ri]=ci;}}
return r;},"last-child":function(c){var r=[],ri=-1,n;for(var i=0,ci;ci=n=c[i];i++){while((n=n.nextSibling)&&n.nodeType!=1){}
if(!n){r[++ri]=ci;}}
return r;},"nth-child":function(c,a){var r=[],ri=-1;var m=_20.exec(a=="even"&&"2n"||a=="odd"&&"2n+1"||!_21.test(a)&&"n+"+a||a);var f=(m[1]||1)-0,l=m[2]-0;for(var i=0,n;n=c[i];i++){var pn=n.parentNode;if(batch!=pn._batch){var j=0;for(var cn=pn.firstChild;cn;cn=cn.nextSibling){if(cn.nodeType==1){cn.nodeIndex=++j;}}
pn._batch=batch;}
if(f==1){if(l==0||n.nodeIndex==l){r[++ri]=n;}}else{if((n.nodeIndex+l)%f==0){r[++ri]=n;}}}
return r;},"only-child":function(c){var r=[],ri=-1;for(var i=0,ci;ci=c[i];i++){if(!prev(ci)&&!next(ci)){r[++ri]=ci;}}
return r;},"empty":function(c){var r=[],ri=-1;for(var i=0,ci;ci=c[i];i++){var cns=ci.childNodes,j=0,cn,_e0=true;while(cn=cns[j]){++j;if(cn.nodeType==1||cn.nodeType==3){_e0=false;break;}}
if(_e0){r[++ri]=ci;}}
return r;},"contains":function(c,v){var r=[],ri=-1;for(var i=0,ci;ci=c[i];i++){if((ci.textContent||ci.innerText||"").indexOf(v)!=-1){r[++ri]=ci;}}
return r;},"nodeValue":function(c,v){var r=[],ri=-1;for(var i=0,ci;ci=c[i];i++){if(ci.firstChild&&ci.firstChild.nodeValue==v){r[++ri]=ci;}}
return r;},"checked":function(c){var r=[],ri=-1;for(var i=0,ci;ci=c[i];i++){if(ci.checked==true){r[++ri]=ci;}}
return r;},"not":function(c,ss){return Ext.DomQuery.filter(c,ss,true);},"any":function(c,_f5){var ss=_f5.split("|");var r=[],ri=-1,s;for(var i=0,ci;ci=c[i];i++){for(var j=0;s=ss[j];j++){if(Ext.DomQuery.is(ci,s)){r[++ri]=ci;break;}}}
return r;},"odd":function(c){return this["nth-child"](c,"odd");},"even":function(c){return this["nth-child"](c,"even");},"nth":function(c,a){return c[a-1]||[];},"first":function(c){return c[0]||[];},"last":function(c){return c[c.length-1]||[];},"has":function(c,ss){var s=Ext.DomQuery.select;var r=[],ri=-1;for(var i=0,ci;ci=c[i];i++){if(s(ss,ci).length>0){r[++ri]=ci;}}
return r;},"next":function(c,ss){var is=Ext.DomQuery.is;var r=[],ri=-1;for(var i=0,ci;ci=c[i];i++){var n=next(ci);if(n&&is(n,ss)){r[++ri]=ci;}}
return r;},"prev":function(c,ss){var is=Ext.DomQuery.is;var r=[],ri=-1;for(var i=0,ci;ci=c[i];i++){var n=prev(ci);if(n&&is(n,ss)){r[++ri]=ci;}}
return r;}}};}();Ext.query=Ext.DomQuery.select;Date.precompileFormats=function(s){var _11b=s.split("|");for(var i=0,len=_11b.length;i<len;i++){Date.createNewFormat(_11b[i]);Date.createParser(_11b[i]);}};Date.precompileFormats("D n/j/Y|n/j/Y|n/j/y|m/j/y|n/d/y|m/j/Y|n/d/Y|YmdHis|F d, Y|l, F d, Y|H:i:s|g:i A|g:ia|g:iA|g:i a|g:i A|h:i|g:i|H:i|ga|ha|gA|h a|g a|g A|gi|hi|gia|hia|g|H|m/d/y|m/d/Y|m-d-y|m-d-Y|m/d|m-d|md|mdy|mdY|d|Y-m-d|Y-m-d H:i:s|d/m/y|d/m/Y|d-m-y|d-m-Y|d/m|d-m|dm|dmy|dmY|Y-m-d|l|D m/d|D m/d/Y|m/d/Y");Ext.ColorPalette.prototype.tpl=new Ext.XTemplate("<tpl for=\".\"><a href=\"#\" class=\"color-{.}\" hidefocus=\"on\"><em><span style=\"background:#{.}\" unselectable=\"on\">&#160;</span></em></a></tpl>");
Ext.air.FileProvider=function(_1){Ext.air.FileProvider.superclass.constructor.call(this);this.defaultState={mainWindow:{width:780,height:580,x:10,y:10}};Ext.apply(this,_1);this.state=this.readState();var _2=this;air.NativeApplication.nativeApplication.addEventListener("exiting",function(){_2.saveState();});};Ext.extend(Ext.air.FileProvider,Ext.state.Provider,{file:"extstate.data",readState:function(){var _3=air.File.applicationStorageDirectory.resolvePath(this.file);if(!_3.exists){return this.defaultState||{};}
var _4=new air.FileStream();_4.open(_3,air.FileMode.READ);var _5=_4.readObject();_4.close();return _5||this.defaultState||{};},saveState:function(_6,_7){var _8=air.File.applicationStorageDirectory.resolvePath(this.file);var _9=new air.FileStream();_9.open(_8,air.FileMode.WRITE);_9.writeObject(this.state);_9.close();}});
Ext.air.NativeObservable=Ext.extend(Ext.util.Observable,{addListener:function(_1){this.proxiedEvents=this.proxiedEvents||{};if(!this.proxiedEvents[_1]){var _2=this;var f=function(){var _4=Array.prototype.slice.call(arguments,0);_4.unshift(_1);_2.fireEvent.apply(_2,_4);};this.proxiedEvents[_1]=f;this.getNative().addEventListener(_1,f);}
Ext.air.NativeObservable.superclass.addListener.apply(this,arguments);}});Ext.air.NativeObservable.prototype.on=Ext.air.NativeObservable.prototype.addListener;
Ext.air.NativeWindow=function(_1){Ext.apply(this,_1);this.id=this.id||Ext.uniqueId();this.addEvents("close","closing","move","moving","resize","resizing","displayStateChange","displayStateChanging");Ext.air.NativeWindow.superclass.constructor.call(this);if(!this.instance){var _2=new air.NativeWindowInitOptions();_2.systemChrome=this.chrome;_2.type=this.type;_2.resizable=this.resizable;_2.minimizable=this.minimizable;_2.maximizable=this.maximizable;_2.transparent=this.transparent;this.loader=window.runtime.flash.html.HTMLLoader.createRootWindow(false,_2,false);this.loader.load(new air.URLRequest(this.file));this.instance=this.loader.window.nativeWindow;}else{this.loader=this.instance.stage.getChildAt(0);}
var _3=Ext.state.Manager;var b=air.Screen.mainScreen.visibleBounds;var _5=_3.get(this.id)||{};_3.set(this.id,_5);var _6=this.instance;var _7=Math.max(_5.width||this.width,100);var _8=Math.max(_5.height||this.height,100);var _9=b.x+((b.width/2)-(_7/2));var _a=b.y+((b.height/2)-(_8/2));var x=!Ext.isEmpty(_5.x,false)?_5.x:(!Ext.isEmpty(this.x,false)?this.x:_9);var y=!Ext.isEmpty(_5.y,false)?_5.y:(!Ext.isEmpty(this.y,false)?this.y:_a);_6.width=_7;_6.height=_8;_6.x=x;_6.y=y;_6.addEventListener("move",function(){if(_6.displayState!=air.NativeWindowDisplayState.MINIMIZED&&_6.width>100&&_6.height>100){_5.x=_6.x;_5.y=_6.y;}});_6.addEventListener("resize",function(){if(_6.displayState!=air.NativeWindowDisplayState.MINIMIZED&&_6.width>100&&_6.height>100){_5.width=_6.width;_5.height=_6.height;}});Ext.air.NativeWindowManager.register(this);this.on("close",this.unregister,this);if(this.minimizeToTray){this.initMinimizeToTray(this.trayIcon,this.trayMenu);}};Ext.extend(Ext.air.NativeWindow,Ext.air.NativeObservable,{chrome:"standard",type:"normal",width:600,height:400,resizable:true,minimizable:true,maximizable:true,transparent:false,getNative:function(){return this.instance;},getCenterXY:function(){var b=air.Screen.mainScreen.visibleBounds;return{x:b.x+((b.width/2)-(this.width/2)),y:b.y+((b.height/2)-(this.height/2))};},show:function(){if(this.trayed){Ext.air.SystemTray.hideIcon();this.trayed=false;}
this.instance.visible=true;},activate:function(){this.show();this.instance.activate();},hide:function(){this.instance.visible=false;},close:function(){this.instance.close();},isMinimized:function(){return this.instance.displayState==air.NativeWindowDisplayState.MINIMIZED;},isMaximized:function(){return this.instance.displayState==air.NativeWindowDisplayState.MAXIMIZED;},moveTo:function(x,y){this.x=this.instance.x=x;this.y=this.instance.y=y;},resize:function(_10,_11){this.width=this.instance.width=_10;this.height=this.instance.height=_11;},unregister:function(){Ext.air.NativeWindowManager.unregister(this);},initMinimizeToTray:function(_12,_13){var _14=Ext.air.SystemTray;_14.setIcon(_12,this.trayTip);this.on("displayStateChanging",function(e){if(e.afterDisplayState=="minimized"){e.preventDefault();this.hide();_14.showIcon();this.trayed=true;}},this);_14.on("click",function(){this.activate();},this);if(_13){_14.setMenu(_13);}}});Ext.air.NativeWindow.getRootWindow=function(){return air.NativeApplication.nativeApplication.openedWindows[0];};Ext.air.NativeWindow.getRootHtmlWindow=function(){return Ext.air.NativeWindow.getRootWindow().stage.getChildAt(0).window;};Ext.air.NativeWindowGroup=function(){var _16={};return{register:function(win){_16[win.id]=win;},unregister:function(win){delete _16[win.id];},get:function(id){return _16[id];},closeAll:function(){for(var id in _16){if(_16.hasOwnProperty(id)){_16[id].close();}}},each:function(fn,_1c){for(var id in _16){if(_16.hasOwnProperty(id)){if(fn.call(_1c||_16[id],_16[id])===false){return;}}}}};};Ext.air.NativeWindowManager=new Ext.air.NativeWindowGroup();
Ext.sql.Connection=function(_1){Ext.apply(this,_1);Ext.sql.Connection.superclass.constructor.call(this);this.addEvents({open:true,close:true});};Ext.extend(Ext.sql.Connection,Ext.util.Observable,{maxResults:10000,openState:false,open:function(_2){},close:function(){},exec:function(_3){},execBy:function(_4,_5){},query:function(_6){},queryBy:function(_7,_8){},isOpen:function(){return this.openState;},getTable:function(_9,_a){return new Ext.sql.Table(this,_9,_a);},createTable:function(o){var _c=o.name;var _d=o.key;var fs=o.fields;if(!Ext.isArray(fs)){fs=fs.items;}
var _f=[];for(var i=0,len=fs.length;i<len;i++){var f=fs[i],s=f.name;switch(f.type){case"int":case"bool":case"boolean":s+=" INTEGER";break;case"float":s+=" REAL";break;default:s+=" TEXT";}
if(f.allowNull===false||f.name==_d){s+=" NOT NULL";}
if(f.name==_d){s+=" PRIMARY KEY";}
if(f.unique===true){s+=" UNIQUE";}
_f[_f.length]=s;}
var sql=["CREATE TABLE IF NOT EXISTS ",_c," (",_f.join(","),")"].join("");this.exec(sql);}});Ext.sql.Connection.getInstance=function(db,_16){if(Ext.isAir){return new Ext.sql.AirConnection(_16);}else{return new Ext.sql.GearsConnection(_16);}};
Ext.sql.Table=function(_1,_2,_3){this.conn=_1;this.name=_2;this.keyName=_3;};Ext.sql.Table.prototype={update:function(o){var _5=this.keyName+" = ?";return this.updateBy(o,_5,[o[this.keyName]]);},updateBy:function(o,_7,_8){var _9="UPDATE "+this.name+" set ";var fs=[],a=[];for(var _c in o){if(o.hasOwnProperty(_c)){fs[fs.length]=_c+" = ?";a[a.length]=o[_c];}}
for(var _c in _8){if(_8.hasOwnProperty(_c)){a[a.length]=_8[_c];}}
_9=[_9,fs.join(",")," WHERE ",_7].join("");return this.conn.execBy(_9,a);},insert:function(o){var _e="INSERT into "+this.name+" ";var fs=[],vs=[],a=[];for(var key in o){if(o.hasOwnProperty(key)){fs[fs.length]=key;vs[vs.length]="?";a[a.length]=o[key];}}
_e=[_e,"(",fs.join(","),") VALUES (",vs.join(","),")"].join("");return this.conn.execBy(_e,a);},lookup:function(id){return this.selectBy("where "+this.keyName+" = ?",[id])[0]||null;},exists:function(id){return!!this.lookup(id);},save:function(o){if(this.exists(o[this.keyName])){this.update(o);}else{this.insert(o);}},select:function(_16){return this.selectBy(_16,null);},selectBy:function(_17,_18){var sql="select * from "+this.name;if(_17){sql+=" "+_17;}
_18=_18||{};return this.conn.queryBy(sql,_18);},remove:function(_1a){this.deleteBy(_1a,null);},removeBy:function(_1b,_1c){var sql="delete from "+this.name;if(_1b){sql+=" where "+_1b;}
_1c=_1c||{};this.conn.execBy(sql,_1c);}};
Ext.sql.Proxy=function(_1,_2,_3,_4,_5){Ext.sql.Proxy.superclass.constructor.call(this);this.conn=_1;this.table=this.conn.getTable(_2,_3);this.store=_4;if(_5!==true){this.store.on("add",this.onAdd,this);this.store.on("update",this.onUpdate,this);this.store.on("remove",this.onRemove,this);}};Ext.sql.Proxy.DATE_FORMAT="Y-m-d H:i:s";Ext.extend(Ext.sql.Proxy,Ext.data.DataProxy,{load:function(_6,_7,_8,_9,_a){if(!this.conn.isOpen()){this.conn.on("open",function(){this.load(_6,_7,_8,_9,_a);},this,{single:true});return;}
if(this.fireEvent("beforeload",this,_6,_7,_8,_9,_a)!==false){var _b=_6.where||"";var _c=_6.args||[];var _d=_6.groupBy;var _e=_6.sort;var _f=_6.dir;if(_d||_e){_b+=" ORDER BY ";if(_d&&_d!=_e){_b+=_d+" ASC, ";}
_b+=_e+" "+(_f||"ASC");}
var rs=this.table.selectBy(_b,_c);this.onLoad({callback:_8,scope:_9,arg:_a,reader:_7},rs);}else{_8.call(_9||this,null,_a,false);}},onLoad:function(_11,rs,e,_14){if(rs===false){this.fireEvent("loadexception",this,null,_11.arg,e);_11.callback.call(_11.scope||window,null,_11.arg,false);return;}
var _15=_11.reader.readRecords(rs);this.fireEvent("load",this,rs,_11.arg);_11.callback.call(_11.scope||window,_15,_11.arg,true);},processData:function(o){var fs=this.store.fields;var r={};for(var key in o){var f=fs.key(key),v=o[key];if(f){if(f.type=="date"){r[key]=v?v.format(Ext.sql.Proxy.DATE_FORMAT,10):"";}else{if(f.type=="boolean"){r[key]=v?1:0;}else{r[key]=v;}}}}
return r;},onUpdate:function(ds,_1d){var _1e=_1d.getChanges();var kn=this.table.keyName;this.table.updateBy(this.processData(_1e),kn+" = ?",[_1d.data[kn]]);_1d.commit(true);},onAdd:function(ds,_21,_22){for(var i=0,len=_21.length;i<len;i++){this.table.insert(this.processData(_21[i].data));}},onRemove:function(ds,_26,_27){var kn=this.table.keyName;this.table.removeBy(kn+" = ?",[_26.data[kn]]);}});
Ext.sql.AirConnection=Ext.extend(Ext.sql.Connection,{open:function(db){this.conn=new air.SQLConnection();var _2=air.File.applicationDirectory.resolvePath(db);this.conn.open(_2);this.openState=true;this.fireEvent("open",this);},close:function(){this.conn.close();this.fireEvent("close",this);},createStatement:function(_3){var _4=new air.SQLStatement();_4.sqlConnection=this.conn;return _4;},exec:function(_5){var _6=this.createStatement("exec");_6.text=_5;_6.execute();},execBy:function(_7,_8){var _9=this.createStatement("exec");_9.text=_7;this.addParams(_9,_8);_9.execute();},query:function(_a){var _b=this.createStatement("query");_b.text=_a;_b.execute(this.maxResults);return this.readResults(_b.getResult());},queryBy:function(_c,_d){var _e=this.createStatement("query");_e.text=_c;this.addParams(_e,_d);_e.execute(this.maxResults);return this.readResults(_e.getResult());},addParams:function(_f,_10){if(!_10){return;}
for(var key in _10){if(_10.hasOwnProperty(key)){if(!isNaN(key)){var v=_10[key];if(Ext.isDate(v)){v=v.format(Ext.sql.Proxy.DATE_FORMAT);}
_f.parameters[parseInt(key)]=v;}else{_f.parameters[":"+key]=_10[key];}}}
return _f;},readResults:function(rs){var r=[];if(rs&&rs.data){var len=rs.data.length;for(var i=0;i<len;i++){r[r.length]=rs.data[i];}}
return r;}});
Ext.air.SystemTray=function(){var _1=air.NativeApplication.nativeApplication;var _2,_3=false,_4;if(air.NativeApplication.supportsSystemTrayIcon){_2=_1.icon;_3=true;}
if(air.NativeApplication.supportsDockIcon){_2=_1.icon;}
return{setIcon:function(_5,_6,_7){if(!_5){return;}
var _8=new air.Loader();_8.contentLoaderInfo.addEventListener(air.Event.COMPLETE,function(e){_4=new runtime.Array(e.target.content.bitmapData);if(_7){_5.bitmaps=_4;}});_8.load(new air.URLRequest(_5));if(_6&&air.NativeApplication.supportsSystemTrayIcon){_1.icon.tooltip=_6;}},bounce:function(_a){_2.bounce(_a);},on:function(_b,fn,_d){_2.addEventListener(_b,function(){fn.apply(_d||this,arguments);});},hideIcon:function(){if(!_2){return;}
_2.bitmaps=[];},showIcon:function(){if(!_2){return;}
_2.bitmaps=_4;},setMenu:function(_e,_f){if(!_2){return;}
var _10=new air.NativeMenu();for(var i=0,len=_e.length;i<len;i++){var a=_e[i];if(a=="-"){_10.addItem(new air.NativeMenuItem("",true));}else{var _14=_10.addItem(Ext.air.MenuItem(a));if(a.menu||(a.initialConfig&&a.initialConfig.menu)){_14.submenu=Ext.air.SystemTray.setMenu(a.menu||a.initialConfig.menu,_10);}}
if(!_f){_2.menu=_10;}}
return _10;}};}();
Ext.air.DragType={TEXT:"text/plain",HTML:"text/html",URL:"text/uri-list",BITMAP:"image/x-vnd.adobe.air.bitmap",FILES:"application/x-vnd.adobe.air.file-list"};Ext.apply(Ext.EventObjectImpl.prototype,{hasFormat:function(_1){if(this.browserEvent.dataTransfer){for(var i=0,_3=this.browserEvent.dataTransfer.types.length;i<_3;i++){if(this.browserEvent.dataTransfer.types[i]==_1){return true;}}}
return false;},getData:function(_4){return this.browserEvent.dataTransfer.getData(_4);}});
Ext.air.Sound={play:function(_1,_2){var _3=air.File.applicationDirectory.resolvePath(_1);var _4=new air.Sound();_4.load(new air.URLRequest(_3.url));_4.play(_2);}};
Ext.air.SystemMenu=function(){var _1;if(air.NativeWindow.supportsMenu&&nativeWindow.systemChrome!=air.NativeWindowSystemChrome.NONE){_1=new air.NativeMenu();nativeWindow.menu=_1;}
if(air.NativeApplication.supportsMenu){_1=air.NativeApplication.nativeApplication.menu;}
function find(_2,_3){for(var i=0,_5=_2.items.length;i<_5;i++){if(_2.items[i]["label"]==_3){return _2.items[i];}}
return null;}
return{add:function(_6,_7,_8){var _9=find(_1,_6);if(!_9){_9=_1.addItem(new air.NativeMenuItem(_6));_9.mnemonicIndex=_8||0;_9.submenu=new air.NativeMenu();}
for(var i=0,_b=_7.length;i<_b;i++){_9.submenu.addItem(_7[i]=="-"?new air.NativeMenuItem("",true):Ext.air.MenuItem(_7[i]));}
return _9.submenu;},get:function(){return _1;}};}();Ext.air.MenuItem=function(_c){if(!_c.isAction){_c=new Ext.Action(_c);}
var _d=_c.initialConfig;var _e=new air.NativeMenuItem(_d.itemText||_d.text);_e.enabled=!_d.disabled;if(!Ext.isEmpty(_d.checked)){_e.checked=_d.checked;}
var _f=_d.handler;var _10=_d.scope;_e.addEventListener(air.Event.SELECT,function(){_f.call(_10||window,_d);});_c.addComponent({setDisabled:function(v){_e.enabled=!v;},setText:function(v){_e.label=v;},setVisible:function(v){_e.enabled=!v;},setHandler:function(_14,_15){_f=_14;_10=_15;},on:function(){}});return _e;};