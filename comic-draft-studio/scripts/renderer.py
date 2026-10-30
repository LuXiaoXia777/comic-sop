import argparse, json, pathlib, re, html, copy, base64, mimetypes

CSS = '''
:root{color-scheme:dark;font-family:system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#08090a;color:#e4e4e7;font-size:15px}*{box-sizing:border-box}body{margin:0}button,input,textarea{font:inherit}button,a,input,textarea{outline-offset:5px}a{color:#d6ded9;text-underline-offset:4px}button{cursor:pointer}nav{position:sticky;top:0;background:#08090af5;backdrop-filter:blur(14px);z-index:5;border-bottom:1px solid #292b2e;padding:0 max(24px,calc((100vw - 1200px)/2));display:flex;gap:30px;overflow-x:auto}nav button{border:0;border-bottom:2px solid transparent;background:none;color:#989ca2;padding:23px 0 20px;white-space:nowrap}nav button[aria-selected=true]{color:#f5f5f5;border-color:#c4d2c7}main{max-width:1256px;margin:auto;padding:32px 28px 64px}.meta{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:26px;color:#a4a8ae;font-size:13px}.meta a{color:#b6bbb8}.toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:0 0 22px}input[type=search]{background:#111315;border:1px solid #303337;border-radius:8px;padding:12px 16px;color:#eee;min-width:240px;flex:1}.chip,.action{border:1px solid #35383c;border-radius:7px;padding:9px 13px;color:#c9cdd1;background:#121416}.chip.active{background:#d4ddd6;color:#101512;border-color:#d4ddd6}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.card,.block{background:#111315;border:1px solid #292c30;border-radius:10px;padding:24px}.card{display:flex;flex-direction:column;gap:13px}.card .name{font-size:18px;color:#f1f2f3;line-height:1.5}.small,.caption{font-size:13px;color:#9da3a9;line-height:1.8}.tag{display:inline-block;border:1px solid #383d40;border-radius:4px;color:#c6d2ca;padding:2px 8px;font-size:12px;width:fit-content}.text{white-space:pre-wrap;line-height:1.9;margin:0;overflow-wrap:anywhere}.block{margin-bottom:18px}.label{font-size:13px;color:#a8b5ad;margin-bottom:14px;letter-spacing:.03em}.blocktop{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:14px}.blocktop .label{margin:0}.copy{flex-shrink:0;border:1px solid #3c4144;border-radius:5px;background:#1b1f20;color:#d6dcda;padding:6px 11px;font-size:12px}pre{font:inherit;white-space:pre-wrap;line-height:1.85;margin:0;overflow-wrap:anywhere;color:#d1d7d3}.tablebox{overflow:auto;border:1px solid #303336;border-radius:7px;max-height:70vh}table{width:100%;border-collapse:collapse;min-width:900px;text-align:left;font-size:14px;line-height:1.8}th{background:#1d2123;color:#c8d2cc;font-weight:500;position:sticky;top:0;z-index:1}td,th{padding:17px 18px;border-bottom:1px solid #303336;vertical-align:top;min-width:135px;white-space:pre-wrap}td:first-child,th:first-child{min-width:65px;width:65px}tr:last-child td{border-bottom:0}td{color:#d4d6d9}tbody tr:nth-child(even){background:#15181a}details{border-top:1px solid #303437;padding-top:13px}summary{cursor:pointer;color:#cbd3ce;font-size:14px}details .text{margin-top:14px}ul{padding-left:20px;margin:0;line-height:2}li+li{margin-top:9px}.note{border-left:2px solid #7f9387;padding:12px 18px;background:#101512;color:#b4c0b8;font-size:14px;line-height:1.9;margin-bottom:24px}.foot{margin-top:auto;padding-top:6px;display:flex;gap:18px}.empty{padding:40px;text-align:center;color:#a8adb2}textarea{display:block;width:100%;min-height:150px;padding:14px;color:#e5e7e9;background:#090b0c;border:1px solid #34393b;border-radius:6px;line-height:1.8;margin:14px 0}.status{font-size:13px;color:#b9c8bf}a.action{text-decoration:none;display:inline-block}button:hover,.action:hover{filter:brightness(1.2)}[hidden]{display:none!important}@media(max-width:700px){nav{gap:24px;padding:0 18px}nav button{padding:18px 0}.grid{grid-template-columns:1fr}main{padding:22px 16px 48px}.block,.card{padding:19px}.meta{align-items:flex-start;font-size:12px}.toolbar{gap:9px}input[type=search]{width:100%;min-width:0;flex-basis:100%}.chip{font-size:13px;padding:8px 10px}table{font-size:13px}.name{font-size:17px!important}}@media print{nav,.copy,.toolbar,.feedback{display:none}main{max-width:none}.block{break-inside:avoid}.tablebox{max-height:none;overflow:visible}}
'''

CSS += '''
.resource-section{margin-top:28px}.topics-table{max-height:none}.topics-table table{min-width:650px}.topics-table th:first-child,.topics-table td:first-child{width:22%;min-width:170px}.topics-table th:nth-child(2),.topics-table td:nth-child(2){width:78%;min-width:300px}.back{margin-left:auto;align-self:center;white-space:nowrap;font-size:13px}.block:has(>.tablebox){padding:0;border:0;background:none}.tablebox{max-height:none}
'''

CSS += '''
main{max-width:none;margin:0;padding:0}
nav{padding-left:16px;padding-right:16px}
.tablebox{border:0;border-radius:0;margin:0;padding:0;background:transparent}
table{border:0}
th{background:#08090a}
tbody tr:nth-child(even){background:transparent}
td,th{padding:14px 16px;border-left:0;border-right:0;border-top:0;border-bottom:1px solid #25282b}
.block:has(>.tablebox){margin:0;padding:0;border:0;border-radius:0}
.block:not(:has(>.tablebox)){margin:0;padding:20px 16px;border:0;border-radius:0;background:transparent}
.resource-section{margin-top:20px}
@media(max-width:700px){main{padding:0}td,th{padding:12px}.block:not(:has(>.tablebox)){padding:16px 12px}nav{padding-left:12px;padding-right:12px}}
'''

CSS += '''
.resources .section-title{font-size:22px;font-weight:600;line-height:1.4;margin:0;padding:22px 16px 14px;color:#f0f2f1}
.resources .resource-section{margin-top:18px}.resources .resource-section:first-child{margin-top:0}
.resources table{table-layout:fixed;min-width:720px}
.resources th:first-child,.resources td:first-child{width:200px;min-width:200px;white-space:nowrap}
.resources th:last-child,.resources td:last-child{width:28%}
.resources td{overflow-wrap:anywhere}
@media(max-width:700px){.resources .section-title{font-size:20px;padding:20px 12px 12px}.resources th:first-child,.resources td:first-child{width:160px;min-width:160px}}
'''

CSS += '''
.episodes-table table{table-layout:fixed;min-width:480px}
.episodes-table th:first-child,.episodes-table td:first-child{width:auto;min-width:0;overflow-wrap:anywhere}
.episodes-table th:nth-child(2),.episodes-table td:nth-child(2){width:180px;min-width:0}
.episodes-table th:last-child,.episodes-table td:last-child{width:120px;min-width:0;white-space:nowrap}
@media(max-width:700px){.episodes-table th:nth-child(2),.episodes-table td:nth-child(2){width:140px}.episodes-table th:last-child,.episodes-table td:last-child{width:96px}}
'''

CSS += '''
.image-bar{display:flex;align-items:center;gap:12px;padding:16px;flex-wrap:wrap}.image-bar label{cursor:pointer}
.file-input{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}.image-bar:focus-within label{outline:1px solid #b8c8bf}
.image-gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:20px;padding:0 16px 24px}.image-gallery figure{margin:0}.image-gallery img{display:block;width:100%;height:auto;max-height:85vh;object-fit:contain;object-position:top}.image-gallery figcaption{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0;font-size:13px;color:#adb4b0}
'''

CSS += '''
td.number-cell,th.number-cell{width:64px;min-width:64px;text-align:center}td.page-cell{vertical-align:middle}
'''

CSS += '''
table th:not(:last-child),table td:not(:last-child){border-right:1px solid #303437}
'''

CSS += '''
.page-tabs{display:flex;gap:24px;padding:0 16px;border-bottom:1px solid #292b2e;overflow-x:auto}.page-tabs button{background:none;border:0;border-bottom:2px solid transparent;color:#989ca2;padding:16px 0;white-space:nowrap}.page-tabs button[aria-selected=true]{color:#f5f5f5;border-color:#c4d2c7}.prompt-pages .blocktop{justify-content:flex-end}.prompt-pages pre{font-size:14px;line-height:1.8}
'''

CSS += '''
.character-table th:first-child,.character-table td:first-child{width:180px;min-width:180px}.character-table th:nth-child(2){width:44%}.page-script-table th:first-child,.page-script-table td:first-child{width:70px;min-width:70px}.page-script-table th:nth-child(2){width:64%}.page-script-table th:nth-child(3){min-width:240px}.sketch-image{display:block;width:100%;max-width:900px;height:auto;margin:0 auto}.sketch-open{display:block;width:fit-content;margin:12px auto 0}.blocktop .label{font-size:20px;color:#e4e4e7;font-weight:600}.sketch-panel{padding-top:12px}
'''


CSS += '''
.episode-script{padding:32px 0 64px}
.episode-script>.block,.episode-script>.block:has(>.tablebox),.episode-script>.block:not(:has(>.tablebox)){margin:0;padding:0;border:0;background:transparent}
.episode-script>.block+.block{margin-top:56px}
.episode-script>.block>.blocktop{padding:0 16px;margin:0 0 22px}
.episode-script>.block>.blocktop .label{line-height:1.5}
.episode-script .sketch-panel{padding:24px 16px 0}
@media(max-width:700px){.episode-script{padding:24px 0 40px}.episode-script>.block+.block{margin-top:40px}.episode-script>.block>.blocktop{padding:0 12px;margin-bottom:18px}.episode-script .page-tabs{padding:0 12px}.episode-script .sketch-panel{padding:20px 12px 0}}
'''

CSS += '''
.inline-sketch-table table{table-layout:fixed;min-width:1000px}.inline-sketch-table th:first-child,.inline-sketch-table td:first-child{width:64px;min-width:64px}.inline-sketch-table th:nth-child(2){width:auto}.inline-sketch-table th:nth-child(3){width:26%}.inline-sketch-table th:last-child{width:280px}.sketch-thumb{display:block;width:100%;padding:0;border:0;background:transparent;cursor:zoom-in}.sketch-thumb img{display:block;width:100%;height:auto}.sketch-dialog{background:#111;border:1px solid #35383c;padding:16px;max-width:96vw;max-height:94vh}.sketch-dialog::backdrop{background:#000c}.sketch-dialog>button{display:block;margin:0 0 12px auto}.sketch-dialog>img{display:block;max-width:100%;max-height:80vh;width:auto;height:auto;margin:auto}
'''

CSS += '''
.episode-row{display:block;padding:22px 16px;border-bottom:1px solid #25282b;color:#d4d6d9;font-size:15px;line-height:1.9;text-decoration:none;transition:color .15s ease,background-color .15s ease}.episode-row:hover,.episode-row:focus-visible{color:#a8dcc5;background:#111918}.episode-row:last-child{border-bottom:0}@media(max-width:700px){.episode-row{padding:18px 12px}}
'''

CSS += '''
.topics-table th:first-child,.topics-table td:first-child{width:72px;min-width:72px;text-align:center}.topics-table th:nth-child(2),.topics-table td:nth-child(2){width:22%;min-width:170px}.topics-table th:nth-child(3),.topics-table td:nth-child(3){width:auto;min-width:300px}
'''

JS = r'''
const D=JSON.parse(document.getElementById('data').textContent),main=document.querySelector('main'),nav=document.querySelector('nav');
function el(tag,cls,text){let e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function link(text,href,cls){let a=el('a',cls,text);a.href=href;return a}
let current=0;
function toast(text){document.getElementById('status').textContent=text}
async function copy(text,btn){try{if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(text);else{let t=el('textarea');t.value=text;document.body.append(t);t.select();let ok=document.execCommand('copy');t.remove();if(!ok)throw Error()}btn.textContent='已复制';setTimeout(()=>btn.textContent=btn.dataset.copyLabel||'复制整页提示词',1500)}catch{toast('复制未成功，请选中文本手动复制')}}
function block(b){let wrap=el('section','block');let top=el('div','blocktop');if(b.label)top.append(el('div','label',b.label));if(b.type==='prompt'){let c=el('button','copy','复制整页提示词');c.dataset.copyLabel='复制整页提示词';c.onclick=()=>copy(b.text,c);top.append(c)}if(top.childNodes.length)wrap.append(top);if(b.type==='sketches'){sketchTabs(wrap,b.pages);return wrap}if(b.type==='table'){let box=el('div','tablebox '+(b.columns[0]==='角色'?'character-table':b.columns.includes('速写稿')?'inline-sketch-table':b.columns.length===3&&b.columns[0]==='页码'?'page-script-table':''));box.tabIndex=0;box.setAttribute('aria-label',b.label+'，可横向滚动');let t=el('table'),head=el('thead'),tr=el('tr');b.columns.forEach(x=>{let h=el('th',x==='页码'||x==='画格'?'number-cell':'',x);h.scope='col';tr.append(h)});head.append(tr);t.append(head);let body=el('tbody');b.rows.forEach((row,i)=>{let r=el('tr');row.forEach((x,c)=>{if(c===0&&b.columns[0]==='页码'&&i>0&&b.rows[i-1][0]===x)return;let cell=el('td',b.columns[c]==='页码'||b.columns[c]==='画格'?'number-cell':'',typeof x==='string'?x:undefined);if(x&&typeof x==='object'&&x.type==='image'){let btn=el('button','sketch-thumb');btn.type='button';btn.setAttribute('aria-label',x.alt+'，点击放大');let img=el('img');img.src=x.src;img.alt=x.alt;img.loading='lazy';btn.append(img);btn.onclick=()=>enlargeSketch(x);cell.append(btn)}if(c===0&&b.columns[0]==='页码'){let span=1;while(i+span<b.rows.length&&b.rows[i+span][0]===x)span++;cell.rowSpan=span;cell.classList.add('page-cell')}r.append(cell)});body.append(r)});t.append(body);box.append(t);wrap.append(box)}else if(b.type==='list'){let ul=el('ul');b.items.forEach(x=>ul.append(el('li','',x)));wrap.append(ul)}else wrap.append(el(b.type==='prompt'?'pre':'p','text',b.text));return wrap}

function enlargeSketch(item){let d=el('dialog','sketch-dialog'),close=el('button','action','关闭'),img=el('img');img.src=item.src;img.alt=item.alt;close.onclick=()=>d.close();d.append(close,img);d.addEventListener('click',e=>{if(e.target===d)d.close()});d.addEventListener('close',()=>d.remove());document.body.append(d);d.showModal()}
let sketchPage=0;
function sketchTabs(parent,pages){
if(!pages.length)return;
let tabs=el('div','page-tabs'),panel=el('div','sketch-panel');tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','速写页码');panel.id='sketch-panel';panel.setAttribute('role','tabpanel');parent.append(tabs,panel);
function choose(i,focus=false){sketchPage=i;[...tabs.children].forEach((b,n)=>{b.setAttribute('aria-selected',String(i===n));b.tabIndex=i===n?0:-1});panel.setAttribute('aria-labelledby','sketch-tab-'+i);let img=el('img','sketch-image');img.src=pages[i].src;img.alt=pages[i].alt;let a=link('查看原图',pages[i].src,'sketch-open');a.target='_blank';a.rel='noopener';panel.replaceChildren(img,a);if(focus)tabs.children[i].focus()}
pages.forEach((page,i)=>{let b=el('button','',`第${i+1}页`);b.id='sketch-tab-'+i;b.setAttribute('role','tab');b.setAttribute('aria-controls','sketch-panel');b.onclick=()=>choose(i);b.onkeydown=e=>{let n=i;if(e.key==='ArrowRight')n=(i+1)%pages.length;else if(e.key==='ArrowLeft')n=(i+pages.length-1)%pages.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=pages.length-1;else return;e.preventDefault();choose(n,true)};tabs.append(b)});choose(Math.min(sketchPage,pages.length-1));
}

let promptPage=0;
function promptTabs(pane,prompts){
let group=el('section','prompt-pages'),tabs=el('div','page-tabs'),panel=el('div');
tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','整页提示词');panel.setAttribute('role','tabpanel');panel.id='prompt-page-panel';group.append(tabs,panel);pane.append(group);
function choose(i,focus){promptPage=i;[...tabs.children].forEach((b,n)=>{b.setAttribute('aria-selected',String(n===i));b.tabIndex=n===i?0:-1});panel.setAttribute('aria-labelledby','prompt-page-'+i);panel.replaceChildren(block({...prompts[i],label:''}));if(focus)tabs.children[i].focus()}
prompts.forEach((p,i)=>{let b=el('button','',`第${i+1}页`);b.id='prompt-page-'+i;b.setAttribute('role','tab');b.setAttribute('aria-controls','prompt-page-panel');b.onclick=()=>choose(i,false);b.onkeydown=e=>{let n=i;if(e.key==='ArrowRight')n=(i+1)%prompts.length;else if(e.key==='ArrowLeft')n=(i+prompts.length-1)%prompts.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=prompts.length-1;else return;e.preventDefault();choose(n,true)};tabs.append(b)});choose(Math.min(promptPage,prompts.length-1),false)
}

function render(){main.replaceChildren();let pane=el('div');pane.id='panel-'+current;if(D.kind==='episode'&&current===0)pane.classList.add('episode-script');pane.setAttribute('role','tabpanel');pane.setAttribute('aria-labelledby','tab-'+current);main.append(pane);let tab=D.tabs[current];if(tab.blocks){let prompts=tab.blocks.filter(b=>b.type==='prompt'),placed=false;tab.blocks.forEach(b=>{if(b.type!=='prompt')pane.append(block(b));else if(!placed){promptTabs(pane,prompts);placed=true}})}if(tab.kind==='images')images(pane);if(tab.kind==='topics')topics(pane);if(tab.kind==='episodes')episodes(pane);if(tab.kind==='skills')skills(pane);if(tab.kind==='rules')rules(pane);if(tab.kind==='resources'){pane.classList.add('resources');if(D.outputStandard){let standard=el('section','resource-section');standard.append(el('h2','section-title','现行输出标准'));contentTable(standard,['项目','输出要求','检查方式'],D.outputStandard.rows);let call=el('section','resource-section');call.append(el('h2','section-title','直接调用'));call.append(block({type:'text',label:'',text:D.outputStandard.invocation}));pane.append(standard,call)}if(D.sketchTools){let toolsSection=el('section','resource-section');toolsSection.append(el('h2','section-title','速写工具'));contentTable(toolsSection,['工具','能力与适用范围','使用情况'],D.sketchTools.map(x=>[link(x.name,x.url),x.capability,x.use]));pane.append(toolsSection)}let flow=el('section','resource-section');flow.append(el('h2','section-title','创作流程'));tab.flow.forEach(b=>flow.append(block(b)));pane.append(flow);let prefs=el('section','resource-section');prefs.append(el('h2','section-title','个人规则'));rules(prefs);pane.append(prefs);}}
function contentTable(pane,columns,rows,cls){let box=el('div','tablebox '+(cls||''));box.tabIndex=0;let t=el('table'),head=el('thead'),tr=el('tr');columns.forEach(x=>{let h=el('th','',x);h.scope='col';tr.append(h)});head.append(tr);t.append(head);let body=el('tbody');rows.forEach(row=>{let tr=el('tr');row.forEach(x=>{let td=el('td');if(typeof x==='string')td.textContent=x;else td.append(x);tr.append(td)});body.append(tr)});t.append(body);box.append(t);pane.append(box)}
function topics(pane){if(!D.topics.length){pane.append(el('p','empty','告诉我一个画面、一句话或零散情节，我会帮你完善成脚本。请在聊天中发送。'));return}contentTable(pane,['序号','选题','剧情粗稿'],D.topics.map((t,i)=>[String(i+1),t.name,t.outline]),'topics-table')}
function episodes(pane){if(!D.episodes.length){pane.append(el('p','empty','还没有脚本。提供粗稿并确定页数后，将在这里展示。'));return}let list=el('div','episode-list');D.episodes.forEach((e,i)=>{let a=link(`${i+1}. ${e.summary||e.name}`,'期次/'+e.id+'.html','episode-row');list.append(a)});pane.append(list)}
function skills(pane){contentTable(pane,['技能','用途','资料'],D.skills.map(s=>{let links=el('div','foot');links.append(link('原文','资料/技能原文/'+s.id+'/阅读.html'),link('来源',s.url));return [s.name,s.text,links]}))}
function rules(pane){pane.append(block({type:'list',label:'',items:D.rules.rules}))}

let imageItems=D.images||[],imageLoaded=false;
function imageDB(){return new Promise((resolve,reject)=>{let q=indexedDB.open('comic-library-images',1);q.onupgradeneeded=()=>q.result.createObjectStore('issues');q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)})}
async function imageStore(save){let db=await imageDB();return new Promise((resolve,reject)=>{let tx=db.transaction('issues',save?'readwrite':'readonly'),store=tx.objectStore('issues'),q=save?store.put(imageItems,D.id):store.get(D.id);let result;q.onsuccess=()=>result=q.result;tx.oncomplete=()=>{db.close();resolve(result)};tx.onerror=()=>{db.close();reject(tx.error)};tx.onabort=()=>{db.close();reject(tx.error)}})}
function readImage(file){return new Promise((resolve,reject)=>{let reader=new FileReader();reader.onload=()=>resolve({name:file.name,src:reader.result});reader.onerror=()=>reject(reader.error);reader.readAsDataURL(file)})}
async function images(pane){let bar=el('div','image-bar'),input=el('input');input.type='file';input.accept='image/png,image/jpeg,image/webp,image/gif';input.multiple=true;input.id='image-upload';input.setAttribute('aria-label','上传图片');let upload=el('label','action','上传图片');upload.htmlFor=input.id;input.className='file-input';let download=el('button','action','保存含图片的页面'),state=el('span','status');state.setAttribute('role','status');bar.append(upload,input,download,state);pane.append(bar);let gallery=el('div','image-gallery');pane.append(gallery);
function draw(){gallery.replaceChildren();imageItems.forEach((item,index)=>{let figure=el('figure'),img=el('img');img.src=item.src;img.alt=item.name;let caption=el('figcaption'),remove=el('button','copy','移除');caption.append(el('span','',item.name),remove);remove.onclick=async()=>{imageItems.splice(index,1);draw();try{await imageStore(true);state.textContent='已保存到当前浏览器'}catch{state.textContent='未能暂存，请保存含图片的页面'}};figure.append(img,caption);gallery.append(figure)})}
input.disabled=true;
if(!imageLoaded){try{let saved=await imageStore(false);if(saved&&!D.images)imageItems=saved}catch{}imageLoaded=true}draw();input.disabled=false;
input.onchange=async()=>{input.disabled=true;let rejected=false;for(let file of input.files){if(!/^image\/(png|jpeg|webp|gif)$/.test(file.type)){rejected=true;continue}try{imageItems.push(await readImage(file))}catch{rejected=true}}draw();try{await imageStore(true);state.textContent=rejected?'部分文件无法读取，其余已保存到当前浏览器':'已保存到当前浏览器'}catch{state.textContent='未能暂存，请保存含图片的页面'}input.value='';input.disabled=false};
download.onclick=()=>{let snapshot=document.documentElement.cloneNode(true),data={...D,images:imageItems};snapshot.querySelector('#data').textContent=JSON.stringify(data).replace(/</g,'\\u003c');snapshot.querySelector('nav').replaceChildren();snapshot.querySelector('main').replaceChildren();snapshot.querySelector('#status').textContent='';let url=URL.createObjectURL(new Blob(['<!doctype html>'+snapshot.outerHTML],{type:'text/html;charset=utf-8'})),a=link('',url);a.download=D.name+'.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
}

D.tabs.forEach((t,i)=>{let b=el('button','',t.label);b.id='tab-'+i;b.setAttribute('role','tab');b.setAttribute('aria-controls','panel-'+i);b.onclick=()=>select(i);b.onkeydown=e=>{let n=i;if(e.key==='ArrowRight')n=(i+1)%D.tabs.length;else if(e.key==='ArrowLeft')n=(i+D.tabs.length-1)%D.tabs.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=D.tabs.length-1;else return;e.preventDefault();select(n);nav.children[n].focus()};nav.append(b)});
function select(i){current=i;[...nav.querySelectorAll('button')].forEach((b,n)=>{b.setAttribute('aria-selected',n===i?'true':'false');b.tabIndex=n===i?0:-1});render();try{history.replaceState(null,'','#'+i)}catch{}}
if(D.kind==='episode')nav.append(link('返回','../index.html','back'));
let initial=Number(location.hash.slice(1));if(D.kind==='library'&&(initial===3||initial===4))initial=2;select(Number.isInteger(initial)&&initial>=0&&initial<D.tabs.length?initial:0);
'''

