# MangaTag 标注与验证

## 入口与资料来源

优先使用本机 `mangatag` CLI 或 MangaTag 工作台。如果命令不在 PATH 中，先定位 MangaTag 的工作树，再检查其虚拟环境中的 `.venv/bin/mangatag`。具体能力以 `mangatag scan FILE`、命令的 `--help` 和项目 README 为准。

- 先读同卷封面、版权页、原目录、内嵌书目或书签。书目按作品、版本和卷区分。已核实的名称、作者、绘者、出版社、出版语言、原文语言、阅读方向、卷号、ISBN 或日期写入适当字段。单行本卷号用 `volume`，只有确实需要阅读器显示为 ComicInfo 期号时才另设 `issue`。
- 可用 `mangatag metadata search --book FILE --source mangabaka` 找作品，或 `mangatag metadata search ISBN --source ndl` 查对应日版书目。当前版优先用该版书内证据与出版社或书目馆记录。区分原作开始年份、日版单卷发行日期和当前版出版日。不同版本的 ISBN、卷标题、译者不可移用，无法确定的字段留空并记录来源。
- 目录从原生导航、书内目录图、章节标题页或可靠的版别资料取证。保留已有正确条目，OCR 和文件名只用来找候选。印刷页码、图像序号和电子阅读单元可能不同。对每种版式校对开头、中间、末尾和异常页，跨页图锚到实际包含章节开始的图。遇到剧情先于标题页时保留剧情起点。分话单文件没有需要另设的内部章节时，可只标书目，并在既有进度记录中注明。

## 写入和回读

- `mangatag metadata get FILE` 查看原生和完整视图；`mangatag chapters export FILE` 导出可读回的章节结构；`mangatag chapters detect FILE --ocr --start-page 1 --max-pages 8` 可尝试找候选。CLI 的 `--page` 从 1 起，JSON 的 `start.index` 从 0 起。以 `open_book(path).units()` 的实际资源确认锚点。
- CLI 的写入默认只预览，加 `--apply` 后才保存。批量同时改书目和章节，可用 MangaTag 的 `comicapi.book.open_book`、`Chapter` 与 `comicapi.book.save.save_copy(book, destination, metadata, chapters, provenance=...)` 在一次导出中写入。先检查已有内容，再组装修改后的清单。需要保留源格式但原生写入受限时，把书复制到成品工作区，用 `--sidecar` 或 `save_sidecar` 写入对应侧车。
- CBZ 主要写 ComicInfo，原生 Bookmark 每张图最多一条。完整层级或同页多条留在侧车。EPUB 在可写时保留原格式及版式，使用原生 NCX/Nav。MOBI 原生目录只读，章节用侧车；少量原生元数据能否写入取决于 calibre 和文件能力。侧车可供支持它的工具读取，只有原生目录写入后才可称普通阅读器可见的书内目录。
- 每本成品运行 `mangatag verify FILE`，并检查实际 `results` 覆盖所要求的文件。回读卷号、语言、版别、章节数量、顺序、锚点和侧车匹配。CBZ/EPUB 用 MangaTag 保存时会检查阅读资源或版式保留。对转换后的 CBZ 另核对页数、阅读顺序、原图内容和章节重映射。书与侧车按最终书名配对，保持同目录。
- 大套按卷并行审目录或导出，可用多组清单加一个主清单记录状态。先验证可代表各版式的一小批，随后复用已验证的页序规则，逐卷核对偏移。已验证的分组可先上传到暂存，不必等其余卷写完。
