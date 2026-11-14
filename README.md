# HighSchool-Chemistry-Forge v0.7

用于高中化学无答案试卷独立求解、面向有一点化学基础学生的易读讲解、科学复核和完整教辅PDF。完整保留知识索引、基础知识、提示词、校验脚本和参考规范。

## 本次更新
将完整试卷工作流、每题知识深度、打印验收标准与海淀19题回归案例固化。入口为SKILL.md；具体标准在references/complete-exam-workflow.md、lesson-depth.md、print-acceptance.md。data/haidian_verified.json为本案例独立解答记录，不称官方答案；课程索引中index_only仍表示尚未扩写或逐节点科学审查。

## 检查
python scripts/validate.py
python scripts/validate_topics.py
python scripts/validate_exam_manifest.py
python scripts/check_regression.py

通用渲染器scripts/build_teacher_pdf.py接受--original、--content、--output、--font、--heading-font、--symbol-font，输入文本用@@、##、!区分页面、标题和答案。需要reportlab与PyMuPDF。先渲染再逐页视觉检查；程序通过不能代替科学审查。

## 回归素材
assets/haidian_lessons.txt为完整自学讲解，可配合另行提供的原卷重建。第三方原卷和DOCX不在本Skill中再分发。本ZIP为完整可移植源码包。

## 参考答案写作
参考答案在详解前按题号列出。解释题采用“结构或事实→原理→性质或趋势→结论”的简洁完整句式，覆盖全部得分点；具体要求见references/standard-answer-writing.md。

## 默认读者与语言
默认学生认得常见化学式和简单反应，但还不会熟练解题。逐选项先用直白语言讲清对错及原因，再集中补知识与延伸。遇到新术语随文解释，不用术语替代推理。规范与样例见references/student-readable-explanations.md。完整历史案例保留为科学核验素材，其措辞不作为v0.7写法示范。
