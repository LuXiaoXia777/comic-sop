"""Initialize and build a portable comic workspace. Python 3.9+, standard library."""
import argparse, base64, copy, html, json, mimetypes, pathlib, re
from renderer import CSS, JS
SKILL=pathlib.Path(__file__).resolve().parent.parent

def write_default(path,value):
    if not path.exists(): path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def page(data):
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(data.get('name','漫画工作室'))+'</title><style>'+CSS+'</style><body><nav role="tablist" aria-label="内容分类"></nav><main></main><div id="status" class="status" role="status" aria-live="polite"></div><script id="data" type="application/json">'+payload+'</script><script>'+JS+'</script></body></html>'

def build(root,initialize=False):
    root=root.resolve()
    if initialize:
        for folder in ['资料/期次','期次','素材','归档']: (root/folder).mkdir(parents=True,exist_ok=True)
        write_default(root/'资料/选题库.json',[])
        write_default(root/'资料/个人规则.json',{'rules':[],'changes':[]})
        write_default(root/'资料/输出标准.json',json.loads((SKILL/'references/output-standard.json').read_text(encoding='utf-8')))
    # Add reference defaults to old projects without overwriting user edits.
    write_default(root/'资料/布局参考.json',json.loads((SKILL/'references/layout-library.json').read_text(encoding='utf-8')))
    read=lambda path:json.loads((root/path).read_text(encoding='utf-8'))
    topics=read('资料/选题库.json');rules=read('资料/个人规则.json');standard=read('资料/输出标准.json')
    episodes=[]
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
                            asset=(root/cell['src']).resolve()
                            if root not in asset.parents:raise ValueError('图片必须位于用户项目内')
                            mime=mimetypes.guess_type(asset.name)[0]
                            if mime not in ['image/png','image/jpeg','image/webp','image/gif']:raise ValueError('使用PNG、JPEG、WebP或GIF图片')
                            cell['src']='data:'+mime+';base64,'+base64.b64encode(asset.read_bytes()).decode()
        episodes.append({k:e.get(k,'') for k in ['id','name','summary']})
        (root/'期次'/f"{e['id']}.html").write_text(page(data),encoding='utf-8')
    flow=[{'type':'table','label':'','columns':['步骤','完成内容'],'rows':[
        ['提供粗稿','在聊天中发一句话、画面或大致情节，可附画风、对白语言。'],
        ['确定页数','已指定则遵循；未指定则给页数输入框和建议理由，等待回答。格数按情节安排。'],
        ['完善脚本','保留核心想法，补全因果、角色、动作和对白，设计阅读节奏。'],
        ['制作速写','生成黑白粗稿，检查姿态、透视、表情、气泡与画面连续性。'],
        ['交付与调整','角色表及含逐页速写的脚本表，反馈持续更新个人规则。']]}]
    data={'kind':'library','name':'漫画工作室','topics':topics,'episodes':episodes,'rules':rules,'skills':[],
          'layoutLibrary':read('资料/布局参考.json'),'outputStandard':standard,'tabs':[{'label':'选题库','kind':'topics'},{'label':'每期内容','kind':'episodes'},{'label':'创作资料','kind':'resources','flow':flow}]}
    (root/'index.html').write_text(page(data),encoding='utf-8')
    print(str(root/'index.html'))
    print('期次数：'+str(len(episodes)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=pathlib.Path);p.add_argument('--init',action='store_true');a=p.parse_args();build(a.root,a.init)
