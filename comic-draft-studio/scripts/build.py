"""Initialize and build a portable comic workspace. Python 3.9+, standard library."""
import argparse, base64, copy, html, json, mimetypes, pathlib, re, io, zipfile, shutil
from renderer import CSS, JS
SKILL=pathlib.Path(__file__).resolve().parent.parent

def write_default(path,value):
    if not path.exists(): path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def page(data,theme=""):
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    heading=''
    if data.get('displayTitle'):
        heading='<header class=episode-heading><h1>'+html.escape(data['displayTitle'])+'</h1>'
        if data.get('englishTitle'): heading+='<p lang=en-GB>'+html.escape(data['englishTitle'])+'</p>'
        heading+='</header>'
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(data.get('name','漫画工作室'))+'</title><style>'+CSS+theme+'</style><body>'+heading+'<nav role="tablist" aria-label="内容分类"></nav><main></main><div id="status" class="status" role="status" aria-live="polite"></div><script id="data" type="application/json">'+payload+'</script><script>'+JS+'</script></body></html>'

def build(root,initialize=False):
    root=root.resolve()
    nested=root/'底层文件/项目资料'
    if (nested/'资料').exists():
        root=nested
    elif initialize and not (root/'资料').exists() and not (root/'项目配置.json').exists():
        workspace=root
        root=nested
        root.mkdir(parents=True,exist_ok=True)
        for name in ['HTML','图片']: (workspace/name).mkdir(exist_ok=True)
        write_default(root/'项目配置.json',{'htmlDirectory':'../../HTML','assetDirectory':'../../图片','indexFile':'../../HTML/漫画目录.html','episodeLinksPrefix':'','compatibilityAliases':False})
        local_skill=workspace/'底层文件/Skill/comic-draft-studio'
        if local_skill.resolve()!=SKILL.resolve() and not local_skill.exists():
            shutil.copytree(SKILL,local_skill,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
        launcher=root/'重新生成.command'
        if not launcher.exists():
            launcher.write_text('#!/bin/zsh\ncd -- "$(dirname -- "$0")"\npython3 "../Skill/comic-draft-studio/scripts/build.py" --root "$PWD"\n',encoding='utf-8')
            launcher.chmod(0o755)
    config_path=root/'项目配置.json'
    config=json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    output=(root/config.get('htmlDirectory','期次')).resolve()
    assets=(root/config.get('assetDirectory','.')).resolve()
    index_path=(root/config.get('indexFile','index.html')).resolve()
    output.mkdir(parents=True,exist_ok=True)
    index_path.parent.mkdir(parents=True,exist_ok=True)
    theme_path=root/"资料/主题.css"
    theme=theme_path.read_text(encoding="utf-8") if theme_path.exists() else (SKILL/"assets/theme.css").read_text(encoding="utf-8")
    if initialize:
        for folder in ['资料/期次']: (root/folder).mkdir(parents=True,exist_ok=True)
        if not theme_path.exists(): theme_path.write_text(theme,encoding='utf-8')
        write_default(root/'资料/选题库.json',[])
        write_default(root/'资料/个人规则.json',{'rules':[],'changes':[]})
        write_default(root/'资料/输出标准.json',json.loads((SKILL/'references/output-standard.json').read_text(encoding='utf-8')))
    # Add reference defaults to old projects without overwriting user edits.
    write_default(root/'资料/布局参考.json',json.loads((SKILL/'references/layout-library.json').read_text(encoding='utf-8')))
    read=lambda path:json.loads((root/path).read_text(encoding='utf-8'))
    topics=read('资料/选题库.json');rules=read('资料/个人规则.json');standard=read('资料/输出标准.json')
    episodes=[];used_names={index_path.name} if output==index_path.parent else set()
    for src in sorted((root/'资料/期次').glob('*.json')):
        e=json.loads(src.read_text(encoding='utf-8'))
        if not re.fullmatch(r'[a-z0-9-]+',e['id']):raise ValueError('期次ID只能包含小写英文、数字和连字符')
        data=copy.deepcopy(e);data['kind']='episode'
        for tab in data['tabs']:
            for block in tab.get('blocks',[]):
                if block['type']!='table': continue
                for row in block['rows']:
                    if len(row)!=len(block['columns']):raise ValueError('表格列数不一致')
                    for cell in row:
                        if isinstance(cell,dict) and cell.get('type')=='image':
                            asset=(assets/cell['src']).resolve()
                            if assets not in asset.parents:raise ValueError('图片必须位于用户项目内')
                            mime=mimetypes.guess_type(asset.name)[0]
                            if mime not in ['image/png','image/jpeg','image/webp','image/gif']:raise ValueError('使用PNG、JPEG、WebP或GIF图片')
                            cell['src']='data:'+mime+';base64,'+base64.b64encode(asset.read_bytes()).decode()
        colour_files=[]
        for tab in data['tabs']:
            for block in tab.get('blocks',[]):
                if block.get('type')=='table' and '上色图' in block['columns']:
                    col=block['columns'].index('上色图')
                    for row in block['rows']:
                        cell=row[col]
                        if isinstance(cell,dict) and cell.get('type')=='image':
                            mime=cell['src'].split(';')[0].split(':')[1]
                            ext={'image/png':'png','image/jpeg':'jpg','image/webp':'webp','image/gif':'gif'}[mime]
                            colour_files.append({'name':f"{len(colour_files)+1:02d}.{ext}",'src':cell['src']})
        if colour_files:
            archive=io.BytesIO()
            with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
                for f in colour_files:z.writestr(f['name'],base64.b64decode(f['src'].split(',',1)[1]))
            data['colourDownload']={'name':re.sub(r'[\\/:*?"<>|]', '-',e.get('displayTitle') or e['name'])+'—上色图片','zip':'data:application/zip;base64,'+base64.b64encode(archive.getvalue()).decode()}
        filename=e.get('fileName') or re.sub(r'[\\/:*?"<>|]', '-',e.get('displayTitle') or e['name'])+'.html'
        if pathlib.Path(filename).name!=filename or any(c in filename for c in '/\\') or not filename.endswith('.html'):raise ValueError('fileName必须是单个HTML文件名')
        if filename in used_names:raise ValueError('期次文件名重复')
        used_names.add(filename)
        episodes.append({**{k:e.get(k,'') for k in ['id','name','summary']},'fileName':filename})
        rendered=page(data,theme)
        (output/filename).write_text(rendered,encoding='utf-8')
        if config.get('compatibilityAliases',True) and filename!=f"{e['id']}.html": (output/f"{e['id']}.html").write_text(rendered,encoding='utf-8')
    flow=[{'type':'table','label':'','columns':['步骤','完成内容'],'rows':[
        ['提供粗稿','在聊天中发一句话、画面或大致情节，可附画风、对白语言。'],
        ['确定页数','已指定则遵循；未指定则给页数输入框和建议理由，等待回答。格数按情节安排。'],
        ['完善脚本','保留核心想法，补全因果、角色、动作和对白，设计阅读节奏。'],
        ['制作速写','生成黑白粗稿，检查姿态、透视、表情、气泡与画面连续性。'],
        ['交付与调整','角色表及含逐页速写的脚本表，反馈持续更新个人规则。']]}]
    data={'kind':'library','episodeLinksPrefix':config.get('episodeLinksPrefix','期次/'),'name':'漫画工作室','topics':topics,'episodes':episodes,'rules':rules,'skills':[],
          'layoutLibrary':read('资料/布局参考.json'),'outputStandard':standard,'tabs':[{'label':'选题库','kind':'topics'},{'label':'每期内容','kind':'episodes'},{'label':'创作资料','kind':'resources','flow':flow}]}
    index_path.write_text(page(data,theme),encoding='utf-8')
    print(str(index_path))
    print('期次数：'+str(len(episodes)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=pathlib.Path);p.add_argument('--init',action='store_true');a=p.parse_args();build(a.root,a.init)
