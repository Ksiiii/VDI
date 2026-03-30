# 多螺栓法兰连接装配小样本任务的 Tabular Foundation Model 领域适配研究框架（V1.0）

## 一、研究总目标与核心问题

本课题的目标是围绕“多螺栓法兰连接装配中最小垫片接触压力/密封安全裕量预测”这一具体工程问题，建立一个面向装配小样本任务的统一 benchmark 包，并据此系统研究现成 tabular foundation model 在工程高保真样本稀缺、低保真解析样本丰富条件下的领域适配问题。

本课题拟回答四个核心研究问题：  
1. 为什么原始 TabPFN/TabPFN-2.5 在装配小样本任务上不够好；  
2. 如何构建一个既真实又可复用的高保真 benchmark 包，使模型比较具备统一且公平的协议；  
3. 如何将 VDI2230、PCC-1、工艺规则、简化模型和参数扫描组织成一个具有物理意义的 low-fidelity synthetic universe；  
4. 如何通过装配导向的 synthetic subset selection 与 continued adaptation 缓解 synthetic-real domain gap，并提升数据效率、稳健性与可解释性。  

## 二、研究定位：不是重新造 backbone，而是做领域适配

本课题的研究定位不是重新设计一个全新的大型表格模型，也不是从零训练 foundation model。主线是将已有 tabular foundation model 视为强基础模型，将创新点集中在“领域化适配”而非“底层骨干重造”。

这一路线与两类近期工作在思想上高度一致：一类工作强调 continued pre-training 可以使 TabPFN 更适应真实世界表格分布；另一类工作强调可以先识别与目标领域更相似的 synthetic data，再利用这些 synthetic tasks 做适配。基于此，本课题提出一个更适合装配场景的版本：以高保真法兰装配 benchmark 为目标域，以物理可解释的 low-fidelity subsets 为适配源，通过 subset-level selection 与 domain-aware adaptation 实现性能提升。

## 三、论文主线的总体框架

整体框架分为五层：

1. **母场景定义**：固定一个工程上明确、后续可扩展的多螺栓法兰连接装配母场景，作为所有实验、比较与扩展的共同语境。  
2. **高保真 benchmark 包**：通过有限元建模生成正式的 train/val/test 数据，并在同一母场景下设置多个子场景与多个任务，形成统一 benchmark 包。  
3. **Low-fidelity synthetic universe**：通过 VDI2230、PCC-1、工艺规则、等效模型和参数扫描，构建 1 万到 10 万量级的解析/半解析样本宇宙。  
4. **subset-level selection + continued adaptation**：将 synthetic universe 划分为多个具有物理意义的 subsets，筛选出最接近高保真目标域的 subset 组合，并对 TabPFN 做 continued adaptation。  
5. **统一协议评测与分析**：在完全相同的高保真 train/val/test 协议下，对原始模型、适配后模型与强 baseline 进行公平比较，并开展数据效率、合理性与失败模式分析。  

## 四、benchmark 包设计：必须是“包”，不能只是一个 csv

本课题的 benchmark 不应只是一个单任务回归表，而应是一个统一 benchmark 包。其设计原则如下：

1. 同一母场景；  
2. 多个子场景；  
3. 多个任务；  
4. 统一协议。  

第一篇论文不宜把 benchmark 做得过宽。建议在 V1 版本中，优先固定一个主法兰构型，只开放少数几个最能体现 domain gap 的控制因素，例如螺栓数、垫片等效刚度、摩擦/预紧离散与偏心等级。

## 五、输入/输出与桥接语义层：当前初稿的正式化解释

现有输入输出初稿已经具备较好的三层结构，应作为后续数据工程与论文写作的基础骨架。

1. **共享核心输入层**：定义高低保真共同使用的“母参数语言”。  
2. **benchmark 主输出层**：定义论文对外报告的核心任务标签。  
3. **低高保真桥接语义层**：定义 low-fidelity 与 high-fidelity 之间的“功能语义接口”。  

桥接层存在的意义在于：高低保真不能只在输入变量上对齐，还要在“功能解释层”上对齐。后续做 subset selection、分布匹配、适配前后分析时，桥接层会提供比原始输入更稳定、也更工程可解释的比较空间。

## 六、为什么采用 subset-level selection，而不是 sample-level selection

本课题不建议直接做样本级 selection，原因如下：

1. low-fidelity synthetic data 并非无结构的 iid 样本，而是由物理因素共同诱导出的结构化样本簇；  
2. sample-level selection 会破坏分布结构，不利于 continued adaptation 学习稳定领域先验；  
3. subset-level selection 更符合“域”的概念，更有工程可解释性，也更适合后续做消融与失败模式分析。  

因此，selection 的对象应是 subset 或 subset 组合，而不是孤立单点样本。

## 七、synthetic subset selection 的推荐实现思路

建议采用“由简到繁”的两阶段路线：

- 阶段 A：构建 subset 元信息与统计描述；  
- 阶段 B：定义与高保真目标域的相似性评分。  

评分可由输入空间相似性、桥接语义相似性、任务相关性、表示层相似性组合而成。第一版建议优先采用“统计距离 + 轻量代理模型验证”的混合评分方案。

## 八、continued adaptation 设计：主线建议

推荐主线：

1. 从原始 TabPFN/TabPFN-2.5 checkpoint 出发；  
2. 使用 selection 选出的 subset 组合构造适配训练源；  
3. 在不改 backbone 基本结构的前提下做 continued adaptation；  
4. 再回到统一高保真 benchmark 协议下评测。  

建议第一版先固定三种方案：  
- 原始 TabPFN；  
- selected subsets 适配后的 TabPFN；  
- adaptation 后再加少量高保真微调的增强版本（可选）。  

## 九、baseline、评测协议与分析维度

建议 baseline：XGBoost、LightGBM、RF、MLP、原始 TabPFN、适配后的 TabPFN。  

建议分析维度：  
- 主任务精度；  
- 小样本数据效率；  
- selection 合理性分析；  
- 稳健性分析；  
- 失败模式分析；  
- 工程一致性分析。  

## 十、论文贡献点建议表述

1. 提出一个面向多螺栓法兰连接密封预测的统一高保真 benchmark 包；  
2. 构建基于标准、规则和简化模型的 low-fidelity synthetic universe，并组织为物理有意义的 subsets；  
3. 提出装配领域的小样本 subset-level selection + continued adaptation 路线；  
4. 系统验证领域化 synthetic selection 对数据效率、精度和失败模式的影响。  

## 十一、当前不应作为主线的内容

- 从零设计新的 PITT-Bolt 式 backbone；  
- 过早引入复杂多模态模型；  
- 过早把 Agent 封装作为论文主体；  
- 过早把 BERT 风格 mask 训练当成主创新。  

其中，mask 机制与 Agent 方向都可以作为后续增强，但不应替代当前主线。

## 十二、分阶段工作包（建议执行顺序）

- **WP0：研究协议固化**  
- **WP1：高保真 benchmark 构建**  
- **WP2：low-fidelity synthetic universe 构建**  
- **WP3：subset selection 设计与验证**  
- **WP4：continued adaptation 与统一评测**  
- **WP5：分析与扩展**  

## 十三、最终收敛后的主线表述（可直接对外使用）

本研究围绕多螺栓法兰连接装配中的密封预测问题，构建统一高保真 benchmark 包与低保真 synthetic universe，系统研究现成 tabular foundation model 在工程小样本场景下的领域适配问题。具体而言，本研究不从零设计新的 foundation backbone，而是以 TabPFN/TabPFN-2.5 为基础，通过装配导向的 synthetic subset selection 与 continued adaptation，缓解低保真解析样本与高保真有限元样本之间的 domain gap，并在统一 benchmark 协议下与强 baseline 公平比较，从而回答 tabular foundation model 在装配任务中“为什么不够好、如何被修复、在什么条件下有效、又会在何处失效”这一组核心问题。

## 附：当前版本的关键执行原则

1. 一切实验围绕同一高保真 benchmark 协议展开；  
2. 低保真数据不是替代真值，而是可筛选、可组织、可适配的 synthetic universe；  
3. selection 单位优先用 subset，不用碎片化 sample；  
4. 创新中心放在 benchmark、selection、adaptation 与分析，而非硬造新 backbone；  
5. Agent 与 mask 模块属于后续增强，不得喧宾夺主。  

## 参考依据

- Real-TabPFN: Improving Tabular Foundation Models via Continued Pre-training With Real-World Data.  
- Engineering Regression Without Real-Data Training: Domain Adaptation for Tabular Foundation Models Using Multi-Dataset Embeddings.  
- 法兰装配_母参数输入输出表_初稿.md（用户提供）。
