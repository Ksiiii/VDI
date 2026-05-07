# 面向 EAAI 投稿的高配研究框架路线 V2.0

# Physics-Informed OT + Target-Conditioned Subset Value Learning for Tabular Foundation Model Adaptation in Bolted Flange Sealing Prediction

## 0. 版本定位

本文档是对原有“多螺栓法兰连接装配小样本任务的 Tabular Foundation Model 领域适配研究框架”的高配重构版。

原始框架已经明确：本研究围绕多螺栓法兰连接装配中的最小垫片接触压力 / 密封安全裕量预测，构建统一高保真 benchmark 包，并研究 TabPFN / TabPFN-2.5 在“高保真样本稀缺、低保真解析样本丰富”条件下的领域适配问题；研究定位也已经明确为“不是从零重造 backbone，而是做现成 tabular foundation model 的领域化适配”。

本版在原始框架上做三点重大升级：

1. 将 subset selection 从启发式距离打分升级为 **Physics-Informed Optimal Transport, PIOT**。
2. 将人工规则式 subset 权重升级为 **Target-Conditioned Subset Value Learning**。
3. 将物理因果拓扑作为 **feature grouping、context retrieval 和 failure analysis** 的辅助机制。

最终目标不是完成一个工程 AI pipeline，而是形成一套面向高保真工程小样本表格回归任务的低高保真适配方法论。

---

## 1. 严厉的研究定位

### 1.1 不能再这样定位

本研究不应再被表述为：

- 基于 TabPFN 的法兰密封预测；
- 用低保真数据增强高保真数据；
- 用一个打分器筛选 synthetic subsets；
- 将现成模型套到机械装配数据上。

这些表述过弱，容易被审稿人判为“工程应用 + 模型拼接”。

### 1.2 应当这样定位

本研究应定位为：

> 面向高保真工程表格回归数据稀缺问题，提出一种工程语义约束的 low-to-high fidelity synthetic subset selection 与 tabular foundation model adaptation 方法。该方法通过 Physics-Informed Optimal Transport 度量低保真子域与高保真目标域之间的可迁移性，并结合目标域反馈学习 subset value，从而提升 TabPFN / TabPFN-2.5 在多螺栓法兰密封预测任务上的数据效率、稳健性和工程安全性。

### 1.3 核心论文命题

本研究最终要证明的命题是：

> 在高保真 FEA 样本稀缺的工程表格回归任务中，低保真 synthetic 数据不能直接全量使用。经过工程桥接语义约束的 Physics-Informed OT selection 后，选出的低保真 subsets 能更有效地支撑 Tabular Foundation Model 的目标域适配，并降低 full synthetic 或 random synthetic 带来的负迁移风险。

---

## 2. 最终论文标题建议

### 2.1 主标题建议

**Physics-Informed Optimal Transport for Engineering-Aware Synthetic Subset Selection in Low-to-High Fidelity Tabular Foundation Model Adaptation**

### 2.2 工程场景副标题

**A Case Study on Bolted Flange Sealing Prediction**

### 2.3 完整标题备选

**Physics-Informed Optimal Transport for Low-to-High Fidelity Tabular Foundation Model Adaptation in Bolted Flange Sealing Prediction**

### 2.4 缩写建议

**PIOT-EASS**

全称：

**Physics-Informed Optimal Transport for Engineering-Aware Synthetic Subset Selection**

---

## 3. 研究总目标

本研究围绕多螺栓法兰连接装配中的密封预测任务，构建一个包含高保真 FEA benchmark、低保真 synthetic universe、工程桥接语义层和统一评测协议的研究平台。

在此基础上，提出 PIOT-EASS 方法：将低保真 synthetic universe 划分为具有物理意义的 subsets，并利用 Physics-Informed Optimal Transport 计算每个 source subset 与高保真 target domain 之间的迁移代价；再结合少量高保真验证反馈学习 target-conditioned subset value；最终将 selected subsets 用于 TabPFN / TabPFN-2.5 的 context construction、continued adaptation 或 few-shot high-fidelity tuning。

---

## 4. 核心研究问题

本研究必须回答以下六个问题：

1. 原始 TabPFN / TabPFN-2.5 在多螺栓法兰装配小样本密封预测任务上存在什么失效模式？
2. 如何构建一个真实、可复用、可公平比较的高保真 FEA benchmark 包？
3. 如何将 VDI2230、PCC-1、工艺规则和简化力学模型组织成具有物理意义的 low-fidelity synthetic universe？
4. 如何通过 Physics-Informed OT 评价 source subsets 与 high-fidelity target domains 之间的迁移价值？
5. 如何利用极少量 high-fidelity validation feedback 学习 target-conditioned subset weights？
6. selected subsets 是否能稳定提升 TabPFN / TabPFN-2.5 的数据效率、目标域精度和工程安全性？

---

## 5. 总体技术路线

整体路线由七层组成。

### Layer 0：研究协议固化

- 固定母场景。
- 固定输入输出字典。
- 固定单位体系。
- 固定高低保真共享字段。
- 固定 train / validation / test 协议。
- 固定主任务与辅助任务。

### Layer 1：高保真 FEA benchmark 包

构建同一母场景下的多子域高保真 benchmark。

应包含：

- 多个 high-fidelity target domains；
- 多个任务标签；
- 统一 FEA 后处理流程；
- 统一 split；
- 可复用数据字典；
- 代表性接触压力云图和失败样本分析。

### Layer 2：low-fidelity synthetic universe

基于 VDI2230、PCC-1、工艺规则、简化力学模型和参数扫描生成 1 万到 10 万量级的低保真 synthetic 样本。

synthetic universe 的定位不是替代真值，而是可筛选、可组织、可适配的数据源。

### Layer 3：工程桥接语义层

构建 high-fidelity 和 low-fidelity 之间的功能语义接口。

桥接变量包括：

- `F_Kerf`
- `F_KP`
- `F_KR`
- `F_M_min`
- `F_M_max`
- `Phi`
- `contact_uniformity_index`
- `seal_margin_proxy`
- `near_threshold_indicator`

桥接层是 PIOT-EASS 的核心，不可降级为普通输入特征。

### Layer 4：Physics-Informed OT subset selection

将每个 low-fidelity subset 看作一个 source distribution，将少量高保真 FEA 样本看作 target distribution。

通过物理正则化的 OT cost 计算 source-target migration cost，并选择 top-k source subsets。

### Layer 5：target-conditioned subset value learning

在 PIOT score 的基础上，引入少量 high-fidelity validation feedback，学习每个 source subset 对特定 target domain 的贡献权重。

该模块作为 PIOT 的增强模块，不作为第一阶段强依赖。

### Layer 6：Tabular Foundation Model adaptation

将 selected subsets 用于：

- TabPFN / TabPFN-2.5 baseline；
- context set construction；
- continued adaptation；
- selected synthetic + few-shot FEA tuning。

### Layer 7：统一评测、消融与失败模式分析

所有方法必须回到统一 high-fidelity benchmark 协议下评测。

评测不仅包括 RMSE / MAE，也必须包括工程安全指标。

---

## 6. 高保真 benchmark 设计

### 6.1 Benchmark 不是 csv

benchmark 必须是一个包，包括：

- 数据表；
- FEA 建模说明；
- 输入变量字典；
- 输出变量字典；
- low/high fidelity 对齐说明；
- split 协议；
- 任务定义；
- 评价指标；
- 代表性仿真云图；
- 后处理脚本或伪代码。

### 6.2 推荐规模

EAAI 导向的可战规模：

- 高保真 FEA：200–400 cases；
- low-fidelity synthetic：50,000–100,000 cases；
- physical subsets：8–12 个；
- high-fidelity target domains：3–5 个；
- 每个 target domain：40–80 个 FEA cases。

### 6.3 高保真 target domains

建议定义如下 target domains：

1. T1：高内压 + 低垫片刚度；
2. T2：高预紧散布；
3. T3：大偏心载荷；
4. T4：低 seal margin 临界区域；
5. T5：高摩擦不确定性区域。

这些 target domains 共同验证方法的泛化性。

### 6.4 主任务

主任务 1：


a. `p_min_gasket` 回归。

主任务 2：

b. `seal_margin` 回归。

主任务 3：

c. `seal_pass` 分类。

### 6.5 工程安全任务

必须额外评估：

- false-safe rate；
- unsafe recall；
- near-threshold accuracy；
- worst 10% error；
- under-prediction ratio；
- over-prediction ratio；
- critical-domain MAE。

密封预测的审稿重点不只是平均误差，安全边界附近的误判更关键。

---

## 7. Low-fidelity synthetic universe 设计

### 7.1 数据源

low-fidelity synthetic universe 来自：

- VDI2230；
- PCC-1；
- 预紧工艺规则；
- 简化法兰等效模型；
- 参数扫描；
- 工艺扰动模拟。

### 7.2 变量层级

变量分为五层：

1. L0：母场景固定参数；
2. L1：主设计变量；
3. L2：subset 定义变量；
4. L3：扰动变量；
5. L4：派生桥接变量。

### 7.3 不可接受的 synthetic 方式

以下方式不应作为论文级数据来源：

- 无物理依据的纯随机采样；
- 单纯均匀分布堆样本；
- 变量单位混乱；
- low/high fidelity 字段无法对齐；
- 无约束过滤；
- 无物理可行性检查。

### 7.4 synthetic universe 的论文角色

low-fidelity synthetic universe 的作用是：

- 提供丰富但带 domain gap 的源数据；
- 支撑 subset construction；
- 支撑 PIOT selection；
- 支撑 TabPFN adaptation；
- 暴露 full synthetic 负迁移问题。

---

## 8. Bridge Semantic Layer

### 8.1 设计原则

高低保真不能只在原始输入空间对齐。原始输入变量只描述几何、材料、载荷和工艺条件。真实工程功能更接近于桥接语义量。

桥接层的作用是把 low-fidelity 和 high-fidelity 放到同一套功能解释语言中。

### 8.2 桥接变量组

#### 夹紧力语义组

- `F_Kerf`
- `F_KP`
- `F_KR`
- `F_M_min`
- `F_M_max`

#### 载荷分配语义组

- `Phi`
- bolt-load redistribution proxy
- flange opening proxy

#### 密封风险语义组

- `p_min_gasket_proxy`
- `seal_margin_proxy`
- `near_threshold_ratio`
- `contact_uniformity_index`

#### 工艺扰动语义组

- preload scatter proxy
- friction uncertainty proxy
- eccentricity severity proxy

### 8.3 在 PIOT 中的作用

bridge features 进入 OT cost matrix：

\[
C_{ij}
=
\|x_i-x_j\|^2_{\Sigma_x^{-1}}
+
\lambda_b\|b_i-b_j\|^2_{\Sigma_b^{-1}}
+
\lambda_r\|r_i-r_j\|^2
+
\lambda_p R_{phys}(i,j)
\]

其中：

- \(x_i\)：原始输入特征；
- \(b_i\)：bridge semantic features；
- \(r_i\)：risk / task proxy features；
- \(R_{phys}\)：物理一致性惩罚项。

---

## 9. PIOT-EASS 方法设计

### 9.1 输入

- low-fidelity synthetic universe：\(\mathcal{D}_{LF}\)
- high-fidelity target domain：\(\mathcal{D}_{HF}^{T}\)
- subset collection：\(\mathcal{S}=\{S_1,S_2,\dots,S_K\}\)
- bridge semantic features：\(B\)
- target task labels：\(Y\)

### 9.2 Step 1：physical subset construction

将 synthetic universe 按工程变量组织为 subsets。

可使用：

- 内压等级；
- 垫片刚度等级；
- 预紧散布等级；
- 偏心等级；
- 摩擦不确定性等级；
- seal margin proxy 等级。

### 9.3 Step 2：multi-view subset representation

每个 subset 表示为：

\[
z_S=[z_{raw},z_{bridge},z_{task},z_{risk},z_{repr}]
\]

其中：

- \(z_{raw}\)：原始输入统计；
- \(z_{bridge}\)：桥接语义统计；
- \(z_{task}\)：任务 proxy 分布；
- \(z_{risk}\)：工程风险统计；
- \(z_{repr}\)：TabPFN / proxy encoder 表示。

### 9.4 Step 3：Physics-Informed OT scoring

对每个 subset \(S_k\) 与 target \(T\) 计算：

\[
OT_{PI}(S_k,T)
=
\min_{\pi\in\Pi(a,b)}
\langle \pi,C\rangle
+
\epsilon KL(\pi\|a\otimes b)
\]

Subset score 定义为：

\[
Score_{PIOT}(S_k,T)=-OT_{PI}(S_k,T)
\]

得分越高，subset 与 target 越接近，越适合作为 adaptation source。

### 9.5 Step 4：top-k subset selection

选择：

\[
\mathcal{S}^{*}_T=TopK_{S_k}\ Score_{PIOT}(S_k,T)
\]

### 9.6 Step 5：selected adaptation

将 \(\mathcal{S}^{*}_T\) 用于：

- TabPFN context set construction；
- TabPFN / TabPFN-2.5 continued adaptation；
- selected synthetic + few-shot FEA tuning。

---

## 10. Target-Conditioned Subset Value Learning

### 10.1 模块定位

该模块是 PIOT-EASS 的增强模块。它的目的不是替代 PIOT，而是利用少量 high-fidelity validation feedback 修正 PIOT score。

### 10.2 基本思想

每个 source subset 的价值不是固定的，而是相对于某个 target domain 的条件价值：

\[
V(S,T)
\]

同一个 subset 对不同 target domains 的价值不同。

### 10.3 输入

对每一组 \((S_i,T_j)\)，构造特征：

- PIOT distance；
- raw distance；
- bridge distance；
- task proxy distance；
- risk distance；
- subset size；
- physical violation ratio；
- representation distance。

### 10.4 监督信号

定义迁移收益：

\[
\Delta Perf(S_i,T_j)
=
Perf(Baseline,T_j)-Perf(Model(S_i),T_j)
\]

收益为正，表示该 subset 对 target 有帮助。

### 10.5 学习器

可用：

- XGBoost ranker；
- LightGBM ranker；
- RandomForest regressor；
- shallow MLP；
- small Set Transformer。

### 10.6 输出

得到 subset weight：

\[
w_i=g_\phi(S_i,T)
\]

最终 adaptation source：

\[
\mathcal{D}_{adapt}=\bigcup_i w_iS_i
\]

### 10.7 执行原则

第一阶段只做 PIOT score。第二阶段再加入 value learner。

不建议一开始直接做 meta-gradient through TabPFN。直接对 TabPFN 做双层优化，计算成本高，调试风险大，容易过拟合少量 FEA validation set。

---

## 11. Causal Topology-Guided 辅助机制

### 11.1 模块定位

因果图不作为主贡献，不宣称完成严格因果识别。

它的作用是：

- 指导变量分组；
- 指导 bridge layer 构造；
- 指导 context retrieval；
- 辅助 failure mode 分析。

### 11.2 物理拓扑

建议拓扑：

\[
\text{Geometry / Material / Process / Load}
\rightarrow
\text{Clamp Load / Force Redistribution}
\rightarrow
\text{Flange Opening / Contact State}
\rightarrow
\text{Gasket Contact Pressure}
\rightarrow
\text{Seal Margin / Seal Pass}
\]

### 11.3 用途 1：feature grouping

将特征分为：

- root variables；
- bridge variables；
- contact-state variables；
- risk / task variables。

### 11.4 用途 2：context retrieval

TabPFN context 不只按全特征欧氏距离选择，还按输出父节点变量检索。

Context score：

\[
R(c,t)
=
-\omega_1d_{parents}(c,t)
-\omega_2d_{bridge}(c,t)
-\omega_3d_{risk}(c,t)
\]

### 11.5 用途 3：failure analysis

失败样本按因果层级分析：

- root input mismatch；
- bridge feature mismatch；
- contact state mismatch；
- seal margin near-threshold mismatch。

---

## 12. TabPFN / TabPFN-2.5 Baseline 与 Adaptation

### 12.1 第一阶段：部署 baseline harness

先完成：

- TabPFN-2.5 环境；
- Ridge / RF / XGBoost / LightGBM / MLP；
- 统一数据读取；
- 统一 split；
- 统一指标；
- 统一预测文件；
- 小样本曲线；
- selection 接口。

### 12.2 第二阶段：TabPFN context baseline

比较：

- random context；
- nearest context；
- PIOT-selected context；
- causal-topology guided context。

### 12.3 第三阶段：continued adaptation

比较：

- original TabPFN；
- TabPFN + full synthetic adaptation；
- TabPFN + random subset adaptation；
- TabPFN + vanilla OT selected adaptation；
- TabPFN + PIOT-EASS selected adaptation；
- TabPFN + PIOT-EASS + few-shot FEA tuning。

### 12.4 第四阶段：TabPFN-2.5 扩展

同样协议迁移到 TabPFN-2.5。

重点不是“TabPFN-2.5 绝对分数最高”，而是证明 PIOT-EASS 对 tabular foundation model adaptation 有稳定增益。

---

## 13. Baseline 设计

### 13.1 传统模型 baseline

必须包含：

- Ridge / ElasticNet；
- Random Forest；
- XGBoost；
- LightGBM；
- CatBoost；
- MLP；
- FT-Transformer 或 TabTransformer。

### 13.2 Tabular foundation model baseline

必须包含：

- Original TabPFN；
- Original TabPFN-2.5；
- TabPFN + full synthetic；
- TabPFN + random subsets；
- TabPFN + selected subsets；
- TabPFN + selected subsets + FEA tuning。

### 13.3 Selection baseline

必须包含：

- Random；
- Full synthetic；
- nearest centroid；
- mean distance；
- Wasserstein；
- MMD；
- CORAL；
- vanilla OT；
- bridge distance；
- PIOT-EASS；
- PIOT-EASS + value learner。

只和 random 比不够。

---

## 14. 评价指标

### 14.1 回归指标

- MAE；
- RMSE；
- R²；
- MAPE；
- worst 10% MAE；
- near-threshold MAE。

### 14.2 分类指标

- Accuracy；
- Macro-F1；
- unsafe recall；
- safe recall；
- AUC。

### 14.3 工程安全指标

- false-safe rate；
- false-fail rate；
- under-prediction ratio；
- over-prediction ratio；
- critical-domain recall；
- seal-margin sign accuracy。

### 14.4 selection 指标

- selected subset overlap；
- top-k stability；
- target-domain distance reduction；
- negative transfer rate；
- adaptation gain。

---

## 15. 主实验设计

### Experiment 1：Benchmark Validity

目的：证明高保真 benchmark 有可学习信号。

比较：

- Ridge；
- RF；
- XGBoost；
- LightGBM；
- MLP；
- TabPFN；
- TabPFN-2.5。

输出：

- 主任务表；
- 小样本曲线；
- 误差分布；
- 代表性 FEA case。

### Experiment 2：Original TabPFN Failure Analysis

目的：回答原始 TabPFN 在装配小样本任务上为什么不够好。

分析：

- high-pressure target；
- low-stiffness target；
- near-threshold target；
- high scatter target；
- OOD target。

### Experiment 3：Synthetic Data Usefulness and Negative Transfer

目的：证明 full synthetic 不总是可靠。

比较：

- FEA-only；
- FEA + full synthetic；
- FEA + random synthetic subsets；
- FEA + selected synthetic subsets。

### Experiment 4：PIOT-EASS Main Result

目的：证明 PIOT-EASS selection 优于常规 selection。

比较：

- random；
- MMD；
- Wasserstein；
- CORAL；
- vanilla OT；
- bridge distance；
- PIOT-EASS。

### Experiment 5：Tabular Foundation Model Adaptation

目的：证明 selected subsets 对 TabPFN / TabPFN-2.5 adaptation 有帮助。

比较：

- Original TabPFN；
- Full synthetic adaptation；
- Random subset adaptation；
- Vanilla OT subset adaptation；
- PIOT-EASS subset adaptation；
- PIOT-EASS + FEA tuning。

### Experiment 6：Ablation Study

消融：

- raw-only；
- bridge-only；
- risk-only；
- raw + bridge；
- raw + bridge + risk；
- no OT；
- vanilla OT；
- PIOT；
- PIOT + value learner；
- sample-level selection；
- subset-level selection。

### Experiment 7：Engineering Safety and Failure Modes

分析：

- false-safe cases；
- near-threshold cases；
- high-pressure failure；
- high-scatter failure；
- bridge mismatch failure；
- selected subset negative cases。

---

## 16. 预期结果标准

### 16.1 最低可投稿标准

- PIOT-EASS 平均优于 random selection；
- PIOT-EASS 至少优于一种常规分布距离方法；
- selected adaptation 优于 original TabPFN；
- 至少 3 个 target domains 上趋势一致；
- 有完整消融。

该水平只能算可投稿，不稳。

### 16.2 EAAI 可战标准

- 300 条左右 FEA；
- 5 万条以上 synthetic；
- 5 个 target domains；
- PIOT-EASS 在大多数 target domains 上优于 MMD / Wasserstein / vanilla OT；
- selected adaptation 相比 random subset 平均 RMSE 下降 10%–20%；
- false-safe rate 明显下降；
- bridge feature 消融显示稳定贡献；
- TabPFN 和 TabPFN-2.5 上趋势一致。

### 16.3 强竞争标准

- 400 条以上 FEA；
- 10 万 synthetic；
- 多目标域、多随机种子、多 split；
- PIOT-EASS + value learner 在多数指标上第一；
- 工程安全指标改善明显；
- 负迁移分析清楚；
- benchmark 协议可复用。

---

## 17. 分阶段工作包

### WP0：研究协议固化

任务：

- 固定母场景；
- 固定输入输出字典；
- 固定单位；
- 固定任务标签；
- 固定 split 规则；
- 固定评价指标。

产出：

- `benchmark_protocol.md`
- `data_dictionary.xlsx`
- `task_config.yaml`

### WP1：TabPFN-2.5 baseline harness

任务：

- 部署 TabPFN-2.5；
- 跑通传统 baseline；
- 跑通回归和分类任务；
- 输出统一结果表；
- 预留 selection 接口。

产出：

- `src/run_baseline.py`
- `src/baseline_tabpfn25.py`
- `results/baseline_summary.csv`

### WP2：High-fidelity FEA benchmark

任务：

- 生成 200–400 条 FEA；
- 定义 3–5 个 target domains；
- 提取主标签和安全指标；
- 生成代表性云图。

产出：

- `fea_benchmark.csv`
- `target_domains.json`
- `fea_case_gallery/`

### WP3：Low-fidelity synthetic universe

任务：

- 生成 50,000–100,000 条 low-fidelity 样本；
- 计算 bridge features；
- 做物理约束过滤；
- 构造 8–12 个 subsets。

产出：

- `synthetic_universe.csv`
- `subset_table.csv`
- `bridge_feature_table.csv`

### WP4：PIOT-EASS selection

任务：

- 实现 vanilla OT；
- 实现 PIOT cost matrix；
- 实现 top-k subset selection；
- 与 MMD / Wasserstein / CORAL 对比。

产出：

- `src/piot_scorer.py`
- `selection_results.csv`
- `piot_ablation.csv`

### WP5：TabPFN adaptation

任务：

- original TabPFN baseline；
- full synthetic adaptation；
- random subset adaptation；
- PIOT-EASS selected adaptation；
- few-shot FEA tuning。

产出：

- `adaptation_results.csv`
- `sample_efficiency_curves.csv`

### WP6：Value learner and causal auxiliary

任务：

- target-conditioned subset value learning；
- causal topology-guided context retrieval；
- bridge ablation；
- failure mode analysis。

产出：

- `value_learner_results.csv`
- `causal_context_ablation.csv`
- `failure_case_report.md`

### WP7：论文整理

任务：

- 整理方法；
- 整理主实验；
- 整理消融；
- 整理工程分析；
- 准备 EAAI 投稿稿。

产出：

- `paper_main.tex`
- `supplementary.pdf`
- `reproducibility_package.zip`

---

## 18. 论文贡献写法

最终论文贡献建议写成：

1. 提出一个多目标域高保真 FEA benchmark，用于多螺栓法兰连接密封预测中的小样本表格回归研究。
2. 构建一个由 VDI2230、PCC-1、工艺规则和简化模型驱动的 low-fidelity synthetic universe，并将其组织为具有工程语义的 subsets。
3. 提出 PIOT-EASS 方法，在 OT cost 中引入 bridge semantic layer 和 physics-consistency penalty，实现工程语义约束的 synthetic subset selection。
4. 提出 target-conditioned subset value refinement，利用少量 high-fidelity validation feedback 学习 source subset 对目标域的迁移价值。
5. 将 selected subsets 用于 TabPFN / TabPFN-2.5 的 context construction 与 continued adaptation，并在精度、数据效率、工程安全指标和失败模式上进行系统验证。

---

## 19. 风险与应对

### 风险 1：FEA 样本不足

应对：

- 优先保证多个 target domains；
- 小样本曲线必须做；
- 强化数据效率叙事。

### 风险 2：PIOT 提升不明显

应对：

- 做 bridge ablation；
- 做 target-specific 分析；
- 加入 value learner；
- 分析 full synthetic 负迁移。

### 风险 3：TabPFN 表现弱

应对：

- 使用 TabPFN-2.5；
- 加入 context retrieval；
- 与 XGBoost / LightGBM 并列分析；
- 将贡献聚焦到 selection/adaptation，不押宝单一 backbone。

### 风险 4：因果图显得虚

应对：

- 不宣称严格因果识别；
- 只作为 feature grouping 和 context retrieval；
- 用消融证明 causal grouping 有帮助。

### 风险 5：EAAI 认为方法创新不足

应对：

- PIOT-EASS 作为主方法；
- 与 MMD、Wasserstein、vanilla OT、CORAL 对比；
- target-conditioned value learner 作为增强；
- 展示工程安全指标改善。

---

## 20. 当前阶段立即执行清单

### 第一周

- 部署 TabPFN-2.5；
- 建立 baseline harness；
- 跑通 synthetic / FEA 通用接口；
- 固定结果表格式。

### 第二周

- 固化 benchmark protocol；
- 固化数据字典；
- 设计 high-fidelity target domains；
- 写 FEA 输出字段规范。

### 第三周

- 重构 synthetic universe 生成规则；
- 计算 bridge semantic features；
- 构造 physical subsets。

### 第四周

- 实现 vanilla OT；
- 实现 PIOT cost matrix；
- 与 mean distance / MMD / Wasserstein 对比。

### 第五周

- 接入 TabPFN baseline；
- 接入 selected subsets；
- 做第一版 selected adaptation / context selection 实验。

### 第六周

- 设计 target-conditioned value learner；
- 做 value refinement；
- 做 bridge ablation。

---

## 21. 最终收敛表述

本研究围绕多螺栓法兰连接装配中的密封预测问题，构建一个多目标域高保真 FEA benchmark 和一个由标准、规则与简化模型驱动的 low-fidelity synthetic universe。针对低保真解析样本与高保真 FEA 样本之间的 domain gap，本文提出 PIOT-EASS：一种工程语义约束的 Physics-Informed Optimal Transport synthetic subset selection 方法。该方法通过将原始输入特征、bridge semantic layer、任务风险特征和物理一致性惩罚共同纳入 OT cost matrix，筛选出对特定高保真目标域更具迁移价值的 source subsets。进一步地，本文利用少量 high-fidelity validation feedback 学习 target-conditioned subset value，并将 selected subsets 用于 TabPFN / TabPFN-2.5 的 context construction 与 continued adaptation。最终，在统一高保真 benchmark 协议下，本文系统比较传统机器学习模型、原始 tabular foundation model、full synthetic adaptation、random subset adaptation、vanilla OT selection 和 PIOT-EASS selection，验证工程语义驱动的 low-to-high fidelity subset selection 对精度、数据效率、稳健性和工程安全性的影响。

---

## 22. 最终判断

这条路线按低配执行，仍然会停留在普通工程 AI pipeline。

这条路线按本版执行，才具备 EAAI 级别投稿竞争力。

决定成败的不是 TabPFN 本身，而是：

1. benchmark 是否成包；
2. synthetic universe 是否物理可信；
3. bridge semantic layer 是否进入方法核心；
4. PIOT-EASS 是否超过常规 domain similarity 方法；
5. selected adaptation 是否在多个 high-fidelity target domains 上稳定有效；
6. 工程安全指标和失败模式是否分析充分。

研究主线从现在开始固定为：

> **高保真工程表格回归中的 Physics-Informed OT synthetic subset selection 与 Tabular Foundation Model 领域适配。**

