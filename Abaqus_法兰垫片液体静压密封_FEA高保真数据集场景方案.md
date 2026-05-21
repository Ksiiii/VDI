# Abaqus 高保真数据集最小场景方案：8 螺栓法兰-垫片液体静压密封模型

**文件定位**：本文件用于指导同门在 Abaqus 中建立一套可批量运行、可稳定后处理、可扩展到 300–500 条高保真样本的最小法兰-垫片密封仿真场景。

**研究任务**：在固定母场景下，通过有限元仿真获得多螺栓法兰连接中垫片有效密封面的接触压力分布，并构造用于机器学习的高保真标签：

- `p_min_gasket_eff`
- `p_req_seal`
- `seal_margin`
- `seal_pass`
- `contact_uniformity_index`
- `flange_opening_max`

本方案优先追求：**可建模、可收敛、可批量、可解释、可与低保真 synthetic universe 对齐**。

---

## 1. 最小研究场景固定

### 1.1 场景名称

**8 螺栓小直径平面法兰-软垫片液体静压密封模型**

### 1.2 密封对象

本场景限定为：

```text
水介质 / 液体静压密封 / 室温 / 无热载荷 / 无外部轴向载荷 / 无偏心载荷
```

选择液体静压密封的原因：

1. 水介质压力边界容易在 Abaqus 中表达；
2. 不需要模拟气体可压缩性；
3. 不需要建立真实泄漏流道；
4. 可以把问题收缩为“内压作用下垫片接触压力是否足够”的结构接触问题；
5. 对后续机器学习任务而言，`seal_margin` 的物理解释清晰。

### 1.3 本阶段不模拟的内容

第一版不引入以下复杂因素：

```text
1. 流体-结构耦合
2. 真实泄漏率计算
3. 温度载荷
4. 外部轴向管道载荷
5. 弯矩或偏心载荷
6. 垫片塑性损伤
7. 螺纹细节
8. 法兰标准全尺寸族变化
```

本阶段的密封判据采用：

```text
垫片有效密封区域的接触压力 >= 所需密封接触压力阈值
```

因此，本场景得到的是 **contact-pressure-based sealing proxy dataset**。

---

## 2. FEA 模型示意图

建议使用完整 360° 三维模型，因为后续需要模拟 8 个螺栓不同预紧力带来的环向不均匀接触。若只做均匀预紧，可以用轴对称模型预验证；正式数据集建议统一使用三维完整模型。

![FEA model schematic](flange_gasket_fea_model_schematic.png)

图中包括：

- 上法兰；
- 下法兰；
- 环形软垫片；
- 8 个 M16 螺栓；
- 中央承压水腔；
- 垫片上下接触界面；
- 螺栓预紧；
- 内压载荷；
- 输出接触压力 `CPRESS`。

---

## 3. 单位体系

统一采用 Abaqus 常用工程单位：

| 物理量 | 单位 |
|---|---|
| 长度 | mm |
| 力 | N |
| 压力 / 应力 / 弹性模量 | MPa |
| 时间 | s，可忽略 |
| 温度 | °C，本阶段固定 0 温差 |
| 摩擦系数 / 比例量 | 无量纲 |

重要换算：

```text
1 MPa = 1 N/mm²
```

Abaqus 中施加内压时，`internal_pressure = 6 MPa` 可直接理解为 `6 N/mm²`。

---

## 4. 几何母场景

本模型采用一个“科研用简化小型法兰”作为固定母场景。它不追求严格等同某一个工业标准法兰，重点是保证变量、输出和物理机制清晰稳定。

### 4.1 固定几何参数

| 参数名 | 符号 | 建议值 | 单位 | 说明 |
|---|---:|---:|---|---|
| 法兰外径 | `D_flange_out` | 220 | mm | 固定 |
| 中央通孔直径 | `D_bore` | 60 | mm | 水压作用内腔 |
| 垫片内径 | `D_gasket_in` | 70 | mm | 略大于流道孔 |
| 垫片外径 | `D_gasket_out` | 120 | mm | 形成有效密封环 |
| 螺栓分布圆直径 | `D_bolt_circle` | 160 | mm | 8 螺栓均布 |
| 螺栓孔直径 | `D_bolt_hole` | 18 | mm | M16 间隙孔 |
| 螺栓公称直径 | `D_bolt` | 16 | mm | M16 简化光杆 |
| 螺栓数量 | `bolt_num` | 8 | / | 全模型 |
| 法兰厚度 | `flange_thickness` | 18–30 | mm | DOE 变量 |
| 垫片厚度 | `gasket_thickness` | 1.5–3.0 | mm | DOE 变量 |

### 4.2 几何建模建议

Abaqus 中建议建立以下 part：

```text
1. upper_flange
2. lower_flange
3. gasket_ring
4. bolt_1 ... bolt_8
5. washer/head/nut equivalent pads，可与 bolt 合并或 tie
```

为了简化：

- 螺纹不建模；
- 螺栓可建成圆柱光杆；
- 螺栓头和螺母可简化为圆柱垫片或刚性加载垫；
- 垫片用实体环形件建模；
- 法兰密封面做平面接触即可。

如果师兄已有现成法兰 CAD，可保留现有 CAD，但必须保持：

```text
D_gasket_in、D_gasket_out、D_bolt_circle、bolt_num、输入变量、输出定义一致
```

---

## 5. 材料模型

### 5.1 法兰材料

| 参数 | 值 |
|---|---:|
| 材料 | 碳钢 / 结构钢 |
| 弹性模量 `E_flange` | 210000 MPa |
| 泊松比 `nu_flange` | 0.30 |
| 塑性 | 第一版不启用 |

### 5.2 螺栓材料

| 参数 | 值 |
|---|---:|
| 螺栓规格 | M16 |
| 强度等级 | 8.8 |
| 弹性模量 `E_bolt` | 210000 MPa |
| 泊松比 `nu_bolt` | 0.30 |
| 建议预紧范围 | 20000–60000 N / bolt |

说明：

- M16 8.8 螺栓的预紧力范围在本场景中主要用于仿真采样；
- 不在第一版中模拟螺栓屈服；
- 若同门发现高预紧 case 出现明显局部屈服，可优先降低上限至 55000 N。

### 5.3 垫片材料

第一版建议使用 **等效线弹性软垫片**，用于保证数据链路稳定。

| 参数 | 范围 |
|---|---:|
| 垫片类型 | 非金属压缩垫片等效模型 |
| 等效弹性模量 `E_gasket_eq` | 200–1000 MPa |
| 泊松比 `nu_gasket` | 0.25 |
| 厚度 `gasket_thickness` | 1.5–3.0 mm |

建议先使用实体单元模拟垫片。若后续需要更接近垫片压缩行为，可升级为：

```text
1. 非线性压缩曲线
2. Abaqus gasket element
3. 压缩-卸载滞回模型
```

第一版高保真 benchmark 的目标是稳定提取 `CPRESS` 分布，因此线弹性等效垫片足够作为最小场景。

---

## 6. 接触设置

### 6.1 必需接触对

| 接触对 | 法向行为 | 切向行为 | 说明 |
|---|---|---|---|
| 上法兰密封面 - 垫片上表面 | hard contact | frictionless 或 μ=0.10 | 必需 |
| 下法兰密封面 - 垫片下表面 | hard contact | frictionless 或 μ=0.10 | 必需 |
| 螺栓头/垫片 - 上法兰 | hard contact 或 tie | 可简化 | 可用 tie 降低收敛难度 |
| 螺母/垫片 - 下法兰 | hard contact 或 tie | 可简化 | 可用 tie 降低收敛难度 |

### 6.2 推荐第一版设置

为了提高收敛概率，第一版建议：

```text
法兰-垫片接触：hard contact + frictionless
螺栓头/螺母接触：tie 或 hard contact
大变形：NLGEOM = ON
```

等数据链路稳定后，再把法兰-垫片切向行为改为 `penalty friction μ=0.10` 做鲁棒性对照。

---

## 7. 边界条件与载荷步骤

### 7.1 坐标约定

建议：

```text
Z 轴：法兰轴向
XY 平面：法兰环向平面
Z 正方向：由下法兰指向上法兰
```

### 7.2 约束设置

为避免刚体运动，推荐：

```text
1. 下法兰远端底面：U3 = 0
2. 下法兰某一参考点：U1 = U2 = 0
3. 另一个非共线参考点：约束一个切向自由度，防止绕 Z 轴整体转动
```

避免把整个下法兰全部 `U1=U2=U3=0`，过强约束可能改变接触压力分布。

### 7.3 分析步

建议使用 `Static, General`，并设置 `NLGEOM = ON`。

#### Step 0：Initial

- 建立接触；
- 检查几何初始间隙；
- 不施加预紧或内压。

#### Step 1：Bolt preload

对 8 个螺栓施加预紧力：

```text
F_i = target_preload_per_bolt × preload_factor_i
```

均匀预紧时：

```text
preload_factor_i = 1.0
```

有散布时采用固定模式，见第 9 节。

#### Step 2：Bolt lock / relaxation

将螺栓预紧长度锁定，让结构发生接触重分布。

Abaqus 中可以通过 bolt load 的 “fix at current length” 或等效 connector 方式实现。

#### Step 3：Internal pressure

对中央内腔和内压作用面施加压力：

```text
internal_pressure = 2–10 MPa
```

压力作用位置包括：

```text
1. 中央孔内壁；
2. 上下法兰内侧承压面；
3. 垫片内侧暴露于压力的边界面，如果建模中存在该暴露面。
```

最终输出在 Step 3 末帧提取。

---

## 8. 输入变量设计

### 8.1 L0 固定母场景变量

| 变量名 | 值 | 单位 |
|---|---:|---|
| `medium` | water | / |
| `temperature_delta` | 0 | °C |
| `bolt_num` | 8 | / |
| `bolt_nominal_diameter` | 16 | mm |
| `bolt_strength_class` | 8.8 | / |
| `D_flange_out` | 220 | mm |
| `D_bore` | 60 | mm |
| `D_gasket_in` | 70 | mm |
| `D_gasket_out` | 120 | mm |
| `D_bolt_circle` | 160 | mm |
| `D_bolt_hole` | 18 | mm |
| `E_flange` | 210000 | MPa |
| `nu_flange` | 0.30 | / |
| `E_bolt` | 210000 | MPa |
| `nu_bolt` | 0.30 | / |
| `nu_gasket` | 0.25 | / |
| `external_axial_load_eq` | 0 | N |
| `load_eccentricity_a` | 0 | mm |

### 8.2 L1 主采样变量

第一版正式 300–500 条 FEA 数据建议开放 6 个变量：

| 变量名 | 范围 | 单位 | 类型 | 说明 |
|---|---:|---|---|---|
| `flange_thickness` | 18–30 | mm | 连续 | 法兰刚度 |
| `gasket_thickness` | 1.5–3.0 | mm | 连续 | 垫片压缩与接触 |
| `E_gasket_eq` | 200–1000 | MPa | 连续 | 垫片等效刚度 |
| `target_preload_per_bolt` | 20000–60000 | N | 连续 | 装配预紧 |
| `internal_pressure` | 2–10 | MPa | 连续 | 液体内压 |
| `preload_scatter_ratio` | 0–0.15 | / | 连续/分层 | 螺栓预紧不均匀 |

### 8.3 暂不开放的变量

| 变量名 | 当前处理 |
|---|---|
| `bolt_num` | 固定为 8 |
| `D_bolt_circle` | 固定 |
| `load_eccentricity_a` | 固定为 0 |
| `external_axial_load_eq` | 固定为 0 |
| `mu_thread` | 不直接建模 |
| `mu_bearing` | 不直接建模 |
| `temperature_delta` | 固定为 0 |

这些变量后续可以作为第二版 benchmark 的扩展方向。

---

## 9. 预紧散布定义

为了保证数据可复现，预紧散布采用确定性环向模式。

设：

```text
F0 = target_preload_per_bolt
r  = preload_scatter_ratio
```

8 个螺栓按圆周编号 1–8，预紧力定义为：

| 螺栓编号 | 预紧力 |
|---:|---:|
| 1 | `F0 × (1 + 1.00r)` |
| 2 | `F0 × (1 - 1.00r)` |
| 3 | `F0 × (1 + 0.50r)` |
| 4 | `F0 × (1 - 0.50r)` |
| 5 | `F0 × (1 + 0.75r)` |
| 6 | `F0 × (1 - 0.75r)` |
| 7 | `F0 × (1 + 0.25r)` |
| 8 | `F0 × (1 - 0.25r)` |

当 `r = 0` 时，所有螺栓预紧力相同。

这个设计有三个优点：

```text
1. 均值保持为 F0；
2. 环向不均匀性明确；
3. 每个 case 可完全复现。
```

---

## 10. 密封阈值与标签定义

### 10.1 输出接触压力

从 Abaqus 输出变量中提取垫片接触界面的：

```text
CPRESS
```

建议提取位置：

```text
垫片上表面与上法兰接触区域
垫片下表面与下法兰接触区域
```

如果上下表面结果接近，可取两者的较小值作为保守输出：

```text
CPRESS_eff = min(CPRESS_top, CPRESS_bottom)
```

### 10.2 不建议直接使用 raw minimum

接触压力的逐点最小值容易受边缘单元、局部接触噪声、网格质量影响。建议同时保存两个量：

```text
p_min_gasket_raw = min(CPRESS_eff)
p_min_gasket_eff = area-weighted 5th percentile of CPRESS_eff over effective sealing band
```

正式机器学习主标签建议使用：

```text
p_min_gasket_eff
```

### 10.3 有效密封区域

有效密封区域定义为垫片环形接触区域：

```text
D_gasket_in ≤ radial_position ≤ D_gasket_out
```

边缘 5% 宽度可在后处理时排除，以降低边缘接触奇异性影响：

```text
effective sealing band:
D_gasket_in + 0.05 × gasket_width ≤ r × 2 ≤ D_gasket_out - 0.05 × gasket_width
```

如后处理不便，第一版可直接使用全垫片接触区域，但必须在所有 case 中保持一致。

### 10.4 密封需求阈值

第一版为了形成可学习、可比较的标签，建议使用统一工程代理阈值：

```text
p_req_seal = 5 + 1.5 × internal_pressure
```

单位均为 MPa。

示例：

| `internal_pressure` | `p_req_seal` |
|---:|---:|
| 2 MPa | 8 MPa |
| 6 MPa | 14 MPa |
| 10 MPa | 20 MPa |

说明：

- 该阈值是第一版研究用 sealing proxy；
- 后续如果有明确垫片标准或实验数据，可以替换；
- 所有 case 必须保存 `p_req_seal` 字段，避免阈值隐藏在代码中。

### 10.5 主标签

```text
seal_margin = p_min_gasket_eff - p_req_seal
```

```text
seal_pass = 1, if seal_margin >= 0
seal_pass = 0, if seal_margin < 0
```

推荐主回归任务：

```text
seal_margin
```

推荐辅助回归任务：

```text
p_min_gasket_eff
```

推荐辅助分类任务：

```text
seal_pass
```

---

## 11. 辅助输出与后处理定义

### 11.1 接触均匀性

```text
contact_uniformity_index = p05(CPRESS_eff) / p50(CPRESS_eff)
```

其中：

- `p05` 为面积加权 5% 分位数；
- `p50` 为面积加权中位数；
- 若 `p50 = 0`，该指标记为 0。

解释：

```text
越接近 1，接触压力越均匀；
越接近 0，局部低压或张开越明显。
```

### 11.2 接触面积比例

```text
contact_area_ratio = area(CPRESS_eff > 0.1 MPa) / total_effective_gasket_area
```

阈值 `0.1 MPa` 用于排除数值接触噪声。

### 11.3 最大张口量

```text
flange_opening_max = max(normal separation between flange sealing surface and gasket)
```

如果后处理难以直接提取 gap，可用上、下法兰密封面相对位移差的最大值作为 proxy。

### 11.4 螺栓残余力

Step 3 末帧提取每个螺栓的轴力：

```text
bolt_force_1 ... bolt_force_8
```

并派生：

```text
bolt_force_mean
bolt_force_std
bolt_load_imbalance_index = bolt_force_std / bolt_force_mean
```

---

## 12. Abaqus 建模执行清单

### 12.1 Part

```text
upper_flange
lower_flange
gasket_ring
bolt_1 ... bolt_8
bolt_head_or_washer_equivalent
nut_or_washer_equivalent
```

### 12.2 Property

```text
steel_flange: E=210000 MPa, nu=0.30
steel_bolt:   E=210000 MPa, nu=0.30
gasket:       E=E_gasket_eq, nu=0.25
```

### 12.3 Assembly

```text
1. 上下法兰同轴；
2. 垫片位于两法兰密封面之间；
3. 8 个螺栓均布在 PCD=160 mm 圆周上；
4. 初始接触面尽量无明显穿透；
5. 垫片初始厚度由 gasket_thickness 控制。
```

### 12.4 Interaction

```text
flange-gasket: surface-to-surface hard contact
bolt head / nut: tie or hard contact
```

### 12.5 Load

```text
Step 1: bolt preload
Step 2: bolt lock
Step 3: internal pressure
```

### 12.6 Boundary

```text
lower flange axial support + minimal rigid body constraints
```

### 12.7 Mesh

建议：

| 区域 | 单元类型 | 建议尺寸 |
|---|---|---:|
| 垫片 | C3D8R 或 C3D8 | 1.0–1.5 mm |
| 法兰密封面附近 | C3D8R 或 C3D10 | 1.5–2.5 mm |
| 法兰远离接触区 | C3D8R 或 C3D10 | 3–5 mm |
| 螺栓 | C3D8R 或 C3D10 | 2–3 mm |

若采用复杂 CAD 自动网格，可用 C3D10 四面体单元，但接触区域需要足够细。

---

## 13. 收敛建议

如果出现接触收敛困难，按以下顺序调整：

```text
1. 检查初始穿透和间隙；
2. 降低第一步预紧增量；
3. 采用 smooth step 载荷幅值；
4. 法兰-垫片切向先用 frictionless；
5. 接触稳定化打开，但控制稳定化能量比例；
6. 降低 internal_pressure 上限到 8 MPa 试跑；
7. 将 gasket E 上限从 1000 MPa 降到 800 MPa 试跑；
8. 检查垫片网格是否过粗；
9. 优先保证 8 个试跑 case 成功，再进入批量采样。
```

---

## 14. 采样策略：从试跑到 300–500 条 FEA

### 14.1 总体采样原则

本场景的高保真数据集不采用全因子扫描。推荐：

```text
物理子域分层 + 子域内 Maximin LHS + 临界区域补样
```

### 14.2 Stage A：8 个试跑 case

先跑 8 个 case，验证建模流程和标签提取。

| case_id | flange_thickness | gasket_thickness | E_gasket_eq | target_preload_per_bolt | internal_pressure | preload_scatter_ratio | 目的 |
|---|---:|---:|---:|---:|---:|---:|---|
| P01 | 24 | 2.2 | 600 | 40000 | 6 | 0.00 | 中心点 |
| P02 | 24 | 2.2 | 600 | 40000 | 6 | 0.10 | 散布对照 |
| P03 | 18 | 3.0 | 250 | 25000 | 10 | 0.12 | 高风险软垫片 |
| P04 | 30 | 1.5 | 900 | 55000 | 2 | 0.00 | 高安全裕量 |
| P05 | 18 | 1.5 | 900 | 25000 | 10 | 0.15 | 薄法兰高压低预紧 |
| P06 | 30 | 3.0 | 250 | 60000 | 8 | 0.10 | 软厚垫片高预紧 |
| P07 | 22 | 2.6 | 400 | 30000 | 8 | 0.05 | 低裕量候选 |
| P08 | 28 | 1.8 | 800 | 50000 | 4 | 0.12 | 硬垫片散布 |

通过标准：

```text
1. 至少 7/8 case 收敛；
2. 所有收敛 case 可提取 CPRESS；
3. 输出 csv 字段完整；
4. p_min_gasket_eff 随预紧力、内压、散布变化具有基本物理趋势；
5. 没有大量人工修补才能完成后处理。
```

### 14.3 Stage B：48 条 pilot FEA

正式大批量前，建议做 48 条 pilot：

```text
12 个物理子域 × 每个子域 4 条 LHS
```

用于检查：

```text
1. 哪些子域收敛困难；
2. 哪些区域 seal_margin 接近 0；
3. p_min_gasket_eff 的动态范围；
4. p_req_seal 是否需要调整；
5. 网格和后处理是否稳定。
```

### 14.4 Stage C：300–420 条正式 FEA

推荐定义 12 个 physical strata：

| stratum_id | 压力等级 | 垫片刚度等级 | 预紧散布等级 | 样本数建议 |
|---|---|---|---|---:|
| S01 | low pressure | soft gasket | uniform/low scatter | 25–35 |
| S02 | low pressure | soft gasket | high scatter | 25–35 |
| S03 | low pressure | hard gasket | uniform/low scatter | 25–35 |
| S04 | low pressure | hard gasket | high scatter | 25–35 |
| S05 | mid pressure | soft gasket | uniform/low scatter | 25–35 |
| S06 | mid pressure | soft gasket | high scatter | 25–35 |
| S07 | mid pressure | hard gasket | uniform/low scatter | 25–35 |
| S08 | mid pressure | hard gasket | high scatter | 25–35 |
| S09 | high pressure | soft gasket | uniform/low scatter | 25–35 |
| S10 | high pressure | soft gasket | high scatter | 25–35 |
| S11 | high pressure | hard gasket | uniform/low scatter | 25–35 |
| S12 | high pressure | hard gasket | high scatter | 25–35 |

总量：

```text
12 × 25 = 300
12 × 30 = 360
12 × 35 = 420
```

### 14.5 子域定义范围

| 子域变量 | low | mid | high |
|---|---:|---:|---:|
| `internal_pressure` | 2–4.5 MPa | 4.5–7 MPa | 7–10 MPa |

| 子域变量 | soft | hard |
|---|---:|---:|
| `E_gasket_eq` | 200–500 MPa | 500–1000 MPa |

| 子域变量 | uniform/low | high |
|---|---:|---:|
| `preload_scatter_ratio` | 0–0.05 | 0.08–0.15 |

在每个子域内部，对以下变量做 Maximin LHS：

```text
flange_thickness
gasket_thickness
E_gasket_eq
target_preload_per_bolt
internal_pressure
preload_scatter_ratio
```

### 14.6 临界区域补样

完成 300–360 条后，建议额外补 60–100 条 near-threshold case。

筛选条件：

```text
|seal_margin_proxy| <= 3 MPa
```

或：

```text
low-fidelity proxy 判断 p_min_gasket 接近 p_req_seal
```

补样区域优先：

```text
1. high pressure + low preload
2. soft gasket + high scatter
3. thin flange + high pressure
4. hard gasket + high scatter
```

最终形成：

```text
主 DOE：300–360
临界补样：60–100
合计：360–460
```

这与 300–500 条 FEA 预算匹配。

---

## 15. 推荐 CSV 字段

### 15.1 `hf_case_inputs.csv`

| 字段名 | 说明 |
|---|---|
| `case_id` | 唯一样本编号 |
| `batch_id` | pilot / main / threshold_refine |
| `stratum_id` | S01–S12 |
| `medium` | water |
| `D_flange_out` | 法兰外径 |
| `D_bore` | 中央孔 |
| `D_gasket_in` | 垫片内径 |
| `D_gasket_out` | 垫片外径 |
| `D_bolt_circle` | 螺栓圆直径 |
| `bolt_num` | 螺栓数 |
| `bolt_nominal_diameter` | 螺栓直径 |
| `flange_thickness` | 法兰厚度 |
| `gasket_thickness` | 垫片厚度 |
| `E_gasket_eq` | 垫片等效模量 |
| `target_preload_per_bolt` | 单螺栓目标预紧 |
| `internal_pressure` | 内压 |
| `preload_scatter_ratio` | 预紧散布 |
| `preload_pattern_id` | deterministic_8bolt_v1 |

### 15.2 `hf_case_outputs.csv`

| 字段名 | 说明 |
|---|---|
| `case_id` | 对应输入表 |
| `job_status` | converged / failed / warning |
| `p_min_gasket_raw` | CPRESS 原始最小值 |
| `p_min_gasket_eff` | 面积加权 5% 分位数 |
| `p_req_seal` | 密封阈值 |
| `seal_margin` | 密封裕量 |
| `seal_pass` | 0/1 |
| `contact_uniformity_index` | p05 / p50 |
| `contact_area_ratio` | 有效接触面积比 |
| `flange_opening_max` | 最大张口 |
| `bolt_force_1` ... `bolt_force_8` | 各螺栓残余力 |
| `bolt_force_mean` | 平均残余力 |
| `bolt_force_std` | 残余力标准差 |
| `bolt_load_imbalance_index` | 残余力不均匀系数 |
| `max_von_mises_flange` | 法兰最大等效应力 |
| `max_von_mises_bolt` | 螺栓最大等效应力 |
| `notes` | 后处理备注 |

### 15.3 `hf_case_quality.csv`

| 字段名 | 说明 |
|---|---|
| `case_id` | 样本编号 |
| `n_increments` | 收敛增量数 |
| `max_contact_penetration` | 最大接触穿透 |
| `stabilization_energy_ratio` | 稳定化能量比例 |
| `mesh_version` | 网格版本 |
| `abaqus_version` | Abaqus 版本 |
| `postprocess_script_version` | 后处理脚本版本 |

---

## 16. 交付文件夹结构

建议同门按以下结构返回：

```text
hf_fea_dataset_v1/
  00_protocol/
    fea_scenario_protocol.md
    variable_dictionary.xlsx
  01_inputs/
    hf_case_inputs.csv
  02_abaqus_models/
    base_model.cae
    scripts/
      build_model.py
      run_batch.py
      postprocess_cpress.py
  03_odb/
    C0001.odb
    C0002.odb
    ...
  04_outputs/
    hf_case_outputs.csv
    hf_case_quality.csv
  05_figures/
    cpress_contours/
    opening_contours/
    bolt_force_plots/
  06_logs/
    abaqus_job_logs/
```

---

## 17. 最小验收标准

### 17.1 建模验收

```text
1. 三维模型可参数化生成；
2. 8 个螺栓预紧可单独赋值；
3. 内压可按 case 自动修改；
4. 垫片 E 和厚度可自动修改；
5. 法兰厚度可自动修改；
6. 大多数 case 能在统一设置下收敛。
```

### 17.2 后处理验收

```text
1. 每个 case 都有 p_min_gasket_raw；
2. 每个 case 都有 p_min_gasket_eff；
3. 每个 case 都有 p_req_seal；
4. 每个 case 都有 seal_margin；
5. 每个 case 都有 contact_uniformity_index；
6. 输出字段和单位固定。
```

### 17.3 物理趋势验收

至少应观察到以下趋势中的大部分：

```text
1. target_preload_per_bolt 增大时，p_min_gasket_eff 通常增大；
2. internal_pressure 增大时，seal_margin 通常下降；
3. preload_scatter_ratio 增大时，contact_uniformity_index 通常下降；
4. flange_thickness 增大时，flange_opening_max 通常下降；
5. high pressure + low preload 更容易接近 seal_margin = 0；
6. soft gasket 与 hard gasket 在接触均匀性上表现不同。
```

---

## 18. 给同门的简短建模说明

可以直接转发如下内容：

```text
请优先建立一个 8 螺栓小型法兰-垫片液体静压密封模型。介质设为水，但不用做流体仿真，只在中央孔和内压作用面施加 2–10 MPa 静压。模型包括上下钢法兰、环形软垫片和 8 个 M16 螺栓。统一采用 mm-N-MPa 单位制。

固定几何建议为：法兰外径 220 mm，中央孔 60 mm，垫片内径 70 mm，垫片外径 120 mm，螺栓圆直径 160 mm，8 个 M16 螺栓均布，螺栓孔 18 mm。

第一版只开放 6 个变量：法兰厚度 18–30 mm，垫片厚度 1.5–3.0 mm，垫片等效模量 200–1000 MPa，单螺栓预紧力 20000–60000 N，内压 2–10 MPa，预紧散布 0–0.15。暂时不引入偏心、外部轴向载荷、温度和螺纹细节。

分析步为：Step 1 施加 8 个螺栓预紧；Step 2 锁定预紧长度并允许接触重分布；Step 3 施加内压。最终在 Step 3 末帧提取垫片接触压力 CPRESS。

最重要输出是：p_min_gasket_eff，即垫片有效密封区域 CPRESS 的面积加权 5% 分位数；p_req_seal = 5 + 1.5 × internal_pressure；seal_margin = p_min_gasket_eff - p_req_seal；seal_pass = seal_margin >= 0。此外请输出 contact_uniformity_index、contact_area_ratio、flange_opening_max 和 8 个螺栓残余力。
```

---

## 19. 最终建议

当前阶段不要直接追求复杂工业法兰全变量建模。建议先固定一个小型、清晰、可批量的液体静压密封场景，用 8 个试跑 case 验证 Abaqus 链路，再扩展到 48 条 pilot FEA，最后通过 12 个物理子域内的 LHS 采样得到 300–420 条正式高保真样本，并用 near-threshold 补样扩展到 360–460 条。

这套设计能够同时满足：

```text
1. FEA 同门知道具体怎么建模；
2. 输入变量数量受控；
3. 输出标签清晰；
4. 后续可以与低保真 synthetic universe 对齐；
5. 可以支撑 PIOT-EASS 的 high-fidelity target domain；
6. 可以支撑 TabPFN-2.5 小样本适配实验。
```
