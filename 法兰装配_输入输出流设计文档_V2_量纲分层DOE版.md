# 多螺栓法兰连接装配任务：输入/输出流设计文档 V2（量纲统一 + 主变量收缩 + 变量分层 + DOE 控制版）

## 1. 文档目的

本版文档用于解决此前输入/输出流设计中的两个核心问题：

1. **量纲未统一**：不同来源的数据在长度、力、压力、模量、比例量上混用，后续会影响 FEA 建模、VDI 生成、数据拼接、分布对齐与模型训练。
2. **变量过多导致样本量爆炸**：若所有连续/离散变量同时放开并做全组合扫描，FEA 计算成本无法承受，也不利于 benchmark 的可控性与论文叙事。

因此，V2 的核心原则不是“把所有可能变量都放进来”，而是：

- 先固定母场景；
- 再收缩主变量；
- 再按层管理变量；
- 最后用分层 DOE 而不是全因子穷举来生成样本。

---

## 2. V2 的总体思想

V2 将原先的“共享输入层 + 主输出层 + 桥接语义层 + FEA 解释层”保留，但新增两条硬约束：

### 2.1 量纲纪律（Dimensional Discipline）
所有变量必须同时具备：
- **物理单位**（用于仿真、VDI 计算、工程解释）；
- **统一存储单位**（用于表格落盘与跨来源对齐）；
- **建模辅助归一化形式**（用于跨场景比较、DOE 设计与模型输入稳定化）。

### 2.2 变量层级纪律（Variable Hierarchy Discipline）
所有变量必须被分到以下五层之一：
- **L0 固定母场景常量层**：第一版 benchmark 固定不动；
- **L1 主设计变量层**：真正允许进入 FEA DOE 主采样；
- **L2 子集定义变量层**：用于定义 synthetic subset / FEA 子场景；
- **L3 扰动/误差变量层**：用于鲁棒性与装配偏差分析，第一版只少量开放；
- **L4 派生/桥接/解释层**：由前面变量计算得到，不直接作为 DOE 自由变量。

这意味着：**不是所有共享变量都应被同时当作“自由输入变量”去扫。**

---

## 3. 统一量纲规范

## 3.1 原则

建议第一版采用“工程常用单位统一存储”，而不是完全 SI 基本单位落盘：

- 长度：`mm`
- 面积：`mm^2`
- 力：`N`（若展示方便可同时给 `kN`）
- 压力 / 应力 / 模量：`MPa`
- 温度差：`°C`
- 摩擦系数、比例、系数：`dimensionless`
- 分类变量：字符串或整数编码

这样做的原因是：
1. 与机械设计/FEA 前后处理习惯一致；
2. 避免 `Pa` 与 `MPa` 混用带来 10^6 级错误；
3. 便于直接与 VDI 和图纸参数沟通。

## 3.2 数据表中的三种字段

每个关键变量建议在数据字典中明确三列：

- `unit_raw`：工程物理单位
- `unit_storage`：表格实际存储单位
- `model_form`：模型使用形式（raw / normalized / derived）

例如：

| variable | unit_raw | unit_storage | model_form | 备注 |
|---|---|---|---|---|
| `flange_thickness` | mm | mm | raw + normalized | 原始几何量 |
| `target_preload_per_bolt` | N | N | raw + normalized | 建议附加预紧利用率 |
| `internal_pressure` | MPa | MPa | raw | 不要混成 Pa |
| `preload_scatter_ratio` | – | – | raw | 无量纲 |
| `seal_margin` | MPa | MPa | target | 主标签 |

## 3.3 建议额外保留的归一化特征

为了跨子场景比较，建议在原始物理量之外，额外生成一组**辅助无量纲特征**，但它们是“派生特征”，不是必须的 DOE 原变量。

建议优先保留：

- `flange_thickness_ratio = flange_thickness / bolt_nominal_diameter`
- `gasket_thickness_ratio = gasket_thickness / bolt_nominal_diameter`
- `bolt_circle_ratio = bolt_circle_diameter / bolt_nominal_diameter`
- `eccentricity_ratio = load_eccentricity_a / bolt_circle_diameter`
- `preload_utilization_ratio = target_preload_per_bolt / F_proof_per_bolt`
- `pressure_to_seal_ratio = internal_pressure / p_req_seal`（仅分析用，不建议作为训练输入主特征）

原则是：
- **原始量保留真实工程含义**；
- **比值量帮助跨场景对齐和 selection 分析**；
- **输出标签仍以物理量为准**，例如 `MPa`。

---

## 4. 变量分层：哪些变量该固定，哪些变量该开放

## 4.1 L0 固定母场景常量层（第一版 benchmark 固定）

这层变量不进入第一版 FEA 主 DOE。它们定义的是“同一母场景”的背景，使 benchmark 不至于发散成一个过宽的问题。

建议 V1 固定：

| 变量名 | 单位 | 建议处理 | 原因 |
|---|---:|---|---|
| `bolt_nominal_diameter` | mm | 固定 | 避免尺寸体系同时变化 |
| `bolt_strength_class` | – | 固定 | 避免强度等级与预紧水平耦合爆炸 |
| `E_bolt` | MPa | 固定 | 若螺栓材料不变，无需开放 |
| `E_flange` | MPa | 固定 | 第一版先固定法兰材料 |
| `flange_effective_width` | mm | 由几何导出/固定 | 避免几何自由度过多 |
| `gasket_effective_width` | mm | 固定或由构型导出 | 第一版先锁定密封带宽 |
| `clamping_eccentricity_s_sym` | mm | 固定 | 先不单独开放夹紧偏心 |
| `temperature_delta` | °C | 固定为 0 或单一工况 | 热-力耦合留到第二阶段 |

## 4.2 L1 主设计变量层（进入 FEA DOE 主采样）

这层变量是你第一版最值得花 FEA 成本去扫的变量。建议控制在 **5–7 个**，不要超过 8 个。

### 推荐的 V1 主变量

| 变量名 | 单位 | 类型 | 推荐范围/等级 | 推荐理由 |
|---|---:|---|---|---|
| `flange_thickness` | mm | 连续 | 3–5 个代表水平或连续区间 | 法兰刚度主控量 |
| `gasket_thickness` | mm | 连续 | 3–4 个代表水平或连续区间 | 影响接触压缩与密封 |
| `E_gasket_eq` | MPa | 连续/分级 | 3 个材料等级或区间 | 垫片等效刚度核心量 |
| `target_preload_per_bolt` | N | 连续 | 依据允许预紧区间设置 | 最关键装配控制量 |
| `internal_pressure` | MPa | 连续 | 依据工况区间设置 | 密封任务核心载荷 |
| `external_axial_load_eq` | N | 连续 | 若母场景存在该工况则开放 | 影响残余夹紧力 |

备注：
- 若你希望第一版更聚焦“内压密封”，可暂时**不开放** `external_axial_load_eq`，将主变量降为 5 个。
- 若你暂时无法稳定定义 `E_gasket_eq` 的连续取值，可先把它作为 3 级离散材料等级。

## 4.3 L2 子集定义变量层（subset key，不做高密度连续扫描）

这层变量主要用于定义“物理有意义的子集”，支持你后续的 subset-level selection。它们更像“域标签”而不是高密度连续自由变量。

### 推荐的 V1 subset 变量

| 变量名 | 单位 | 类型 | 推荐水平 | 作用 |
|---|---:|---|---|---|
| `bolt_num` | – | 离散 | 2–3 个水平 | 定义不同螺栓布局子集 |
| `preload_scatter_ratio` | – | 离散分级 | 0 / 低 / 高 | 定义装配质量子集 |
| `load_eccentricity_a` 或 `eccentricity_ratio` | mm 或 – | 离散分级 | 0 / 中 / 高 | 定义偏心工况子集 |
| `gasket_family`（可新增标签） | – | 离散 | 2–3 类 | 区分垫片家族 |

建议把这层变量用于：
- 划分 subsets；
- 做 selection；
- 做 benchmark 子场景拆分；
- 做 OOD 分析。

**不要在第一版里同时把 L2 全部再做细粒度连续扫描。**

## 4.4 L3 扰动/误差变量层（少量开放）

这层变量主要代表装配误差、摩擦波动、局部偏差等。第一版只建议作为**弱扰动**引入，不要和主变量同权展开。

| 变量名 | 单位 | 第一版建议 | 备注 |
|---|---:|---|---|
| `mu_thread` | – | 固定或 2 级扰动 | 先不要连续大范围扫 |
| `mu_bearing` | – | 固定或 2 级扰动 | 同上 |
| 局部预紧随机分配模式 | – | 作为重复仿真种子 | 不单独当作主 DOE 维度 |
| 接触参数细微变化 | – | 留给第二阶段 | 否则 FEA 成本暴涨 |

## 4.5 L4 派生/桥接/解释层（不做自由输入）

这层变量来自 VDI、规则或 FEA 后处理，主要用于跨保真对齐、selection 和解释。

建议继续保留：

- `FKP`
- `FKerf`
- `Phi`
- `FSA`
- `FPA`
- `FKR`
- `FM_min`
- `FM_max`
- `contact_uniformity_index`

这些变量的定位是：
- bridge / analysis / explanation；
- 可以做 selection 打分特征；
- 不建议作为第一版 FEA DOE 自由维度。

---

## 5. 新版输入流设计（推荐版）

## 5.1 输入流总体结构

### A. 母场景固定参数
定义同一 benchmark 包的公共背景：
- 法兰基型
- 螺栓规格与强度等级
- 材料体系
- 密封面基准结构
- 基准接触设置

### B. 子集定义参数（subset-level）
定义“这是哪个物理子域”：
- `bolt_num`
- `preload_scatter_ratio_level`
- `eccentricity_level`
- `gasket_family`

### C. 主 DOE 参数（sample-level within subset）
在每个 subset 内做连续/半连续采样：
- `flange_thickness`
- `gasket_thickness`
- `E_gasket_eq`
- `target_preload_per_bolt`
- `internal_pressure`
- `external_axial_load_eq`（可选）

### D. 扰动参数
以低密度或重复试验方式加入：
- `mu_thread`
- `mu_bearing`
- preload realization seed

### E. 派生输入特征
由前述变量计算：
- thickness ratio
- eccentricity ratio
- preload utilization ratio
- 其他 bridge features

---

## 6. 新版输出流设计（推荐版）

## 6.1 主任务输出层（对外 benchmark 标签）

| 输出名 | 单位 | 来源 | 角色 |
|---|---:|---|---|
| `p_min_gasket` | MPa | FEA 主后处理 / 低保真映射 | 主回归标签 |
| `p_req_seal` | MPa | 规则 / VDI / 需求定义 | 阈值量 |
| `seal_margin = p_min_gasket - p_req_seal` | MPa | 派生 | **主标签优先推荐** |
| `seal_pass` | 0/1 | 派生 | 工程判定标签 |

说明：
- 第一篇论文建议把 **`seal_margin` 作为主回归标签**；
- `p_min_gasket` 作为原始物理标签同步报告；
- `seal_pass` 用于补充分类评价；
- `p_req_seal` 必须显式记录，不能只隐含在文字里。

## 6.2 辅助解释输出层

| 输出名 | 单位 | 作用 |
|---|---:|---|
| `contact_uniformity_index` | – | 解释为什么最小接触压力下降 |
| `opening_displacement_max` | mm | 辅助解释法兰张口 |
| `bolt_load_imbalance_index` | – | 解释螺栓受力不均 |
| `residual_clamping_force_eq` | N | 辅助解释密封失效前兆 |

## 6.3 低高保真桥接输出层

| 输出名 | 单位 | 角色 |
|---|---:|---|
| `FKP` | N | 密封功能所需最小夹紧力 |
| `FKerf` | N | 满足功能要求所需最小夹紧力 |
| `Phi` | – | 载荷分配系数 |
| `FKR` | N | 工作状态残余夹紧力 |
| `FM_min` | N | 设计最小装配预紧力 |
| `FM_max` | N | 设计最大装配预紧力 |

---

## 7. DOE：如何避免样本量爆炸

## 7.1 不要用全因子穷举

假设你有：
- 4 个离散变量，每个 3 个水平；
- 6 个连续变量，每个只取 5 个水平；

那么全因子样本量约为：

`3^4 × 5^6 = 81 × 15625 = 1,265,625`

这对 FEA 完全不可承受。

所以必须改成：

**“子集离散分层 + 子集内连续 DOE + 自适应补样”**。

## 7.2 推荐的三阶段 DOE 路线

### 阶段 0：低保真快速筛选（cheap screening）
先在 VDI / 低保真解析侧做大范围便宜扫描，用于判断哪些变量真正敏感。

建议做法：
- 单因素扫描（One-at-a-time）或 Morris screening；
- 记录对 `seal_margin`、`FKR`、`Phi` 的敏感性排序；
- 最终只保留前 5–7 个高敏主变量进入 FEA 主 DOE。

### 阶段 1：子集层离散设计（subset-level design）
先定义有限个物理子集，而不是一开始在全空间乱采。

一个可执行示例：
- `bolt_num`: 2 个水平
- `preload_scatter_ratio_level`: 2 个水平
- `eccentricity_level`: 2 个水平
- `gasket_family`: 2 个水平

这样先得到 `2×2×2×2 = 16` 个理论子集。

然后不要全保留，可以根据工程意义和 low-fidelity 预分析，先选 **8–12 个最有代表性的子集**。

### 阶段 2：子集内连续 DOE（sample-level within subset）
在每个子集内部，对 L1 主变量做连续采样。

推荐方法：
- **Maximin Latin Hypercube Sampling (LHS)**：最实用；
- 若连续+离散混杂严重，可用 **D-optimal / I-optimal**；
- 若第一版只想简单稳妥，优先用 **分层离散 + 子集内 LHS**。

#### 推荐样本规模

对于每个 subset：
- 主变量 5 个时：先取 **15–25 个样本**；
- 主变量 6 个时：先取 **20–30 个样本**；
- 总体高保真 FEA：控制在 **160–360 个样本** 较现实。

示例：
- 8 个 subset × 20 样本 = 160 个 FEA 样本
- 12 个 subset × 25 样本 = 300 个 FEA 样本

这已经足够支撑：
- benchmark 初版；
- baseline；
- selection 前分析；
- 小样本适配验证。

## 7.3 自适应补样（第二轮）

第一轮 DOE 跑完后，不要立刻继续均匀加样，而要做**有目的地补样**。

补样优先区域：
- `seal_margin ≈ 0` 的决策边界附近；
- surrogate 误差最大的区域；
- bridge 特征与高保真偏差最大的区域；
- 接触均匀性突变、法兰张口突变的区域。

这一步可以显著降低你需要的总 FEA 数量。

---

## 8. V1 最小可执行方案（强烈推荐）

如果你现在就要真正开干，而不是继续扩表，我建议直接采用下面这套 V1：

## 8.1 固定项
- `bolt_nominal_diameter`
- `bolt_strength_class`
- `E_bolt`
- `E_flange`
- `flange_effective_width`
- `gasket_effective_width`
- `temperature_delta = 0`
- 接触算法和网格基准规则固定

## 8.2 subset 变量
- `bolt_num`: 2 水平
- `preload_scatter_ratio`: 2 水平
- `eccentricity_level`: 2 水平

共 `2×2×2 = 8` 个 subset。

## 8.3 主 DOE 变量
- `flange_thickness`
- `gasket_thickness`
- `E_gasket_eq`
- `target_preload_per_bolt`
- `internal_pressure`

每个 subset 内做 20 个 LHS 点。

则高保真样本数约为：

`8 × 20 = 160`

这是一个非常适合你当前阶段的数量级。

## 8.4 标签输出
主输出：
- `p_min_gasket`
- `p_req_seal`
- `seal_margin`
- `seal_pass`

桥接输出：
- `FKP`
- `FKerf`
- `Phi`
- `FKR`

解释输出：
- `contact_uniformity_index`
- `opening_displacement_max`

---

## 9. 建议的数据表结构

建议最终不要只有一个 csv，而是至少维护以下 4 张表：

### 9.1 `case_definition.csv`
记录每个样本所属母场景、subset、DOE 批次、随机种子。

### 9.2 `input_raw.csv`
记录原始物理输入，带单位约定。

### 9.3 `input_derived.csv`
记录归一化特征、桥接前特征、分析辅助特征。

### 9.4 `output_labels.csv`
记录主输出、桥接输出、解释输出。

这样做的好处是：
- 原始量与派生量分离；
- 训练输入和工程输入分离；
- 后续做 selection、adaptation、可解释性分析更干净。

---

## 10. 一句话执行建议

你现在最应该做的，不是继续把变量表扩得更大，而是：

**先锁定母场景与单位体系，再把变量分成“固定项 / subset 项 / 主 DOE 项 / 扰动项 / 派生桥接项”，随后用“subset 分层 + 子集内 LHS + 边界补样”的方式，把高保真 FEA benchmark 控制在 10^2 量级，而不是让问题膨胀到无法计算的 10^5–10^6 量级。**

