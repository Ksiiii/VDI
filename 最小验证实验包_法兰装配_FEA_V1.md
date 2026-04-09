# 多螺栓法兰连接装配任务：最小验证实验包（可直接交给师兄执行）

## 0. 本文档用途

这不是最终 benchmark，也不是完整论文实验，而是一套**当下即可执行的最小验证实验包**。其目的只有四个：

1. 验证当前输入输出流在 **高保真 FEA** 中是否真正可落地；
2. 验证核心主输出 `p_min_gasket` / `seal_margin` / `seal_pass` 是否可稳定提取；
3. 验证“**主变量收缩 + 变量分层 + subset 控制 + DOE 采样**”的方案是否能够在有限仿真预算内跑通；
4. 为后续 low-/high-fidelity 对齐、subset selection、TabPFN 适配提供第一批正式高保真样本。

**建议定位**：
- 这批数据不是最终论文主结果；
- 这批数据的角色是 **高保真链路验证包 + 第一版 benchmark seed**；
- 目标不是把变量铺满，而是先跑出一批**定义清晰、输出稳定、便于后续扩展**的数据。

---

## 1. 本最小包要验证什么

本最小包聚焦于一个明确任务：

> 在固定母场景下，预测多螺栓法兰连接装配中的 **最小垫片接触压力 `p_min_gasket`** 及其对应的 **密封安全裕量 `seal_margin`**。

本包只回答以下最小问题：

### Q1. 当前主变量体系在高保真 FEA 中能否稳定得到标签？
也就是：每个 case 是否都能提取出统一格式的输入、桥接量、主输出和解释输出。

### Q2. 用“少量主变量 + 两个装配子集”是否已经能观察到明显物理差异？
也就是：同一连续参数点下，仅改变装配散布水平，`p_min_gasket` 和 `contact_uniformity_index` 是否发生可解释变化。

### Q3. 当前样本量是否足以作为第一版 high-fidelity seed set？
也就是：在 20–30 个高保真样本量级上，是否已经能够支撑：
- 变量定义固化；
- 输出提取脚本固化；
- 初步与 low-fidelity bridge 对齐；
- 后续继续扩样。

---

## 2. 设计原则：为什么这个包要这样做

本包严格采用以下原则：

1. **固定母场景，不做开放式几何大扩展**；
2. **共享输入语言保留，但自由变量收缩**；
3. **将变量分成固定层、DOE 主变量层、subset 层、派生桥接层**；
4. **先做 paired subset 对比，而不是一次性铺开所有离散组合**；
5. **先验证数据链路和标签可提取性，再追求更复杂 domain gap**。

因此，第一版不追求：
- 多种法兰结构并行；
- 同时开放螺栓数、偏心、外载、温差、摩擦散布、垫片家族等所有维度；
- 一次性构造大规模 train/val/test。

---

## 3. 变量分层：这次谁固定，谁变化

## 3.1 L0：固定母场景常量层（本包中不扫）

这些变量保留在总输入字典里，但在本最小包中固定不变。

| 变量名 | 建议值 | 单位 | 说明 |
|---|---:|---|---|
| `bolt_num` | 8 | / | 固定 8 螺栓法兰母场景 |
| `bolt_circle_diameter` | 180 | mm | 螺栓分布圆直径 |
| `flange_effective_width` | 24 | mm | 法兰有效宽度 |
| `gasket_effective_width` | 18 | mm | 垫片有效宽度 |
| `bolt_nominal_diameter` | M16 | / | 紧固件规格 |
| `bolt_strength_class` | 8.8 | / | 螺栓强度等级 |
| `E_flange` | 210000 | MPa | 法兰弹性模量 |
| `E_bolt` | 210000 | MPa | 螺栓弹性模量 |
| `mu_thread` | 0.14 | / | 第一版固定 |
| `mu_bearing` | 0.14 | / | 第一版固定 |
| `external_axial_load_eq` | 0 | N | 第一版不引入额外轴向外载 |
| `load_eccentricity_a` | 0 | mm | 第一版不引入偏心 |
| `clamping_eccentricity_s_sym` | 0 | mm | 第一版不引入夹紧偏心 |
| `temperature_delta` | 0 | °C | 第一版不引入热载荷 |

> 注：如果师兄已有现成 CAD/CAE 母模型，以上固定值可替换为现成模型更方便的标称值；但**优先保证“固定母场景 + 相同子集逻辑 + 相同 DOE 结构”不变**。

---

## 3.2 L1：主 DOE 连续变量层（本包真正要扫的变量）

本包只扫 5 个连续变量：

| 变量名 | 范围 | 单位 | 角色 |
|---|---:|---|---|
| `flange_thickness` | 20 – 32 | mm | 主几何刚度变量 |
| `gasket_thickness` | 1.5 – 3.0 | mm | 接触/压缩关键变量 |
| `E_gasket_eq` | 200 – 1200 | MPa | 垫片等效刚度 |
| `target_preload_per_bolt` | 35000 – 65000 | N | 主装配控制量 |
| `internal_pressure` | 2 – 12 | MPa | 主工况变量 |

这 5 个变量已经足够支撑第一批高保真标签构建；不建议当前再同时放开摩擦、偏心、外载、螺栓数。

---

## 3.3 L2：subset 子集层（本包只开一个离散因素）

本最小包只开放一个 subset 因素：

| subset 名称 | `preload_scatter_ratio` | 含义 |
|---|---:|---|
| `S0_uniform` | 0.00 | 理想装配：各螺栓预紧力一致 |
| `S1_scattered` | 0.10 | 非理想装配：存在 10% 预紧力散布 |

这样设计的原因：
- 它直接对应你当前最重要的装配因素；
- 它能在相同几何/工况点上形成 paired comparison；
- 它已经足够构成第一版“具有物理意义的 subset”。

---

## 3.4 L3：桥接与解释层（不作为自由输入）

以下量不作为本次 DOE 自由变量，而作为后处理输出提取：

- 桥接层：`FKP`、`FKerf`、`Phi`、`FKR`
- 主输出层：`p_min_gasket`、`p_req_seal`、`seal_margin`、`seal_pass`
- 解释输出层：`contact_uniformity_index`、`contact_area_ratio`、`flange_opening_max`、`preload_actual_mean`、`preload_actual_std`

---

## 4. 统一量纲与存储规范

为了避免后续低保真、高保真和机器学习数据表之间出现量纲混乱，本包统一采用以下存储单位：

- 长度：`mm`
- 力：`N`
- 压力/应力/模量：`MPa`
- 温差：`°C`
- 摩擦系数、比例、散布率：无量纲

### 4.1 关键字段单位约定

| 字段 | 单位 |
|---|---|
| `flange_thickness` | mm |
| `gasket_thickness` | mm |
| `bolt_circle_diameter` | mm |
| `gasket_effective_width` | mm |
| `target_preload_per_bolt` | N |
| `internal_pressure` | MPa |
| `E_gasket_eq` | MPa |
| `p_min_gasket` | MPa |
| `p_req_seal` | MPa |
| `seal_margin` | MPa |
| `flange_opening_max` | mm |
| `contact_area_ratio` | / |
| `contact_uniformity_index` | / |

---

## 5. 仿真分两步走：先 4 个试跑点，再 24 个正式点

## 5.1 Step A：4 个试跑点（先做链路验证）

建议先跑下面 4 个 case，目的不是做统计，而是检查：
- 几何参数化是否稳定；
- 接触/预紧/加载流程是否稳定；
- 网格和收敛是否可接受；
- 标签提取脚本是否能自动输出。

| case_id | subset | flange_thickness (mm) | gasket_thickness (mm) | E_gasket_eq (MPa) | target_preload_per_bolt (N) | internal_pressure (MPa) | 说明 |
|---|---|---:|---:|---:|---:|---:|---|
| P01 | S0_uniform | 26.0 | 2.20 | 700 | 50000 | 6.0 | 中心点 |
| P02 | S0_uniform | 26.0 | 2.20 | 700 | 38000 | 11.0 | 高压/低预紧极端 |
| P03 | S0_uniform | 26.0 | 2.20 | 700 | 62000 | 3.0 | 低压/高预紧极端 |
| P04 | S1_scattered | 22.0 | 3.00 | 300 | 45000 | 10.0 | 软垫片 + 厚垫片 + 散布验证 |

### Step A 的通过标准

若以下条件基本满足，则进入正式 DOE：

1. 4 个 case 都能收敛；
2. 输出字段都能被统一抽取；
3. `S1_scattered` 相比 `S0_uniform` 至少在 `p_min_gasket` 或 `contact_uniformity_index` 上表现出可解释差异；
4. 没有大量人工修补才能完成后处理。

---

## 5.2 Step B：24 个正式 case（最小 paired DOE）

正式 DOE 采用：
- 12 个连续参数 base points；
- 每个 base point 跑两个 subset（`S0_uniform` / `S1_scattered`）；
- 总计 **24 个高保真样本**。

这种设计的优势是：
- 同一个连续参数点上可以直接比较“是否有预紧散布”；
- 样本量仍然可控；
- 数据结构天然适合后续做 subset 分析和可视化。

### 12 个 base points（连续变量）

| base_id | flange_thickness (mm) | gasket_thickness (mm) | E_gasket_eq (MPa) | target_preload_per_bolt (N) | internal_pressure (MPa) |
|---|---:|---:|---:|---:|---:|
| B01 | 27.1 | 2.48 | 770 | 36712 | 11.22 |
| B02 | 25.7 | 1.99 | 264 | 48289 | 3.17 |
| B03 | 31.5 | 1.77 | 565 | 43073 | 5.33 |
| B04 | 22.3 | 2.94 | 1092 | 57357 | 3.85 |
| B05 | 24.7 | 1.59 | 654 | 59691 | 6.24 |
| B06 | 29.0 | 2.84 | 797 | 64139 | 2.75 |
| B07 | 21.0 | 2.73 | 1174 | 39607 | 10.69 |
| B08 | 26.9 | 2.14 | 522 | 45080 | 5.76 |
| B09 | 30.2 | 2.04 | 896 | 41940 | 9.19 |
| B10 | 23.2 | 2.58 | 438 | 53027 | 7.92 |
| B11 | 28.4 | 1.67 | 1006 | 60787 | 10.16 |
| B12 | 20.6 | 2.26 | 365 | 50669 | 7.04 |

### 24 个正式运行 case

| case_id | base_id | subset | preload_scatter_ratio |
|---|---|---|---:|
| C01 | B01 | S0_uniform | 0.00 |
| C02 | B01 | S1_scattered | 0.10 |
| C03 | B02 | S0_uniform | 0.00 |
| C04 | B02 | S1_scattered | 0.10 |
| C05 | B03 | S0_uniform | 0.00 |
| C06 | B03 | S1_scattered | 0.10 |
| C07 | B04 | S0_uniform | 0.00 |
| C08 | B04 | S1_scattered | 0.10 |
| C09 | B05 | S0_uniform | 0.00 |
| C10 | B05 | S1_scattered | 0.10 |
| C11 | B06 | S0_uniform | 0.00 |
| C12 | B06 | S1_scattered | 0.10 |
| C13 | B07 | S0_uniform | 0.00 |
| C14 | B07 | S1_scattered | 0.10 |
| C15 | B08 | S0_uniform | 0.00 |
| C16 | B08 | S1_scattered | 0.10 |
| C17 | B09 | S0_uniform | 0.00 |
| C18 | B09 | S1_scattered | 0.10 |
| C19 | B10 | S0_uniform | 0.00 |
| C20 | B10 | S1_scattered | 0.10 |
| C21 | B11 | S0_uniform | 0.00 |
| C22 | B11 | S1_scattered | 0.10 |
| C23 | B12 | S0_uniform | 0.00 |
| C24 | B12 | S1_scattered | 0.10 |

> 若计算资源非常紧，可先只跑 `C01–C12`（即 6 个 base points × 2 subsets = 12 个样本）；但更推荐一次跑完整 24 个正式 case。

---

## 6. 如何在 FEA 中实现 `preload_scatter_ratio`

为避免引入随机性导致复现实验困难，建议本最小包采用**确定性散布模式**。

设目标预紧力为 `F0 = target_preload_per_bolt`，散布率为 `r = preload_scatter_ratio`。

### 6.1 `S0_uniform`
所有螺栓：

`F_i = F0`

### 6.2 `S1_scattered`
8 个螺栓沿圆周按固定顺序施加以下预紧力：

- `F1 = F0 × (1 + 1.00r)`
- `F2 = F0 × (1 - 1.00r)`
- `F3 = F0 × (1 + 0.50r)`
- `F4 = F0 × (1 - 0.50r)`
- `F5 = F0 × (1 + 0.75r)`
- `F6 = F0 × (1 - 0.75r)`
- `F7 = F0 × (1 + 0.25r)`
- `F8 = F0 × (1 - 0.25r)`

该模式满足：
- 平均预紧力仍约等于 `F0`；
- 存在清晰、可复现的环向不均匀性；
- 便于与 `S0_uniform` 直接比较。

若师兄已有更成熟的装配散布施加方式，也可替换，但要保证：
- 散布定义固定；
- 数据表中明确记录；
- 后续所有 case 统一执行同一规则。

---

## 7. 每个 case 需要返回哪些输出

## 7.1 主输出（必须返回）

| 输出名 | 单位 | 定义 |
|---|---|---|
| `p_min_gasket` | MPa | 垫片有效接触路径上的最小法向接触压力；若局部张开，则该处按 0 计 |
| `p_req_seal` | MPa | 密封所需最小接触压力阈值；本值可由垫片规格/规则单独给定，不一定由 FEA 直接产生 |
| `seal_margin` | MPa | `p_min_gasket - p_req_seal` |
| `seal_pass` | 0/1 | 若 `seal_margin >= 0`，则为 1，否则为 0 |

> 说明：如果 `p_req_seal` 在当前阶段尚未完全确定，也请师兄先返回 `p_min_gasket`，`seal_margin` 和 `seal_pass` 可由你后处理补算。

---

## 7.2 辅助解释输出（强烈建议返回）

| 输出名 | 单位 | 建议定义 |
|---|---|---|
| `contact_uniformity_index` | / | 建议定义为垫片接触压力正值节点/单元的 `p05 / p50`，越接近 1 表示越均匀 |
| `contact_area_ratio` | / | 发生有效接触的垫片面积 / 垫片总有效面积 |
| `flange_opening_max` | mm | 工作载荷后法兰密封面最大开口量 |
| `preload_actual_mean` | N | 装配完成后各螺栓实际预紧力均值 |
| `preload_actual_std` | N | 装配完成后各螺栓实际预紧力标准差 |

---

## 7.3 低高保真桥接量（若可方便计算，建议一起返回）

| 输出名 | 单位 | 备注 |
|---|---|---|
| `FKP` | N | 密封功能所需最小夹紧力 |
| `FKerf` | N | 功能要求最小夹紧力 |
| `Phi` | / | 载荷分配系数 |
| `FKR` | N | 工作状态残余夹紧力 |

> 这部分若不能由 FEA 直接给出，可后续由低保真解析链补入；但若师兄方便从同一 case 同步给出，将显著有利于后续 bridge 对齐。

---

## 8. 建议交付文件格式

建议请师兄最终返回至少以下 3 类文件。

## 8.1 `hf_case_inputs.csv`
每行一个 case，记录：

- `case_id`
- `base_id`
- `subset`
- 全部 L0 固定参数
- 全部 L1 主 DOE 参数
- `preload_scatter_ratio`
- 若采用散布模式，最好额外记录 `preload_pattern_id`

## 8.2 `hf_case_outputs.csv`
每行一个 case，记录：

- `case_id`
- `p_min_gasket`
- `p_req_seal`
- `seal_margin`
- `seal_pass`
- `contact_uniformity_index`
- `contact_area_ratio`
- `flange_opening_max`
- `preload_actual_mean`
- `preload_actual_std`
- 若有则加入 `FKP` / `FKerf` / `Phi` / `FKR`

## 8.3 `plots/` 文件夹（建议）
建议每个 subset 至少保留 2–4 个代表 case 的图：

- 垫片接触压力云图
- 法兰开口/位移图
- 螺栓载荷分布图
- 若可能，导出沿垫片路径的接触压力曲线

---

## 9. 建议的验收标准

跑完这批最小包后，如果满足以下条件，就说明你的高保真链路已经基本建立成功：

### A. 工程链路通过
- 大部分 case 能稳定收敛；
- 参数化建模和批量运行是可重复的；
- 后处理字段能自动或半自动稳定导出。

### B. 标签定义通过
- `p_min_gasket` 的定义在所有 case 中都一致；
- `seal_margin` 可以统一计算；
- `seal_pass` 可以无歧义阈值化。

### C. subset 设计通过
- 对同一 `base_id`，`S1_scattered` 相比 `S0_uniform` 的输出变化具有可解释性；
- 至少部分 case 中，装配散布会降低 `p_min_gasket`、降低 `contact_uniformity_index` 或增大开口。

### D. benchmark seed 通过
- 这批样本已经可作为第一版 high-fidelity seed set；
- 后续可在此基础上继续扩展新的 subset（如偏心、外载、摩擦、螺栓数）。

---

## 10. 这批最小包跑完之后，下一步怎么接

若本包顺利跑通，下一步建议不是立刻扩成海量样本，而是按以下顺序推进：

1. 先对这批样本做统一整理，固化字段命名和单位；
2. 补齐 low-fidelity 对应 case 的桥接量；
3. 做第一版 high-/low-fidelity 对比分析；
4. 再决定第二批高保真扩样优先开放哪个 subset 维度：
   - `bolt_num`
   - `preload_scatter_ratio` 更细等级
   - `load_eccentricity_a`
   - `mu_thread` / `mu_bearing`
   - `external_axial_load_eq`

**不建议**在第一批最小包还没跑稳时，就同时扩展多个离散因素。

---

## 11. 可直接发给师兄的简短说明

师兄您好，这里给您一版我现在最需要的最小高保真验证实验包。当前目的不是做最终大规模 benchmark，而是先把多螺栓法兰装配任务的 FEA 数据链路跑通，并验证统一标签是否可稳定提取。

这版只固定一个母场景，正式只扫 5 个连续变量：
- 法兰厚度 `flange_thickness`
- 垫片厚度 `gasket_thickness`
- 垫片等效刚度 `E_gasket_eq`
- 单螺栓目标预紧力 `target_preload_per_bolt`
- 内压 `internal_pressure`

同时只开放一个 subset 因素：
- `S0_uniform`：理想均匀预紧
- `S1_scattered`：10% 预紧力散布

我希望先拿到：
- 4 个试跑点
- 24 个正式 case（12 个 base points × 2 个 subsets）

最关键需要返回的输出是：
- `p_min_gasket`
- `p_req_seal`（若暂时不方便可后补）
- `seal_margin`
- `seal_pass`
- `contact_uniformity_index`
- `contact_area_ratio`
- `flange_opening_max`

如果这批数据能稳定跑通，我后续就可以正式进入高低保真对齐和 TabPFN 领域适配阶段。

---

## 12. 一句话总结

这套最小验证实验包的本质是：

> **用一个固定母场景、5 个主 DOE 连续变量、2 个装配 subset、总计 28 个 FEA case（4 试跑 + 24 正式），先把高保真 benchmark 的最小闭环建立起来。**

