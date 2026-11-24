# 项目数据

默认三目录布局见 [目录规范](workspace-layout.md)。下列资料路径相对 `底层文件/项目资料/`；图片src相对项目根目录下的 `图片/`。

构建：`python3 <技能目录>/scripts/build.py --root <项目目录>`。首次加 `--init`。初始化仅创建缺失的数据文件，不覆盖已有数据。

- `资料/选题库.json`：数组，每项 `{ "id":"topic-001", "name":"粗稿名称", "outline":"大概剧情" }`。无期次关联。
- `资料/个人规则.json`：`{"rules":[],"changes":[]}`，偏好变更可记录 date 和 text。
- `资料/输出标准.json`：首次从技能复制，后续可按此用户修改；包含 invocation 和 rows。
- `资料/布局参考.json`：来源信息及 entries；每项包含 id、name、source_order、user_note、observed、use_when、application、check。构建旧项目时仅补充缺失文件，已有文件保持原样。
- `资料/期次/issue-001.json`：每期独立源文件。
- 图片目录：项目根目录下 `图片/<中文标题>/速写稿/` 和 `图片/<中文标题>/上色图/`；最终内嵌HTML。

期次结构示意（示意不是预填故事，不复制为真实作品）：

```json
{
  "id": "issue-001",
  "name": "用户本期名称",
  "summary": "该期大纲",
  "defaultTab": 0,
  "showBack": false,
  "tabs": [
    {
      "label": "脚本",
      "blocks": [
        {
          "type": "table",
          "label": "脚本",
          "columns": [
            "页码",
            "速写稿",
            "场景描述",
            "对白"
          ],
          "rows": []
        }
      ]
    },
    {
      "label": "角色描述",
      "blocks": [
        {
          "type": "table",
          "label": "角色描述",
          "columns": [
            "角色",
            "外形与服饰",
            "关系与动作特征"
          ],
          "rows": []
        }
      ]
    }
  ]
}
```

脚本每页一行：`["1",{"type":"image","src":"素材/issue-001-page-1.png","alt":"第1页速写"},"整页大致场景","角色：对白"]`。

没有出图能力或图片尚未完成时，图片格使用空字符串；向用户解释限制，不能把空单元格当作速写完成。人物表每行3列；未上色脚本表每行4列，上色后每行5列，新增“上色图”位于“速写稿”右侧。不同页可含任意合理格数。表中对白必须和图一致。

首次完成作品才创建期次；不在空白项目填充示例。修改既有作品前把源JSON复制到归档目录，图像使用新版文件名。构建会重写HTML；不要把用户仅在浏览器上传的图宣称为磁盘素材。建议用户导出含图片页面保留浏览器上传结果。

可选 `layoutPlan` 保存内部布局决策，例如 `[{"page":1,"references":["layout-09"],"reason":"先遮挡再揭示观察者","readingOrder":"左到右，上到下","continuity":"门的位置与人物视线保持一致"}]`。不默认显示在脚本表中。

- `资料/主题.css`：项目配色与布局；首次初始化从随包主题创建，后续保留用户修改。
- `referenceReview`：本次实际查看原图的来源、时间、revision与图片编号。
- 新作品建脚本、角色描述、自媒体内容三个标签（按此顺序），不设置 `hideNavigation:true`；`showBack:false` 隐藏返回。旧作品改格式前归档原JSON，保留旧素材。

- 详情页默认隐藏与当前Tab同名的重复表格标题；`hideDuplicateHeadings:false` 仅在用户要求重复标题时使用。


表格块可加 `"columnWidths":[64,307.2,307.2,520,420]`，须与 columns 数量一致且均为正数。上色表 columns 为 `["页码","速写稿","上色图","场景描述","对白"]`；两图片格均使用 image 对象。省略 columnWidths 时，脚本和角色表使用生成器固定默认宽度，整表可横向滚动。图片文件按01.png等排序，图片内不加页码。


## 期次标题与社媒文案

期次可设置 `displayTitle`（中文页面标题）、`englishTitle`（英文副标题）、`fileName`（例如 `001-中文标题.html`）。内部id仍使用issue-001；首页使用fileName链接，默认不保留旧id重复地址。标题不得包含路径，文件名不得与其他期次冲突。

第三个标签为自媒体内容，使用table块，columns为 `["项目","中文","英文（目标受众）"]`，columnWidths为 `[160,520,640]`，rows包含主推标题、标签、正文与可选备选标题。

生成后的colourDownload字段由构建器生成，不手工将base64写入源JSON；上色列会自动显示整期下载按钮。详见titles-social-download.md。


## 分目录项目配置

项目可在源资料根目录放置项目配置.json：htmlDirectory指定HTML输出目录，assetDirectory指定图片根目录，indexFile指定目录网页路径，episodeLinksPrefix指定首页链接前缀，compatibilityAliases=false停止生成id.html重复副本。路径相对源资料根目录解析。

当前整理型布局：顶层HTML只放中文命名网页，图片按每期标题区分速写稿、上色图；Skill与项目资料一起放入底层文件。通过 `python3 ../Skill/comic-draft-studio/scripts/build.py --root <项目资料目录>` 重建。不再将旧目录、历史ZIP或重复导出复制回交付区。删除历史稿仍需用户授权。
