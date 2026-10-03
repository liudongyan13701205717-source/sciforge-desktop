# MCP 工具清单（65 个）

> 本文档由 `sciforge/server.py` 自动生成，记录所有 `@mcp.tool()` 装饰的 MCP 工具。
> 静态计数 65，运行时 `mcp.list_tools()` 计数 65，两者一致。

## 工具总表

| # | 工具名 | 功能简述 | 参数 |
| --- | --- | --- | --- |
| 1 | `reproduce_paper` | 论文复现五步闭环：解析 PDF → 复现方案 → 生成代码 → 沙箱运行比对 → 产出交付物。 | pdf_path: str, framework: str |
| 2 | `reproduce_status` | 查询论文复现任务的异步状态与阶段进度。 | task_id: str |
| 3 | `write_section` | 论文写作助力：按章节引导生成内容（摘要/问题/假设/符号/建模/求解/结果/参考文献/附录）。 | paper_id: str, section: str, prompt: str, format: str |
| 4 | `export_document` | 论文写作助力：将已写 doc（markdown）导出为 LaTeX / PDF / docx。 | paper_id: str, target: str |
| 5 | `get_deliverables` | 端到端交付：列出某任务（复现/写作）的交付物清单（图/数据/源码/报告）。 | task_id: str |
| 6 | `ideate_paper` | 研究起点：由研究方向构思选题，产出研究缺口、候选假设、多视角评审与实验计划。 | topic: str, paper_id: str |
| 7 | `inject_results` | 将复现任务的真实实验结果并入论文对应章节（实验数据→论文）。 | paper_id: str, task_id: str, section: str |
| 8 | `research_verdict` | 结果分析自旋门：根据复现产物给出 PROCEED/REFINE/PIVOT 决策建议。 | task_id: str |
| 9 | `research_plan` | 研究计划书：由选题展开成完整研究计划（RQ/假设/目标/贡献/方法/数据/ | topic: str, paper_id: str |
| 10 | `literature_review` | 文献综述：基于免 key OpenAlex 检索生成综述框架（代表文献/主题聚类/ | topic: str, paper_id: str |
| 11 | `auto_title_abstract` | 标题/摘要/关键词提炼：从已写正文自动生成投稿所需元数据。 | paper_id: str |
| 12 | `peer_review` | 模拟同行评审：对已有论文生成结构化审稿意见（novelty/rigor/clarity/ | paper_id: str |
| 13 | `venue_suggest` | 投稿建议：根据主题/关键词推荐目标期刊与会议（内置映射库 + 可选 LLM）。 | topic: str, paper_id: str |
| 14 | `paper_polish` | 论文润色与检查：对已有正文做质量检查并产出建议。 | paper_id: str, mode: str |
| 15 | `compare_metrics` | 对比表与显著性检验：汇总多个任务/基线的指标序列并做检验。 | paper_id: str, tasks: list[str], baseline: str, metric: str |
| 16 | `check_novelty` | 创新性检查：从标题/摘要抽关键词检索相似工作，给出重叠与候选差异点。 | paper_id: str, max_papers: int |
| 17 | `package_submission` | 投稿材料一键打包：把论文导出物与研究/复现产物打成 zip（含 cover letter）。 | paper_id: str, task_id: str |
| 18 | `citation_landscape` | 引文邻域与热度分析：围绕 DOI 或主题分析热度/年度分布/高被引代表。 | paper_id: str, doi_or_topic: str |
| 19 | `project_memory` | 项目进度记账：为论文/项目维护可回溯 timeline（备忘/里程碑/状态）。 | paper_id: str, action: str, note: str, milestone: str, status: str |
| 20 | `review_code` | 复现代化码静态点评：对任务下的 .py 做风格/风险/可复现性检查。 | task_id: str |
| 21 | `science_list_dbs` | 列出当前可用的科学数据库（跨 7 大领域，共 41 个），可按领域筛选。 | domain: str |
| 22 | `science_search` | 在指定科学数据库中进行关键词检索。 | database: str, query: str, limit: int |
| 23 | `science_fetch` | 按记录 ID 从指定科学数据库获取单条完整记录。 | database: str, id: str, format: str |
| 24 | `science_cross_lookup` | 跨多个科学数据库联合查询同一关键词。 | query: str, databases: list[str] | None, limit: int |
| 25 | `science_batch_search` | 批量跨库检索：在多个数据库上并行执行同一查询并汇总结果。 | query: str, databases: list[str] | None, limit: int |
| 26 | `ref_to_bibtex` | 按 DOI 生成 BibTeX 条目。 | doi: str |
| 27 | `batch_ref_export` | 批量导出参考文献：解析文本中的 DOI/引用，转成 BibTeX 条目。 | text: str |
| 28 | `recommend_papers` | 围绕研究主题推荐论文。 | topic: str, limit: int, sources: list[str] | None |
| 29 | `run_panel` | 多视角同行评审面板（7 席位：field_analyst/eic/methodology_R1/domain_R2/perspective_R3/devils_advocate/editorial_synthesizer）。 | text: str, mode: str, journal: str, design: str, adjudications: dict | None, author_response: str, gold_set: list | None, paper_id: str, layout |
| 30 | `validate_review_intake` | 评审准入门：校验评审请求是否满足本地评审前置条件（fail-closed）。 | intake: dict |
| 31 | `select_reporting_guidelines` | 按研究设计选择报告指南并做覆盖审计（非计分、带日期）。 | design: str, text: str, as_of: str |
| 32 | `validate_claims_evidence` | claim/evidence 对齐矩阵：每条 claim 判定 ALIGNED / PARTIAL / UNSUPPORTED。 | claims: list, evidence: list |
| 33 | `review_panel_intake` | 评审准入门（兼容旧名，等同 validate_review_intake）。 | intake: dict |
| 34 | `select_guidelines` | 报告指南选择（兼容旧名，等同 select_reporting_guidelines）。 | design: str, text: str, as_of: str |
| 35 | `claims_evidence_matrix` | claim/evidence 对齐矩阵（兼容旧名，等同 validate_claims_evidence）。 | claims: list, evidence: list |
| 36 | `verify` | claim→source 核验：解析 doc.md 中 claims + 引文（含锚点），5 类锚点分类，输出 gate_refuse。 | text: str, sources: dict | None |
| 37 | `gate_2_5` | 完整性门 Stage 2.5：代码生成 → 执行之间的完整性门。 | context: dict |
| 38 | `gate_4_5` | 完整性门 Stage 4.5：结果 → 论文/交付之间的完整性门。 | context: dict |
| 39 | `run_gates` | 一次性跑两道完整性门（2.5 + 4.5）。 | context: dict |
| 40 | `request_bypass` | fail-closed bypass：无理由拒绝放行；有理由记录放行。 | gate: dict, reason: str |
| 41 | `build_passport` | Material Passport（per-run artifact）：含 experiment provenance + claim 审计。 | task_id: str, results: dict | None, runs: list | None, claims: list | None, gate_results: dict | None, hypothesis: str, negative_results: list | None, doc_text: str, as_of: str |
| 42 | `journal_fit` | journal-fit 评分：论文与目标期刊/会议的匹配度（领域/体裁/方法/结构/合规）。 | paper_text: str, venue: str |
| 43 | `list_disciplines` | 列出当前注册的学科（自动发现，零注册即可发现）。 | domain: str |
| 44 | `get_discipline` | 获取指定学科的完整配置（结构体裁/引用样式/报告标准/顶刊/单位公式）。 | name: str |
| 45 | `prisma_review` | PRISMA 系统综述：7 阶段协议（规划→多库检索→筛选→全文评估→主题综合→引文核验→文档生成），带流程计数。 | topic: str, hits: list[dict] | None, databases: list[str] | None, limit: int, include_keywords: list[str] | None, exclude_keywords: list[str] | None, paper_id: str, persist: bool |
| 46 | `convert_citation` | 引用样式转换：解析 BibTeX 条目并渲染为指定样式。 | bibtex: str, style: str |
| 47 | `convert_citation_all` | 引用样式一键转换：BibTeX → 全部 6 种样式（APA/Chicago×2/MLA/IEEE/Vancouver）。 | bibtex: str |
| 48 | `revision_coach` | 修订教练：评审意见 → 结构化路线图（comment→类型 CRITICAL/MAJOR/MINOR→位置→回应计划）。 | comments_text: str, paper_id: str |
| 49 | `rebuttal_audit` | rebuttal 审计：逐条检查 rebuttal 是否回应了每条评审意见（fail-closed）。 | rebuttal_text: str, comments: str, paper_id: str |
| 50 | `detect_style` | 机器文风检测：hedging 密度 + 模板化句式 + 空洞连接词 → 0-100 分 + 证据列表。 | text: str |
| 51 | `claim_strength` | claim-strength ladder：检测表述强度（associated<predicts<causes）与无授权的强度上移。 | text: str |
| 52 | `calibrate_style` | 风格校准：从已有正文学习作者声音画像（句长分布/用词偏好/结构习惯）。 | text: str |
| 53 | `score_style_text` | 文风评分：新文本与作者画像的相似度（0-100，越高越接近作者声音）。 | text: str, profile: dict |
| 54 | `verify_citation` | 引用核验：核验单个 DOI 是否真实存在（Crossref）。离线可用、免 key。 | doi: str |
| 55 | `verify_claim` | 主张核验：检索 OpenAlex 支持证据并判定 SUPPORTED/PARTIAL/UNSUPPORTED。离线可用、免 key。 | claim: str, topic: str, limit: int |
| 56 | `verify_reference_list` | 批量引用核验：逐条核验参考文献 DOI。离线可用、免 key。 | refs: list[str] |
| 57 | `paper_metadata` | 论文元数据：经 Crossref 获取标题/作者/年份/期刊/摘要。离线可用、免 key。 | doi: str |
| 58 | `citation_graph` | 引用图谱：经 OpenAlex 获取被引数与参考文献。离线可用、免 key。 | doi: str, depth: int |
| 59 | `download_paper_pdf` | 论文 PDF 下载：经 OpenAlex OA 定位并下载开放获取 PDF。离线可用、免 key。 | doi: str, out_dir: str |
| 60 | `scout_topic` | 主题侦察：多源聚合检索 + 去重 + 评分排序（被引/新近度/关键词）。离线可用、免 key。 | topic: str, limit: int |
| 61 | `scout_compare` | 主题对比：多主题横向对比（按命中数降序）。离线可用、免 key。 | topics: list[str], limit: int |
| 62 | `rag_answer` | 检索增强问答：检索相关文献并用本地模板合成答案（无 LLM）。离线可用、免 key。 | question: str, topic: str, limit: int |
| 63 | `rag_sources` | RAG 来源：仅检索并排序相关来源（按被引降序）。离线可用、免 key。 | question: str, limit: int |
| 64 | `find_code_for_paper` | 论文找代码：定位论文并检索关联代码/数据集（HuggingFace/Zenodo）。离线可用、免 key。 | title: str, limit: int |
| 65 | `link_papers_to_code` | 主题找代码：主题论文批量关联代码/数据集。离线可用、免 key。 | topic: str, limit: int |

## 按功能线分组

### 复现线

| 工具名 | 功能简述 | 参数 |
| --- | --- | --- |
| `reproduce_paper` | 论文复现五步闭环：解析 PDF → 复现方案 → 生成代码 → 沙箱运行比对 → 产出交付物。 | pdf_path: str, framework: str |
| `reproduce_status` | 查询论文复现任务的异步状态与阶段进度。 | task_id: str |

### 写作线

| 工具名 | 功能简述 | 参数 |
| --- | --- | --- |
| `write_section` | 论文写作助力：按章节引导生成内容（摘要/问题/假设/符号/建模/求解/结果/参考文献/附录）。 | paper_id: str, section: str, prompt: str, format: str |
| `export_document` | 论文写作助力：将已写 doc（markdown）导出为 LaTeX / PDF / docx。 | paper_id: str, target: str |

### 研究线

| 工具名 | 功能简述 | 参数 |
| --- | --- | --- |
| `ideate_paper` | 研究起点：由研究方向构思选题，产出研究缺口、候选假设、多视角评审与实验计划。 | topic: str, paper_id: str |
| `inject_results` | 将复现任务的真实实验结果并入论文对应章节（实验数据→论文）。 | paper_id: str, task_id: str, section: str |
| `research_verdict` | 结果分析自旋门：根据复现产物给出 PROCEED/REFINE/PIVOT 决策建议。 | task_id: str |

### 科研/论文线

| 工具名 | 功能简述 | 参数 |
| --- | --- | --- |
| `research_plan` | 研究计划书：由选题展开成完整研究计划（RQ/假设/目标/贡献/方法/数据/ | topic: str, paper_id: str |
| `literature_review` | 文献综述：基于免 key OpenAlex 检索生成综述框架（代表文献/主题聚类/ | topic: str, paper_id: str |
| `auto_title_abstract` | 标题/摘要/关键词提炼：从已写正文自动生成投稿所需元数据。 | paper_id: str |
| `peer_review` | 模拟同行评审：对已有论文生成结构化审稿意见（novelty/rigor/clarity/ | paper_id: str |
| `venue_suggest` | 投稿建议：根据主题/关键词推荐目标期刊与会议（内置映射库 + 可选 LLM）。 | topic: str, paper_id: str |
| `paper_polish` | 论文润色与检查：对已有正文做质量检查并产出建议。 | paper_id: str, mode: str |
| `compare_metrics` | 对比表与显著性检验：汇总多个任务/基线的指标序列并做检验。 | paper_id: str, tasks: list[str], baseline: str, metric: str |
| `check_novelty` | 创新性检查：从标题/摘要抽关键词检索相似工作，给出重叠与候选差异点。 | paper_id: str, max_papers: int |
| `citation_landscape` | 引文邻域与热度分析：围绕 DOI 或主题分析热度/年度分布/高被引代表。 | paper_id: str, doi_or_topic: str |
| `project_memory` | 项目进度记账：为论文/项目维护可回溯 timeline（备忘/里程碑/状态）。 | paper_id: str, action: str, note: str, milestone: str, status: str |
| `review_code` | 复现代化码静态点评：对任务下的 .py 做风格/风险/可复现性检查。 | task_id: str |
| `ref_to_bibtex` | 按 DOI 生成 BibTeX 条目。 | doi: str |
| `batch_ref_export` | 批量导出参考文献：解析文本中的 DOI/引用，转成 BibTeX 条目。 | text: str |
| `recommend_papers` | 围绕研究主题推荐论文。 | topic: str, limit: int, sources: list[str] | None |
| `prisma_review` | PRISMA 系统综述：7 阶段协议（规划→多库检索→筛选→全文评估→主题综合→引文核验→文档生成），带流程计数。 | topic: str, hits: list[dict] | None, databases: list[str] | None, limit: int, include_keywords: list[str] | None, exclude_keywords: list[str] | None, paper_id: str, persist: bool |
| `convert_citation` | 引用样式转换：解析 BibTeX 条目并渲染为指定样式。 | bibtex: str, style: str |
| `convert_citation_all` | 引用样式一键转换：BibTeX → 全部 6 种样式（APA/Chicago×2/MLA/IEEE/Vancouver）。 | bibtex: str |
| `revision_coach` | 修订教练：评审意见 → 结构化路线图（comment→类型 CRITICAL/MAJOR/MINOR→位置→回应计划）。 | comments_text: str, paper_id: str |
| `rebuttal_audit` | rebuttal 审计：逐条检查 rebuttal 是否回应了每条评审意见（fail-closed）。 | rebuttal_text: str, comments: str, paper_id: str |
| `detect_style` | 机器文风检测：hedging 密度 + 模板化句式 + 空洞连接词 → 0-100 分 + 证据列表。 | text: str |
| `claim_strength` | claim-strength ladder：检测表述强度（associated<predicts<causes）与无授权的强度上移。 | text: str |
| `calibrate_style` | 风格校准：从已有正文学习作者声音画像（句长分布/用词偏好/结构习惯）。 | text: str |
| `score_style_text` | 文风评分：新文本与作者画像的相似度（0-100，越高越接近作者声音）。 | text: str, profile: dict |
| `verify_citation` | 引用核验：核验单个 DOI 是否真实存在（Crossref）。离线可用、免 key。 | doi: str |
| `verify_claim` | 主张核验：检索 OpenAlex 支持证据并判定 SUPPORTED/PARTIAL/UNSUPPORTED。离线可用、免 key。 | claim: str, topic: str, limit: int |
| `verify_reference_list` | 批量引用核验：逐条核验参考文献 DOI。离线可用、免 key。 | refs: list[str] |
| `paper_metadata` | 论文元数据：经 Crossref 获取标题/作者/年份/期刊/摘要。离线可用、免 key。 | doi: str |
| `citation_graph` | 引用图谱：经 OpenAlex 获取被引数与参考文献。离线可用、免 key。 | doi: str, depth: int |
| `download_paper_pdf` | 论文 PDF 下载：经 OpenAlex OA 定位并下载开放获取 PDF。离线可用、免 key。 | doi: str, out_dir: str |
| `scout_topic` | 主题侦察：多源聚合检索 + 去重 + 评分排序（被引/新近度/关键词）。离线可用、免 key。 | topic: str, limit: int |
| `scout_compare` | 主题对比：多主题横向对比（按命中数降序）。离线可用、免 key。 | topics: list[str], limit: int |
| `rag_answer` | 检索增强问答：检索相关文献并用本地模板合成答案（无 LLM）。离线可用、免 key。 | question: str, topic: str, limit: int |
| `rag_sources` | RAG 来源：仅检索并排序相关来源（按被引降序）。离线可用、免 key。 | question: str, limit: int |
| `find_code_for_paper` | 论文找代码：定位论文并检索关联代码/数据集（HuggingFace/Zenodo）。离线可用、免 key。 | title: str, limit: int |
| `link_papers_to_code` | 主题找代码：主题论文批量关联代码/数据集。离线可用、免 key。 | topic: str, limit: int |

### 评审与核验线

| 工具名 | 功能简述 | 参数 |
| --- | --- | --- |
| `run_panel` | 多视角同行评审面板（7 席位：field_analyst/eic/methodology_R1/domain_R2/perspective_R3/devils_advocate/editorial_synthesizer）。 | text: str, mode: str, journal: str, design: str, adjudications: dict | None, author_response: str, gold_set: list | None, paper_id: str, layout |
| `validate_review_intake` | 评审准入门：校验评审请求是否满足本地评审前置条件（fail-closed）。 | intake: dict |
| `select_reporting_guidelines` | 按研究设计选择报告指南并做覆盖审计（非计分、带日期）。 | design: str, text: str, as_of: str |
| `validate_claims_evidence` | claim/evidence 对齐矩阵：每条 claim 判定 ALIGNED / PARTIAL / UNSUPPORTED。 | claims: list, evidence: list |
| `verify` | claim→source 核验：解析 doc.md 中 claims + 引文（含锚点），5 类锚点分类，输出 gate_refuse。 | text: str, sources: dict | None |
| `gate_2_5` | 完整性门 Stage 2.5：代码生成 → 执行之间的完整性门。 | context: dict |
| `gate_4_5` | 完整性门 Stage 4.5：结果 → 论文/交付之间的完整性门。 | context: dict |
| `run_gates` | 一次性跑两道完整性门（2.5 + 4.5）。 | context: dict |
| `request_bypass` | fail-closed bypass：无理由拒绝放行；有理由记录放行。 | gate: dict, reason: str |
| `build_passport` | Material Passport（per-run artifact）：含 experiment provenance + claim 审计。 | task_id: str, results: dict | None, runs: list | None, claims: list | None, gate_results: dict | None, hypothesis: str, negative_results: list | None, doc_text: str, as_of: str |

### 交付线

| 工具名 | 功能简述 | 参数 |
| --- | --- | --- |
| `get_deliverables` | 端到端交付：列出某任务（复现/写作）的交付物清单（图/数据/源码/报告）。 | task_id: str |
| `package_submission` | 投稿材料一键打包：把论文导出物与研究/复现产物打成 zip（含 cover letter）。 | paper_id: str, task_id: str |

### 科学数据线

| 工具名 | 功能简述 | 参数 |
| --- | --- | --- |
| `science_list_dbs` | 列出当前可用的科学数据库（跨 7 大领域，共 41 个），可按领域筛选。 | domain: str |
| `science_search` | 在指定科学数据库中进行关键词检索。 | database: str, query: str, limit: int |
| `science_fetch` | 按记录 ID 从指定科学数据库获取单条完整记录。 | database: str, id: str, format: str |
| `science_cross_lookup` | 跨多个科学数据库联合查询同一关键词。 | query: str, databases: list[str] | None, limit: int |
| `science_batch_search` | 批量跨库检索：在多个数据库上并行执行同一查询并汇总结果。 | query: str, databases: list[str] | None, limit: int |

### 期刊匹配与学科

| 工具名 | 功能简述 | 参数 |
| --- | --- | --- |
| `journal_fit` | journal-fit 评分：论文与目标期刊/会议的匹配度（领域/体裁/方法/结构/合规）。 | paper_text: str, venue: str |
| `list_disciplines` | 列出当前注册的学科（自动发现，零注册即可发现）。 | domain: str |
| `get_discipline` | 获取指定学科的完整配置（结构体裁/引用样式/报告标准/顶刊/单位公式）。 | name: str |

### 兼容别名

| 别名 | 等价于 |
| --- | --- |
| `review_panel_intake` | `validate_review_intake` |
| `select_guidelines` | `select_reporting_guidelines` |
| `claims_evidence_matrix` | `validate_claims_evidence` |

## MCP 资源

| URI | 类型 | 内容 |
| --- | --- | --- |
| `science://databases` | 静态资源 | 全部 46 个连接器清单 + 7 个领域 |
| `science://databases/{domain}` | 参数化模板 | 单个领域下的连接器清单 |
