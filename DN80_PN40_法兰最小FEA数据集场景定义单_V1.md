# DN80 PN40 多螺栓法兰连接最小 FEA 数据集场景定义单 V1

## 0. 文档目的

本文档用于**直接指导 Abaqus / ANSYS 建立第一版高保真有限元模型，并生成 24 个 case 的最小数据集**。

本文档的目标不是给出论文写作层面的概念说明，而是给出一套可以直接执行的仿真定义：

1. 固定一个唯一母场景；
2. 明确所有几何、材料、接触、边界条件、载荷顺序与输出定义；
3. 明确量纲与字段命名；
4. 明确 24 个 case 的逐条输入定义；
5. 消除“法兰型号、垫片类别、内压加载方式、预紧散布如何施加、标签怎么提取”这些模糊项。

---

## 1. 本 V1 数据集的唯一母场景

### 1.1 场景名称

**DN80 PN40 8 螺栓突面法兰连接，在常温内压条件下的密封性能最小数据集**

### 1.2 建模对象

- 上法兰 1 件
- 下法兰 1 件
- 中间环形垫片 1 件
- 8 根螺柱 + 两端简化螺母/承压端面

### 1.3 V1 的仿真目标

在固定母场景下，预测并提取：

- `p_min_gasket`
- `seal_margin`
- `seal_pass`
- `contact_uniformity_index`
- `contact_area_ratio`
- `flange_opening_max`
- `preload_actual_mean`
- `preload_actual_std`

### 1.4 V1 的建模原则

- 使用**全 360° 三维模型**，不使用轴对称模型；
- 不建螺纹；
- 不建塑性；
- 不建热载荷；
- 不建外部轴向载荷；
- 不建偏心载荷；
- 不建摩擦散布；
- 螺栓预紧采用**预紧力控制**，不采用扭矩控制；
- 垫片采用**等效线弹性实体模型**；
- 所有 24 个 case 使用**同一建模逻辑与同一后处理逻辑**。

---

## 2. 单位与坐标系

## 2.1 统一单位（必须统一）

本数据集全部采用下列单位：

- 长度：`mm`
- 力：`N`
- 应力 / 压力 / 弹性模量：`MPa`
- 温度：`°C`
- 质量：本数据集不需要
- 时间：静力分析，不作为主字段
- 摩擦系数、比例量：`dimensionless`

**换算规则：**

- `1 MPa = 1 N/mm^2`
- 因此内部压强 `internal_pressure` 直接可与几何面积（`mm^2`）相乘得到力（`N`）

## 2.2 坐标系定义

建立全局直角坐标系：

- `Z`：法兰轴线方向，向上为正
- `X-Y`：法兰截面平面
- 原点：两法兰中心轴与垫片中面交点

约定：

- 下法兰位于 `Z < 0`
- 上法兰位于 `Z > 0`
- 垫片中心面位于 `Z = 0`

---

## 3. 几何定义（母场景固定）

## 3.1 法兰几何来源与 V1 使用方式

V1 母场景采用 **EN 1092-1 Type 11, DN80, PN40** 的几何主尺寸作为标准基础；但为了更适合批量 FEA 数据集生成，允许在不改变基本连接拓扑的前提下做**有限建模简化**。

### 3.1.1 法兰主尺寸（固定）

| 字段名 | 数值 | 单位 | 说明 |
|---|---:|---|---|
| `flange_standard` | EN1092-1 Type11 DN80 PN40 | / | 母场景标识 |
| `flange_outer_diameter` | 200.0 | mm | 法兰外径 |
| `bolt_circle_diameter` | 160.0 | mm | 螺栓中心圆直径 |
| `bolt_hole_diameter` | 18.0 | mm | 螺栓孔径 |
| `bolt_num` | 8 | / | 螺栓数量 |
| `raised_face_outer_diameter` | 138.0 | mm | 突面外径 |
| `raised_face_height` | 3.0 | mm | 突面高度 |
| `hub_large_outer_diameter` | 105.0 | mm | 颈根部外径 |
| `weld_end_outer_diameter` | 88.9 | mm | 焊端外径 |
| `pipe_wall_thickness` | 3.2 | mm | 与焊端相配的壁厚 |
| `pipe_inner_diameter` | 82.5 | mm | `88.9 - 2×3.2` |

### 3.1.2 法兰可变尺寸（DOE 主变量）

| 字段名 | 范围 | 单位 | 说明 |
|---|---:|---|---|
| `flange_thickness` | 22.0 – 30.0 | mm | 指法兰盘主体厚度，不含垫片、不含螺母 |

### 3.1.3 法兰轴向建模定义（固定）

每个法兰由 3 段组成：

1. **法兰盘主体**：厚度 = `flange_thickness`，外径 = 200 mm；
2. **突面（RF）**：位于内侧密封面，厚度 = 3 mm，外径 = 138 mm；
3. **颈部 + 直管段**：
   - 从法兰背面起，先用一段线性锥台把外径从 105 mm 过渡到 88.9 mm；
   - 锥台长度固定为 34 mm；
   - 再接一段直管，长度固定为 50 mm，外径 88.9 mm，内径 82.5 mm。

### 3.1.4 中心通孔 / 流道定义（固定）

- 法兰内部流道直径：`82.5 mm`
- 该通孔贯穿直管段、颈部和法兰盘
- 突面内侧仍保留至垫片内径的受压台阶区域

---

## 3.2 垫片几何定义（V1 明确定义）

V1 选择**柔性石墨类非金属垫片的等效实体建模**。为了避免标准目录尺寸与 raised face 边缘产生 overhang/欠覆盖争议，**本 V1 不直接照搬商品目录外径，而是定义一条明确的“有效环形垫片几何”**。

### 3.2.1 垫片固定平面尺寸

| 字段名 | 数值 | 单位 | 说明 |
|---|---:|---|---|
| `gasket_inner_diameter` | 90.0 | mm | V1 统一固定 |
| `gasket_outer_diameter` | 136.0 | mm | 小于 RF 外径 138，避免边缘悬出 |

### 3.2.2 垫片可变尺寸

| 字段名 | 范围 | 单位 | 说明 |
|---|---:|---|---|
| `gasket_thickness` | 1.50 – 3.00 | mm | 主 DOE 变量 |

### 3.2.3 垫片位置

- 垫片置于上下两个 RF 面之间；
- 垫片上表面与上法兰 RF 面接触；
- 垫片下表面与下法兰 RF 面接触；
- 垫片与法兰同轴。

---

## 3.3 螺柱/螺母几何定义（V1 简化实体方案）

V1 采用**无螺纹简化实体螺柱**，用预紧截面施加目标预紧力。

### 3.3.1 固定螺栓规格

| 字段名 | 数值 | 单位 | 说明 |
|---|---:|---|---|
| `bolt_nominal_size` | M16 | / | 母场景固定 |
| `bolt_shank_diameter` | 16.0 | mm | 简化为光杆圆柱 |
| `bolt_count` | 8 | / | 与法兰孔数一致 |
| `bolt_circle_diameter` | 160.0 | mm | 与法兰一致 |
| `nut_bearing_diameter` | 24.0 | mm | 简化螺母承压外径 |
| `nut_height` | 13.0 | mm | 简化螺母高度 |
| `stud_total_length` | 100.0 | mm | 对所有 case 固定 |

### 3.3.2 螺栓布置角度

8 根螺栓按如下角度分布：

- Bolt 1: `0°`
- Bolt 2: `45°`
- Bolt 3: `90°`
- Bolt 4: `135°`
- Bolt 5: `180°`
- Bolt 6: `225°`
- Bolt 7: `270°`
- Bolt 8: `315°`

### 3.3.3 螺栓孔关系

- 螺栓孔直径 18 mm；
- 光杆直径 16 mm；
- 孔与杆之间保留径向间隙 1 mm；
- **不建立杆-孔接触**，避免不必要的横向接触非线性；
- 螺栓载荷只通过上下承压端面传入法兰。

### 3.3.4 预紧截面

每根螺柱中部设置一个 pretension section：

- Abaqus：使用 *Bolt Load / Pretension Section*
- ANSYS：使用 Bolt Pretension

预紧力由 `target_preload_per_bolt` 决定。

---

## 4. 材料定义（全部明确）

## 4.1 法兰材料

| 字段名 | 数值 | 单位 |
|---|---:|---|
| `E_flange` | 210000 | MPa |
| `nu_flange` | 0.30 | / |
| `material_flange` | linear elastic steel | / |

## 4.2 螺柱材料

| 字段名 | 数值 | 单位 |
|---|---:|---|
| `bolt_strength_class` | 8.8 | / |
| `E_bolt` | 210000 | MPa |
| `nu_bolt` | 0.30 | / |
| `material_bolt` | linear elastic steel | / |

**说明：**
V1 不考虑螺栓塑性屈服；所有 case 仅在弹性范围内分析。

## 4.3 垫片材料（V1 等效模型）

| 字段名 | 范围 | 单位 | 说明 |
|---|---:|---|---|
| `E_gasket_eq` | 250 – 1100 | MPa | 主 DOE 变量 |
| `nu_gasket` | 0.15 | / | 固定 |
| `material_gasket` | linear elastic equivalent gasket | / | 固定建模方式 |

**硬性规定：**

- V1 垫片必须建成**三维实体**；
- 不允许在不同 case 中切换不同本构形式；
- V1 只允许 `E_gasket_eq` 变化，不允许再引入非线性压缩曲线、损伤、蠕变等复杂行为。

---

## 5. 接触定义（全部明确）

## 5.1 需要建立的接触对

仅建立以下接触：

1. 上法兰 RF 面 ↔ 垫片上表面
2. 下法兰 RF 面 ↔ 垫片下表面
3. 上螺母承压面 ↔ 上法兰背面
4. 下螺母承压面 ↔ 下法兰背面

## 5.2 不建立的接触

以下接触**不建立**：

- 螺纹接触
- 杆-孔接触
- 上下法兰外侧面之间的接触
- 法兰与环境的其他接触

## 5.3 接触法向行为

所有接触对统一采用：

- `normal_behavior = hard contact`
- 允许分离
- 不允许穿透

## 5.4 接触切向行为

V1 统一采用：

| 接触位置 | 摩擦系数 |
|---|---:|
| 法兰-RF / 垫片 | 0.15 |
| 螺母承压面 / 法兰背面 | 0.15 |

### 5.4.1 固定摩擦参数

| 字段名 | 数值 |
|---|---:|
| `mu_gasket_face` | 0.15 |
| `mu_bearing` | 0.15 |
| `mu_thread` | 不建线程，因此不用 |

---

## 6. 网格与单元建议（可直接执行）

## 6.1 分析类型

- `Static, General`（Abaqus）
- `Static Structural`（ANSYS）
- 打开几何非线性：`NLGEOM = ON`

## 6.2 推荐单元

### Abaqus

- 法兰 / 螺柱 / 螺母 / 垫片：`C3D8R`
- 若局部扫掠困难，可局部允许 `C3D10`

### ANSYS

- 法兰 / 螺柱 / 螺母 / 垫片：`SOLID185` 或 `SOLID186`

## 6.3 推荐网格尺度

| 区域 | 目标单元尺寸 |
|---|---:|
| 法兰主体远离接触区 | 4.0 mm |
| RF 接触区 | 1.5 mm |
| 螺栓孔周围 | 1.5 mm |
| 螺母承压面附近 | 1.5 mm |
| 垫片面内 | 2.0 mm |
| 垫片厚度方向 | 最少 3 层单元 |

### 6.3.1 垫片厚度方向单元数

- 当 `gasket_thickness = 1.50 ~ 1.99 mm`：厚度方向 3 层
- 当 `gasket_thickness = 2.00 ~ 3.00 mm`：厚度方向 4 层

## 6.4 网格一致性规则

- 24 个 case 必须使用同一套分区逻辑；
- 只允许随几何变化自动重划分，不允许换不同建模拓扑；
- 不允许部分 case 用 hexa、部分 case 用 shell 或 connector 混合替代。

---

## 7. 约束与边界条件（全部明确）

## 7.1 管端耦合参考点

在上下两个直管切口面分别建立参考点：

- `RP_bottom`
- `RP_top`

并将对应端面与参考点做**分布耦合**（仅平动 DOF）。

## 7.2 底端约束

在 `RP_bottom` 上施加：

- `Ux = 0`
- `Uy = 0`
- `Uz = 0`

## 7.3 顶端约束

在 `RP_top` 上施加：

- `Ux = 0`
- `Uy = 0`
- `Uz` 自由

说明：

- 该设置允许上端在轴向响应内压分离趋势；
- 同时去除刚体平动自由度；
- 本 V1 不引入额外弯矩或横向载荷。

---

## 8. 载荷定义（必须严格统一）

## 8.1 载荷步顺序

### Step-0：Initial

- 建立接触
- 施加边界条件
- 不施加载荷

### Step-1：Pretension Apply

- 对 8 根螺柱施加目标预紧力
- 本步只施加螺栓预紧，不加内压

### Step-2：Pretension Lock

- 锁定 pretension section
- 使系统在预紧状态下达到平衡

### Step-3：Pressure Service

- 保持预紧锁定
- 施加内部压力 `internal_pressure`
- 同时施加等效端盖分离力 `F_end_equiv`

所有输出均以 **Step-3 末状态** 为准。

---

## 8.2 内压加载面定义

内部压力 `internal_pressure` 施加在所有**流体实际接触的内表面**上，包括：

1. 上、下直管内壁；
2. 颈部内壁；
3. 法兰内孔内壁；
4. 到达垫片内径 `90 mm` 以内的内侧台阶受压面。

## 8.3 等效端盖分离力

为了正确反映内压导致的法兰分离效应，除内壁压力外，必须额外施加一个**轴向等效端盖分离力**：

\[
F_{end\_equiv} = p \cdot \frac{\pi d_{eff}^2}{4}
\]

其中：

- `p = internal_pressure`，单位 `MPa = N/mm^2`
- `d_eff = gasket_inner_diameter = 90 mm`

因此：

\[
F_{end\_equiv} = p \cdot \frac{\pi \times 90^2}{4}
\]

该轴向力施加在 `RP_top` 上，方向为 `+Z`。

**统一规定：**

- 所有 case 一律按上式计算；
- 不允许有的 case 只加压力不加端盖效应；
- 不允许有的 case 采用封头、有的 case 采用等效力；
- 整个 24 case 数据集必须保持加载逻辑一致。

---

## 9. 预紧子集定义（S0 / S1）

## 9.1 子集一：`S0_uniform`

定义：8 根螺柱预紧力完全一致。

若该 case 的目标预紧力为 `F0 = target_preload_per_bolt`，则：

- `F1 = F2 = ... = F8 = F0`

## 9.2 子集二：`S1_scattered`

定义：8 根螺柱存在固定的、可复现的 10% 散布。

固定散布率：

- `preload_scatter_ratio = 0.10`

8 根螺柱预紧力定义为：

- `F1 = 1.10 F0`
- `F2 = 0.90 F0`
- `F3 = 1.05 F0`
- `F4 = 0.95 F0`
- `F5 = 1.075 F0`
- `F6 = 0.925 F0`
- `F7 = 1.025 F0`
- `F8 = 0.975 F0`

说明：

- 平均值约等于 `F0`
- 环向不均匀性固定可复现
- 所有散布 case 均使用完全相同的倍率模板

---

## 10. 标签输出定义（必须按本定义提取）

## 10.1 输出总原则

- 所有输出都来自 **Step-3 末帧**；
- 所有输出都必须写入统一表；
- 不允许只保留云图、不导出数值。

---

## 10.2 角向分段规则（用于接触压力后处理）

为避免单个节点极值噪声，垫片接触压力后处理统一采用**72 个等角扇区**（每区 5°）。

### 10.2.1 具体做法

将 `0°~360°` 按 5° 一段切分，共 72 段。

对每个扇区 `k`：

1. 计算上界面该扇区的面积加权平均接触压力 `p_upper(k)`；
2. 计算下界面该扇区的面积加权平均接触压力 `p_lower(k)`；
3. 定义该扇区密封压力：

\[
p_{sector}(k) = \min\left(p_{upper}(k),\ p_{lower}(k)\right)
\]

如果该扇区某一界面发生分离，则该界面接触压力按 `0` 处理。

---

## 10.3 主输出字段

### 10.3.1 `p_min_gasket`

定义：

\[
p_{min\_gasket} = \min_{k=1,...,72} p_{sector}(k)
\]

单位：`MPa`

### 10.3.2 `p_req_seal`

V1 统一固定为：

- `p_req_seal = 20.0 MPa`

说明：

- 这是本最小数据集的**任务阈值定义**；
- 不是材料本构参数；
- 目的是让 `seal_margin` 和 `seal_pass` 可直接计算且全数据集一致。

### 10.3.3 `seal_margin`

定义：

\[
seal\_margin = p_{min\_gasket} - p_{req\_seal}
\]

单位：`MPa`

### 10.3.4 `seal_pass`

定义：

- 若 `seal_margin >= 0`，则 `seal_pass = 1`
- 若 `seal_margin < 0`，则 `seal_pass = 0`

---

## 10.4 辅助输出字段

### 10.4.1 `contact_uniformity_index`

对 72 个 `p_sector(k)` 求分布：

\[
contact\_uniformity\_index = \frac{P05(p_{sector})}{P50(p_{sector})}
\]

单位：无量纲

### 10.4.2 `contact_area_ratio`

定义：

- 上界面接触面积比：`A_upper_contact / A_upper_total`
- 下界面接触面积比：`A_lower_contact / A_lower_total`

最终报告：

\[
contact\_area\_ratio = \min\left(\frac{A_{upper\_contact}}{A_{upper\_total}},\ \frac{A_{lower\_contact}}{A_{lower\_total}}\right)
\]

其中：

- 面单元接触压力 `> 0` 视为接触；
- 单位：无量纲。

### 10.4.3 `flange_opening_max`

在 RF 密封带对应半径范围内，提取上下法兰对应点在 `Z` 向的相对分离量：

\[
opening(r,\theta) = U_z^{upper}(r,\theta) - U_z^{lower}(r,\theta)
\]

只统计正分离量，定义：

\[
flange\_opening\_max = \max(opening, 0)
\]

单位：`mm`

### 10.4.4 `preload_actual_mean`

提取 Step-3 末帧 8 根螺柱的实际轴向拉力 `N_i`，定义：

\[
preload\_actual\_mean = \frac{1}{8} \sum_{i=1}^{8} N_i
\]

单位：`N`

### 10.4.5 `preload_actual_std`

定义：

\[
preload\_actual\_std = std(N_1,...,N_8)
\]

单位：`N`

---

## 11. 本 V1 数据集的输入字段定义

## 11.1 固定输入字段（所有 case 相同）

| 字段名 | 数值 | 单位 |
|---|---:|---|
| `flange_standard` | EN1092-1_Type11_DN80_PN40 | / |
| `flange_outer_diameter` | 200.0 | mm |
| `bolt_circle_diameter` | 160.0 | mm |
| `bolt_hole_diameter` | 18.0 | mm |
| `bolt_num` | 8 | / |
| `bolt_nominal_size` | M16 | / |
| `bolt_shank_diameter` | 16.0 | mm |
| `bolt_strength_class` | 8.8 | / |
| `raised_face_outer_diameter` | 138.0 | mm |
| `raised_face_height` | 3.0 | mm |
| `hub_large_outer_diameter` | 105.0 | mm |
| `weld_end_outer_diameter` | 88.9 | mm |
| `pipe_wall_thickness` | 3.2 | mm |
| `pipe_inner_diameter` | 82.5 | mm |
| `straight_pipe_stub_length` | 50.0 | mm |
| `neck_transition_length` | 34.0 | mm |
| `gasket_inner_diameter` | 90.0 | mm |
| `gasket_outer_diameter` | 136.0 | mm |
| `E_flange` | 210000 | MPa |
| `nu_flange` | 0.30 | / |
| `E_bolt` | 210000 | MPa |
| `nu_bolt` | 0.30 | / |
| `nu_gasket` | 0.15 | / |
| `mu_gasket_face` | 0.15 | / |
| `mu_bearing` | 0.15 | / |
| `temperature_delta` | 0.0 | °C |
| `external_axial_load_eq` | 0.0 | N |
| `load_eccentricity_a` | 0.0 | mm |
| `p_req_seal` | 20.0 | MPa |

## 11.2 DOE 主变量字段

| 字段名 | 单位 |
|---|---|
| `flange_thickness` | mm |
| `gasket_thickness` | mm |
| `E_gasket_eq` | MPa |
| `target_preload_per_bolt` | N |
| `internal_pressure` | MPa |

## 11.3 子集字段

| 字段名 | 类型 |
|---|---|
| `subset` | string |
| `preload_scatter_ratio` | float |
| `preload_pattern_id` | string |

---

## 12. 12 个 base point（连续变量）

| base_id | flange_thickness (mm) | gasket_thickness (mm) | E_gasket_eq (MPa) | target_preload_per_bolt (N) | internal_pressure (MPa) | F_end_equiv (N) |
|---|---:|---:|---:|---:|---:|---:|
| B01 | 28.9 | 2.84 | 583 | 46275 | 3.77 | 23984 |
| B02 | 22.5 | 2.43 | 1039 | 59024 | 1.82 | 11578 |
| B03 | 26.0 | 2.27 | 423 | 49725 | 2.86 | 18195 |
| B04 | 24.7 | 2.11 | 266 | 55385 | 2.14 | 13614 |
| B05 | 27.4 | 2.51 | 734 | 54173 | 3.24 | 20612 |
| B06 | 28.3 | 1.58 | 844 | 52932 | 1.01 | 6425 |
| B07 | 27.2 | 2.22 | 908 | 51256 | 3.06 | 19467 |
| B08 | 23.9 | 1.72 | 368 | 48275 | 1.24 | 7889 |
| B09 | 24.5 | 2.64 | 521 | 43114 | 1.44 | 9161 |
| B10 | 30.0 | 1.79 | 1007 | 57728 | 1.91 | 12151 |
| B11 | 23.0 | 2.00 | 803 | 61014 | 3.60 | 22902 |
| B12 | 26.5 | 2.97 | 626 | 44452 | 2.42 | 15395 |

---

## 13. 24 个正式 case 定义表

### 13.1 24 个 case 的唯一解释规则

- `C01, C03, ..., C23`：均为 `S0_uniform`
- `C02, C04, ..., C24`：均为 `S1_scattered`
- 每一对 `(C2n-1, C2n)` 共用同一个 `base_id`
- 差别仅在预紧模式不同

### 13.2 case 总表

| case_id | base_id | subset | preload_scatter_ratio | preload_pattern_id | flange_thickness (mm) | gasket_thickness (mm) | E_gasket_eq (MPa) | target_preload_per_bolt (N) | internal_pressure (MPa) | F_end_equiv (N) |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| C01 | B01 | S0_uniform | 0.00 | uniform | 28.9 | 2.84 | 583 | 46275 | 3.77 | 23984 |
| C02 | B01 | S1_scattered | 0.10 | scatter_r10_v1 | 28.9 | 2.84 | 583 | 46275 | 3.77 | 23984 |
| C03 | B02 | S0_uniform | 0.00 | uniform | 22.5 | 2.43 | 1039 | 59024 | 1.82 | 11578 |
| C04 | B02 | S1_scattered | 0.10 | scatter_r10_v1 | 22.5 | 2.43 | 1039 | 59024 | 1.82 | 11578 |
| C05 | B03 | S0_uniform | 0.00 | uniform | 26.0 | 2.27 | 423 | 49725 | 2.86 | 18195 |
| C06 | B03 | S1_scattered | 0.10 | scatter_r10_v1 | 26.0 | 2.27 | 423 | 49725 | 2.86 | 18195 |
| C07 | B04 | S0_uniform | 0.00 | uniform | 24.7 | 2.11 | 266 | 55385 | 2.14 | 13614 |
| C08 | B04 | S1_scattered | 0.10 | scatter_r10_v1 | 24.7 | 2.11 | 266 | 55385 | 2.14 | 13614 |
| C09 | B05 | S0_uniform | 0.00 | uniform | 27.4 | 2.51 | 734 | 54173 | 3.24 | 20612 |
| C10 | B05 | S1_scattered | 0.10 | scatter_r10_v1 | 27.4 | 2.51 | 734 | 54173 | 3.24 | 20612 |
| C11 | B06 | S0_uniform | 0.00 | uniform | 28.3 | 1.58 | 844 | 52932 | 1.01 | 6425 |
| C12 | B06 | S1_scattered | 0.10 | scatter_r10_v1 | 28.3 | 1.58 | 844 | 52932 | 1.01 | 6425 |
| C13 | B07 | S0_uniform | 0.00 | uniform | 27.2 | 2.22 | 908 | 51256 | 3.06 | 19467 |
| C14 | B07 | S1_scattered | 0.10 | scatter_r10_v1 | 27.2 | 2.22 | 908 | 51256 | 3.06 | 19467 |
| C15 | B08 | S0_uniform | 0.00 | uniform | 23.9 | 1.72 | 368 | 48275 | 1.24 | 7889 |
| C16 | B08 | S1_scattered | 0.10 | scatter_r10_v1 | 23.9 | 1.72 | 368 | 48275 | 1.24 | 7889 |
| C17 | B09 | S0_uniform | 0.00 | uniform | 24.5 | 2.64 | 521 | 43114 | 1.44 | 9161 |
| C18 | B09 | S1_scattered | 0.10 | scatter_r10_v1 | 24.5 | 2.64 | 521 | 43114 | 1.44 | 9161 |
| C19 | B10 | S0_uniform | 0.00 | uniform | 30.0 | 1.79 | 1007 | 57728 | 1.91 | 12151 |
| C20 | B10 | S1_scattered | 0.10 | scatter_r10_v1 | 30.0 | 1.79 | 1007 | 57728 | 1.91 | 12151 |
| C21 | B11 | S0_uniform | 0.00 | uniform | 23.0 | 2.00 | 803 | 61014 | 3.60 | 22902 |
| C22 | B11 | S1_scattered | 0.10 | scatter_r10_v1 | 23.0 | 2.00 | 803 | 61014 | 3.60 | 22902 |
| C23 | B12 | S0_uniform | 0.00 | uniform | 26.5 | 2.97 | 626 | 44452 | 2.42 | 15395 |
| C24 | B12 | S1_scattered | 0.10 | scatter_r10_v1 | 26.5 | 2.97 | 626 | 44452 | 2.42 | 15395 |

---

## 14. 12 个 scattered case 的 8 根螺柱具体预紧力

以下表格把 `S1_scattered` 的 8 根螺柱具体预紧值全部展开，避免执行时再做二次解释。

| base_id | F0 | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B01 | 46275 | 50903 | 41648 | 48589 | 43961 | 49746 | 42804 | 47432 | 45118 |
| B02 | 59024 | 64926 | 53122 | 61975 | 56073 | 63451 | 54597 | 60500 | 57548 |
| B03 | 49725 | 54698 | 44752 | 52211 | 47239 | 53454 | 45996 | 50968 | 48482 |
| B04 | 55385 | 60924 | 49846 | 58154 | 52616 | 59539 | 51231 | 56770 | 54000 |
| B05 | 54173 | 59590 | 48756 | 56882 | 51464 | 58236 | 50110 | 55527 | 52819 |
| B06 | 52932 | 58225 | 47639 | 55579 | 50285 | 56902 | 48962 | 54255 | 51609 |
| B07 | 51256 | 56382 | 46130 | 53819 | 48693 | 55100 | 47412 | 52537 | 49975 |
| B08 | 48275 | 53103 | 43448 | 50689 | 45861 | 51896 | 44654 | 49482 | 47068 |
| B09 | 43114 | 47425 | 38803 | 45270 | 40958 | 46348 | 39880 | 44192 | 42036 |
| B10 | 57728 | 63501 | 51955 | 60614 | 54842 | 62058 | 53398 | 59171 | 56285 |
| B11 | 61014 | 67115 | 54913 | 64065 | 57963 | 65590 | 56438 | 62539 | 59489 |
| B12 | 44452 | 48897 | 40007 | 46675 | 42229 | 47786 | 41118 | 45563 | 43341 |

其中：

- `C02` 使用 `B01` 行；
- `C04` 使用 `B02` 行；
- ...
- `C24` 使用 `B12` 行。

---

## 15. 建议输出文件格式（直接用于数据集）

## 15.1 `hf_case_inputs.csv`

每行一个 case，至少包含：

- `case_id`
- `base_id`
- `subset`
- 全部固定字段
- 全部 DOE 字段
- `preload_scatter_ratio`
- `preload_pattern_id`
- `F_end_equiv`

## 15.2 `hf_case_outputs.csv`

每行一个 case，至少包含：

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

## 15.3 `hf_case_sector_pressures.csv`

建议额外保留每个 case 的 72 扇区压力：

- `case_id`
- `sector_id`
- `theta_start_deg`
- `theta_end_deg`
- `p_upper_sector`
- `p_lower_sector`
- `p_sector`

这样后续可以直接用于：

- `p_min_gasket` 复核
- `contact_uniformity_index` 复核
- 环向不均匀可视化
- 散布效应分析

---

## 16. 执行优先级（真正开始干时的顺序）

1. 先建立中心 case：`C01`
2. 检查接触、预紧、内压和端盖力是否工作正常
3. 检查 72 扇区后处理脚本是否正确
4. 再跑 `C02`，确认同 base point 下散布引起的物理差异存在
5. 若 `C01/C02` 成功，再批量跑 `C03-C24`

---

## 17. 一句话总结

本 V1 场景定义单的本质是：

> **用一个唯一固定的 DN80 PN40 8 螺栓突面法兰母场景，配合 5 个主 DOE 连续变量、2 个预紧子集、统一的压力-端盖力-预紧-接触-后处理规则，稳定产出 24 个可直接组成最小高保真数据集的 FEA case。**
