# 多螺栓法兰连接密封预测的高配研究框架（EAAI导向版）

## 0. 文档定位

本文档用于把原有研究主线从“工程 AI pipeline”升级为“低高保真工程表格适配方法论”。目标不再是单纯完成一条从低保真数据到高保真预测的闭环，而是把闭环做成具备投稿 Engineering Applications of Artificial Intelligence（EAAI）这类工程 AI 期刊竞争力的研究框架。

本框架保持原有核心方向：多螺栓法兰连接装配中的最小垫片接触压力与密封安全裕量预测；使用 TabPFN/TabPFN-2.5 作为 tabular foundation model 基座；通过 low-fidelity synthetic universe、工程语义 subset selection 与 continued adaptation 缓解 synthetic-real domain gap。

本框架的高配要求是：研究成果必须证明一种可复用的低高保真工程表格适配方法，而不只是证明某个法兰案例能被某个模型预测。

---

## 1. 研究总目标

围绕多螺栓法兰连接装配密封预测任务，构建统一高保真 FEA benchmark 与低保真 synthetic universe，提出工程语义驱动的 synthetic subset selection 方法，并将其用于 TabPFN/TabPFN-2.5 的 continued adaptation。最终目标是在高保真样本稀缺条件下，提高模型对最小垫片接触压力、密封安全裕量和密封风险判定的预测精度、数据效率、稳健性和工程可解释性。

更高层次的研究问题是：

**在高保真工程表格数据稀缺、低保真解析样本丰富的场景下，怎样选择最有迁移价值的 synthetic subsets，并使 tabular foundation model 更可靠地适配目标工程域。**

---

## 2. 严厉现实判断

原始路线普通完成后，仍有明显投稿风险。原因如下：

1. TabPFN/TabPFN-2.5 是现成 backbone，底层模型创新有限。
2. 单一法兰构型容易被认为工程范围过窄。
3. 简单 scorer 容易被认为是启发式工程技巧。
4. 单一 target domain 无法证明方法稳健性。
5. 只报 RMSE/MAE 会削弱密封安全任务的工程价值。
6. benchmark 只以 csv 形式呈现，难以支撑期刊级贡献。

因此，高配路线必须从以下六个维度补强：

- 高保真 benchmark 规模；
- 多 target domain；
- 工程语义 scorer；
- TabPFN continued adaptation；
- 强 baseline 与系统消融；
- 工程安全指标与失败模式分析。

---

## 3. 论文级核心命题

论文最终应证明如下命题：

**低保真 synthetic data 直接全量使用并不总是有效；经过工程语义 subset selection 后的 synthetic subsets 能更稳定地帮助 TabPFN/TabPFN-2.5 适配小样本高保真 FEA 目标域，并在密封安全相关指标上带来更可靠的改进。**

这个命题包含三层含义：

第一，synthetic data 不是替代高保真真值，而是可组织、可筛选、可适配的低保真知识源。

第二，selection 的对象应是物理子域 subset，而不是孤立样本点。

第三，方法的价值必须通过真实 FEA target domain 上的精度、风险判定、数据效率和失败模式来证明。

---

## 4. 研究贡献重构

### 4.1 Benchmark 贡献

构建一个面向多螺栓法兰连接密封预测的高保真 FEA benchmark 包。该 benchmark 需要具备统一母场景、多子场景、多任务和固定评测协议。

benchmark 不应只是一个 csv 文件，而应包含：

- 母场景定义；
- FEA 建模协议；
- 输入变量字典；
- 输出标签定义；
- low/high-fidelity 共享字段；
- bridge semantic layer；
- train/val/test split；
- target domain 定义；
- 评价指标；
- 代表性 FEA 后处理图。

### 4.2 Synthetic universe 贡献

基于 VDI2230、PCC-1、工艺规则、简化力学模型和参数扫描，构建 low-fidelity synthetic universe。该 universe 需要具备明确单位、物理范围、公式来源、约束过滤和高低保真字段对齐。

synthetic universe 的定位是：

- 丰富源域；
- 适配预训练源；
- selection 候选池；
- 工程语义桥接空间；
- domain gap 分析对象。

### 4.3 方法贡献

提出 Engineering-Aware Synthetic Subset Selection（EASS）框架。该方法不直接选择单个样本，而是选择具有物理意义的 synthetic subsets。

EASS 至少包含：

1. 物理子域构造；
2. subset 统计表征；
3. 工程桥接特征表征；
4. target-domain similarity scoring；
5. top-k subset selection；
6. selected subset continued adaptation；
7. high-fidelity benchmark 统一评测。

### 4.4 Adaptation 贡献

以 TabPFN/TabPFN-2.5 为基础，验证 selected subsets 对 continued adaptation 的贡献。重点不是重造 backbone，而是证明工程语义 selection 能提升 tabular foundation model 在小样本高保真装配任务中的适配能力。

### 4.5 分析贡献

系统分析以下问题：

- 原始 TabPFN 为什么在装配任务上不够好；
- full synthetic adaptation 何时带来负迁移；
- 哪类 subset 具备高迁移价值；
- bridge features 对 selection 有多大贡献；
- method 在哪些 target domain 中失败；
- 失败是否能被工程变量解释。

---

## 5. 高配数据设计

### 5.1 高保真 FEA benchmark 规模

建议目标：

- FEA 样本数：300 条左右；
- 最低可战规模：200 条；
- 理想规模：400–600 条；
- 物理 subsets：8–12 个；
- high-fidelity target domains：至少 3 个，建议 5 个。

低于 100 条 FEA 时，benchmark 贡献不足，EAAI 风险很高。200 条左右进入可论证区间。300 条以上具备较明显说服力。

### 5.2 Low-fidelity synthetic universe 规模

建议目标：

- synthetic 样本数：5 万–10 万；
- 最低规模：1 万；
- 每个 subset 样本数充足；
- 所有变量保留单位；
- 所有派生变量记录公式来源；
- 不合理物理样本必须过滤。

### 5.3 Target domain 设计

建议至少构造 5 个真实 FEA target domains：

1. 高内压 + 低垫片刚度；
2. 高预紧散布；
3. 大偏心载荷；
4. 低 seal margin 临界区域；
5. 高摩擦不确定性或高载荷扰动。

每个 target domain 应拥有独立测试集。每个 target domain 需要包含 target-specific 结果、可视化和失败案例。

### 5.4 任务标签设计

主任务：

- `p_min_gasket` 回归；
- `seal_margin` 回归；
- `seal_pass` 分类。

辅助任务：

- `contact_uniformity_index`；
- `contact_area_ratio`；
- `flange_opening_max`；
- near-threshold safety risk。

### 5.5 Bridge semantic layer

桥接层是论文方法独特性的关键，不得弱化。建议包含：

- `FKerf`；
- `FKP`；
- `FKR`；
- `FM_min`；
- `FM_max`；
- `Phi`；
- `FSA`；
- `FPA`；
- `contact_uniformity_index`；
- `seal_margin_proxy`。

这些变量用于 low/high-fidelity 语义对齐、subset scoring、failure analysis 和 adaptation 前后解释。

---

## 6. EASS 方法框架

### 6.1 Physical subset construction

将 low-fidelity synthetic universe 划分为具有物理意义的 subsets。subset 构造变量应优先选择能体现 domain gap 的工程因素：

- 内压等级；
- 垫片等效刚度；
- 预紧散布；
- 摩擦系数不确定性；
- 偏心等级；
- 目标预紧力区间；
- 垫片厚度；
- 法兰厚度或等效刚度。

subset 不是分类标签，而是源域数据包。它的作用是组织 synthetic universe，并作为 selection 的基本单元。

### 6.2 Subset representation

每个 subset 需要转化为一个可比较的元表示。建议包括四类特征：

1. Raw input statistics  
   均值、标准差、分位数、协方差摘要。

2. Bridge semantic statistics  
   `FKerf`、`FKP`、`FKR`、`FM_min`、`FM_max`、`Phi` 等变量的统计摘要。

3. Task proxy statistics  
   low-fidelity 预测输出、seal margin proxy、失败风险比例。

4. Quality statistics  
   样本数、覆盖度、物理约束违反率、临界样本比例。

### 6.3 Engineering-aware scorer

推荐主 scorer：

```math
Score(S,T)=
-\alpha d_{raw}(S,T)
-\beta d_{bridge}(S,T)
-\gamma d_{task}(S,T)
+\lambda q(S)
```

其中：

- \(S\)：candidate synthetic subset；
- \(T\)：high-fidelity target domain；
- \(d_{raw}\)：原始输入分布距离；
- \(d_{bridge}\)：工程桥接语义距离；
- \(d_{task}\)：任务相关 proxy 距离；
- \(q(S)\)：subset 质量项；
- \(lpha,eta,\gamma,\lambda\)：通过 validation target domain 或小规模高保真验证集确定。

距离度量应至少比较以下方法：

- mean distance；
- Wasserstein distance；
- MMD；
- CORAL；
- energy distance；
- domain classifier distance；
- learned ranker score。

### 6.4 Top-k subset selection

根据 score 选择 top-k subsets 构造 adaptation source。需要系统比较不同 k：

- top-1；
- top-2；
- top-4；
- top-6；
- full synthetic；
- random-k。

选择结果需要报告 subset ID、物理语义、score 组成、与 target 的距离、下游效果。

### 6.5 Continued adaptation

以 TabPFN/TabPFN-2.5 checkpoint 为起点，使用 selected subsets 构造 adaptation tasks。随后回到统一 FEA benchmark 协议下评测。

核心对照：

- Original TabPFN；
- TabPFN + full synthetic adaptation；
- TabPFN + random subset adaptation；
- TabPFN + EASS-selected adaptation；
- TabPFN + EASS-selected adaptation + few-shot FEA tuning；
- TabPFN-2.5 同样设置。

---

## 7. 实验设计

### 7.1 实验一：原始 TabPFN 失效分析

目标：回答原始 TabPFN/TabPFN-2.5 在装配任务上为什么不够好。

分析内容：

- 小样本 FEA-only 性能；
- 不同 target domain 的误差；
- near-threshold 样本误判；
- high-pressure/high-scatter 工况下的失败；
- 与 XGBoost/LightGBM/RF 的差异。

输出图：

- FEA 样本量 vs RMSE 曲线；
- target domain 分组误差图；
- near-threshold confusion matrix；
- error vs physical variable 图。

### 7.2 实验二：synthetic universe 直接使用的利弊

目标：证明 full synthetic 不天然最优，random synthetic 存在负迁移。

对照：

- FEA-only；
- FEA + full synthetic；
- FEA + random subset；
- FEA + farthest subset；
- FEA + EASS-selected subset。

重点结果：

- full synthetic 在某些 target domain 中产生负迁移；
- random subset 波动大；
- selected subset 更稳定。

### 7.3 实验三：selection 方法对照

目标：证明 EASS 超过常规 domain similarity 方法。

对照：

- random；
- nearest centroid；
- mean distance；
- Wasserstein；
- MMD；
- CORAL；
- domain classifier；
- bridge-feature scorer；
- learned scorer；
- EASS。

报告指标：

- target RMSE；
- target MAE；
- seal pass F1；
- false-safe rate；
- rank correlation between score and target performance；
- cross-target robustness。

### 7.4 实验四：TabPFN continued adaptation 主实验

目标：验证 selected synthetic subsets 对 TabPFN/TabPFN-2.5 adaptation 的贡献。

对照：

- Original TabPFN；
- Full synthetic adaptation；
- Random subset adaptation；
- Farthest subset adaptation；
- EASS-selected adaptation；
- EASS-selected + few-shot FEA tuning。

重点图：

- main performance table；
- per-target domain bar plot；
- data efficiency curve；
- adaptation source size curve；
- selected vs random violin plot。

### 7.5 实验五：消融实验

必须包含：

- 去掉 bridge distance；
- 去掉 task proxy；
- 去掉 quality term；
- 只用 raw input；
- sample-level selection；
- subset-level selection；
- 不同 top-k；
- 不同 FEA 样本量；
- 不同 target domain。

目标：证明每个模块都有必要，尤其证明 bridge features 和 subset-level selection 的贡献。

### 7.6 实验六：工程安全与失败模式分析

目标：证明方法不仅降低平均误差，还降低工程风险。

指标：

- false-safe rate；
- false-fail rate；
- unsafe recall；
- near-threshold F1；
- worst 10% error；
- underprediction ratio；
- overprediction ratio；
- critical-domain MAE。

可视化：

- contact pressure contour；
- gasket path pressure curve；
- error heatmap over pressure/stiffness；
- false-safe case gallery；
- predicted vs true seal margin near threshold；
- failure mode decision tree。

---

## 8. Baseline 体系

### 8.1 传统模型

- Ridge；
- ElasticNet；
- Random Forest；
- XGBoost；
- LightGBM；
- CatBoost；
- MLP。

### 8.2 Tabular foundation model

- Original TabPFN；
- Original TabPFN-2.5；
- TabPFN + full synthetic adaptation；
- TabPFN + random subset adaptation；
- TabPFN + EASS adaptation；
- TabPFN + EASS + few-shot FEA tuning。

### 8.3 Selection baseline

- Random；
- Full synthetic；
- Farthest；
- Input-only nearest；
- MMD；
- Wasserstein；
- CORAL；
- Domain classifier；
- Bridge-only；
- Learned scorer；
- EASS。

---

## 9. 评价指标

### 9.1 回归指标

- RMSE；
- MAE；
- R²；
- MAPE；
- worst 10% MAE；
- target-domain averaged RMSE；
- cross-domain variance。

### 9.2 分类与风险指标

- Accuracy；
- Macro-F1；
- Recall for unsafe class；
- AUC；
- false-safe rate；
- false-fail rate；
- near-threshold F1；
- near-threshold recall。

### 9.3 数据效率指标

- performance vs FEA sample size；
- performance vs synthetic subset size；
- sample efficiency gain；
- adaptation efficiency ratio。

### 9.4 Selection 质量指标

- score-performance rank correlation；
- selected subset physical interpretability；
- selected subset diversity；
- cross-target stability；
- negative transfer avoidance。

---

## 10. 预期结果门槛

EAAI 可战版本需要达到以下结果门槛：

1. EASS-selected adaptation 在至少 3 个 target domains 中优于 random/full synthetic 的主要对照。
2. 相比 random subset，平均 RMSE/MAE 改善 10%–20%。
3. 相比 FEA-only，小样本阶段提升明显。
4. false-safe rate 有实质下降。
5. bridge feature 消融显示显著贡献。
6. subset-level selection 优于 sample-level selection。
7. TabPFN/TabPFN-2.5 adaptation 有稳定收益。
8. 多随机种子标准差可控。
9. 失败案例能够用工程变量解释。

达不到这些门槛，EAAI 竞争力不足。尤其缺少多 target domain、缺少强 selection baseline、缺少工程安全指标时，论文会被判为普通工程应用实验。

---

## 11. 最终论文结构建议

### Title

Engineering-aware Synthetic Subset Selection for Low-to-High Fidelity Tabular Foundation Model Adaptation in Bolted Flange Sealing Prediction

### Abstract 主线

- 高保真工程数据稀缺；
- 低保真 synthetic data 丰富但存在 domain gap；
- 提出 EASS；
- 结合 TabPFN/TabPFN-2.5 continued adaptation；
- 在多 target FEA benchmark 上验证；
- 显著提升精度、数据效率和密封风险判定。

### Section 1 Introduction

重点写：

- 工程高保真样本稀缺；
- 普通 synthetic augmentation 有负迁移；
- Tabular foundation model 需要领域适配；
- 本文提出工程语义 subset selection。

### Section 2 Related Work

包含：

- bolted flange sealing prediction；
- FEA surrogate modeling；
- tabular foundation models；
- synthetic data for engineering regression；
- domain adaptation / data selection；
- low-to-high fidelity modeling。

### Section 3 Benchmark

包含：

- mother scenario；
- FEA protocol；
- input/output dictionary；
- target domains；
- low-fidelity universe；
- bridge semantic layer；
- metrics。

### Section 4 Method

包含：

- subset construction；
- subset representation；
- EASS scorer；
- top-k selection；
- continued adaptation；
- computational workflow。

### Section 5 Experiments

包含：

- baselines；
- scorer comparisons；
- TabPFN adaptation；
- ablation；
- engineering safety metrics；
- failure cases。

### Section 6 Discussion

重点写：

- selected synthetic 的价值；
- negative transfer；
- 工程语义桥接层；
- 方法边界；
- 可迁移性。

### Section 7 Conclusion

强调：

- benchmark；
- low/high-fidelity adaptation；
- subset selection；
- TabPFN 修复；
- 工程安全预测。

---

## 12. 工作包重构

### WP0：研究协议固化

交付：

- 母场景定义；
- 输入输出字典；
- 单位规范；
- split 协议；
- target domain 定义；
- FEA 后处理协议。

### WP1：高保真 FEA benchmark

交付：

- 200–400 个 FEA case；
- 多 target domains；
- 接触压力云图；
- 标签提取脚本；
- benchmark split。

### WP2：Low-fidelity synthetic universe

交付：

- 1–10 万 synthetic 样本；
- 物理公式说明；
- bridge features；
- 约束过滤；
- subset 元信息。

### WP3：EASS scorer

交付：

- 多种距离；
- bridge scorer；
- learned scorer；
- score ranking；
- top-k selection；
- selection 可解释图。

### WP4：TabPFN adaptation

交付：

- original TabPFN；
- selected adaptation；
- random/full/farthest 对照；
- FEA few-shot tuning；
- 多 target domain 结果。

### WP5：系统分析

交付：

- 消融实验；
- 小样本曲线；
- 工程安全指标；
- 失败案例；
- negative transfer 分析。

### WP6：论文与复现包

交付：

- manuscript；
- data card；
- code；
- benchmark protocol；
- figures；
- supplement。

---

## 13. 风险与应对

### 风险一：FEA 数量不足

后果：benchmark 贡献不足。  
应对：减少几何自由度，增加 target domain 内部样本密度；优先保证 200+ FEA case。

### 风险二：EASS 提升不稳定

后果：方法贡献不足。  
应对：扩展 scorer，加入 bridge distance、learned ranker 和 validation-based weight selection。

### 风险三：TabPFN 没有明显优势

后果：foundation model 主线削弱。  
应对：保留 TabPFN 为主线之一，同时强调 EASS 对多模型的通用适配价值；对 XGBoost/LightGBM/RF 也报告 selected subset 增益。

### 风险四：full synthetic 表现最好

后果：selection 必要性受损。  
应对：分析 target domains 中的 negative transfer 与高 domain gap 场景；强调 selection 的数据效率、稳定性和工程安全指标优势。

### 风险五：工程审稿人质疑公式简化

后果：low-fidelity universe 可信度下降。  
应对：明确 low-fidelity 数据不是高保真真值，只是可筛选适配源；所有公式给出来源、单位和适用边界。

### 风险六：AI 审稿人质疑方法新颖性

后果：被判为应用堆料。  
应对：把核心贡献写成低高保真工程表格适配框架，并用多 scorer、消融、target-domain 泛化证明方法增量。

---

## 14. 投稿定位

### 主投方向

Engineering Applications of Artificial Intelligence

投稿定位：

**工程小样本高保真回归中的 tabular foundation model 领域适配方法。**

不是“法兰密封预测应用”，而是“以法兰密封预测为验证场景的低高保真工程表格适配”。

### 备选期刊

- Expert Systems with Applications；
- Knowledge-Based Systems；
- Neurocomputing；
- Advanced Engineering Informatics；
- Computers in Industry；
- Applied Soft Computing；
- Engineering with Computers。

### 不建议主投方向

- 纯机械结构设计期刊；
- 纯 AI 方法期刊；
- 只接受强理论贡献的机器学习期刊；
- 顶级 AI 会议。

---

## 15. 最终成果预测

### 普通完成版

成果：

- 一个 FEA benchmark；
- 一个 synthetic universe；
- 一个 scorer；
- 一个 TabPFN adaptation；
- 一组提升结果。

预测：

- EAAI 风险高；
- 更适合一般工程 AI/EI/SCI；
- 论文容易被评价为 pipeline 应用。

### 高配完成版

成果：

- 300 级 FEA benchmark；
- 5 个 target domains；
- 10 万级 synthetic universe；
- EASS scorer；
- 多 selection baseline；
- TabPFN/TabPFN-2.5 adaptation；
- 工程安全指标；
- 失败模式分析。

预测：

- EAAI 具备现实竞争力；
- 大修机会明显；
- 命中率约 40%–60%；
- 仍需要结果足够稳定。

### 强竞争版

成果：

- 400–600 FEA case；
- 多构型或多 target 扩展；
- 公开 benchmark 协议；
- EASS 在多个模型和 target domain 均有效；
- 显著降低 false-safe 风险；
- 适配收益稳定且可解释。

预测：

- EAAI 命中机会进一步提高；
- 同时具备转投 ESWA/KBS/Advanced Engineering Informatics 的竞争力。

---

## 16. 对外一句话版本

本研究面向高保真工程表格数据稀缺问题，以多螺栓法兰连接密封预测为验证场景，构建统一 FEA benchmark 与 low-fidelity synthetic universe，提出工程语义驱动的 subset-level selection 方法，并将 selected synthetic subsets 用于 TabPFN/TabPFN-2.5 continued adaptation，从而提升小样本高保真目标域上的预测精度、数据效率和密封风险判定可靠性。

---

## 17. 最终执行原则

1. 所有实验围绕真实 FEA target domain 展开。
2. synthetic data 只作为可筛选适配源，不作为真值替代。
3. subset 是物理子域，不是分类标签。
4. selection 需要超过常规 domain similarity 方法。
5. TabPFN adaptation 必须产生稳定收益。
6. 工程安全指标必须进入主结果。
7. 失败模式分析必须解释方法边界。
8. benchmark 必须作为“包”呈现。
9. 论文主线必须是 low-to-high fidelity tabular adaptation。
10. 低配执行不具备 EAAI 竞争力。
