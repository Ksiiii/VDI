# EN 1092-1 Type 11 DN80 PN40 法兰最小 FEA 数据集  
## 标准变量对照表 + 24 个 case 输入表（重写版）

## 1. 使用原则
本版本只做三件事：

1. **法兰几何变量**只使用 **EN 1092-1 Type 11** 的标准尺寸符号；
2. **垫片几何变量**单独列出，按 **EN 1514-1 Form IBC** 处理；
3. **仿真工况变量**与**标准几何变量**分开，不再混写。

---

## 2. 法兰标准几何变量（固定，不进入 24 case DOE）

### 2.1 标准来源
母场景采用 **EN 1092-1 Type 11, DN80, PN40**。  
对 DN80 PN40，该尺寸表给出如下标准几何量：

| 标准符号 | 建议字段名 | 含义 | 数值 | 单位 |
|---|---|---|---:|---|
| A | A_flange_outer_diameter_mm | 法兰外径 | 200.0 | mm |
| B | B_bolt_circle_diameter_mm | 螺栓孔中心圆直径 | 160.0 | mm |
| C | C_raised_face_outer_diameter_mm | 突面外径 | 138.0 | mm |
| D | D_pipe_wall_thickness_mm | 管壁厚 | 3.2 | mm |
| E | E_weld_end_outer_diameter_mm | 焊端/小端外径 | 88.9 | mm |
| F | F_neck_large_outer_diameter_mm | 颈部大端外径 | 105.0 | mm |
| G | G_bolt_hole_diameter_mm | 螺栓孔径 | 18.0 | mm |
| H | H_raised_face_height_mm | 突面高度 | 3.0 | mm |
| K | K_flange_thickness_mm | 法兰盘厚度 | 24.0 | mm |
| M | M_flange_axial_length_mm | 法兰轴向总长度 | 58.0 | mm |
| N | N_right_end_length_mm | 右端直边长度 | 12.0 | mm |
| R | R_fillet_radius_mm | 过渡圆角半径 | 8.0 | mm |

### 2.2 紧固件固定量
| 字段名 | 含义 | 数值 |
|---|---|---|
| bolt_num | 螺栓数量 | 8 |
| bolt_size | 螺栓规格 | M16 |
| bolt_strength_class | 螺柱性能等级 | 8.8 |
| bolt_hole_num | 螺栓孔数量 | 8 |

### 2.3 派生几何量（由标准几何算出）
| 字段名 | 含义 | 计算式 | 数值 | 单位 |
|---|---|---|---:|---|
| pipe_inner_diameter_mm | 管内径 | E - 2D | 82.5 | mm |
| pipe_outer_diameter_mm | 管外径 | E | 88.9 | mm |
| raised_face_inner_diameter_mm | 突面内径 | 取与管外径一致 | 88.9 | mm |

---

## 3. 垫片标准变量（固定几何，厚度与刚度进入 DOE）

### 3.1 垫片形式
母场景垫片采用 **EN 1514-1 Form IBC**（适用于 raised-face/flat-face flange 的环形垫片）。

### 3.2 DN80 PN40 参考几何
为保持与 EN 1092-1 DN80 PN40 raised-face 场景一致，采用：

| 字段名 | 含义 | 数值 | 单位 |
|---|---|---:|---|
| gasket_standard | 垫片标准 | EN 1514-1 Form IBC | / |
| gasket_nominal_size | 公称规格 | DN80 PN40 | / |
| gasket_inner_diameter_mm | 垫片内径 | 89.0 | mm |
| gasket_outer_diameter_mm | 垫片外径 | 142.0 | mm |

### 3.3 垫片 DOE 变量
| 字段名 | 含义 | 单位 |
|---|---|---|
| gasket_thickness_mm | 垫片厚度 | mm |
| E_gasket_eq_MPa | 垫片等效压缩模量 | MPa |

---

## 4. 固定仿真输入（所有 case 相同）

| 字段名 | 数值 | 单位 | 说明 |
|---|---:|---|---|
| material_flange_E_MPa | 210000 | MPa | 法兰弹性模量 |
| material_flange_nu | 0.30 | / | 法兰泊松比 |
| material_bolt_E_MPa | 210000 | MPa | 螺柱弹性模量 |
| material_bolt_nu | 0.30 | / | 螺柱泊松比 |
| temperature_delta_C | 0.0 | °C | 本批次不考虑温差 |
| external_axial_load_eq_N | 0.0 | N | 本批次不引入外部轴向载荷 |
| load_eccentricity_a_mm | 0.0 | mm | 本批次不引入偏心 |
| mu_thread | 0.14 | / | 螺纹摩擦系数，先固定 |
| mu_bearing | 0.14 | / | 支承面摩擦系数，先固定 |
| p_req_seal_MPa | 5.0 | MPa | 先作为统一阈值固定，用于生成 seal_margin / seal_pass |

---

## 5. 24 个 case 真正变化的 DOE 输入

### 5.1 五个 DOE 主变量
| 字段名 | 含义 | 范围 | 单位 |
|---|---|---|---|
| K_flange_thickness_case_mm | 法兰厚度（对 K 的 DOE 扰动） | 20.0 – 32.0 | mm |
| gasket_thickness_mm | 垫片厚度 | 1.5 – 3.0 | mm |
| E_gasket_eq_MPa | 垫片等效压缩模量 | 200 – 1200 | MPa |
| target_preload_per_bolt_N | 单螺柱目标预紧力 | 35000 – 65000 | N |
| internal_pressure_MPa | 内压 | 0.5 – 4.0 | MPa |

### 5.2 subset 因素
| subset | preload_scatter_ratio | 含义 |
|---|---:|---|
| S0_uniform | 0.00 | 8 根螺柱预紧一致 |
| S1_scattered | 0.10 | 8 根螺柱按固定模板做 ±10% 非均匀预紧 |

---

## 6. 预紧散布定义（S1_scattered）

设目标预紧力为 `F0 = target_preload_per_bolt_N`，则 8 根螺柱的施加值固定为：

- Bolt1 = F0 × (1 + 1.00×0.10) = 1.10 F0
- Bolt2 = F0 × (1 - 1.00×0.10) = 0.90 F0
- Bolt3 = F0 × (1 + 0.50×0.10) = 1.05 F0
- Bolt4 = F0 × (1 - 0.50×0.10) = 0.95 F0
- Bolt5 = F0 × (1 + 0.75×0.10) = 1.075 F0
- Bolt6 = F0 × (1 - 0.75×0.10) = 0.925 F0
- Bolt7 = F0 × (1 + 0.25×0.10) = 1.025 F0
- Bolt8 = F0 × (1 - 0.25×0.10) = 0.975 F0

---

## 7. 12 个 base point（连续变量）

| base_id | K_flange_thickness_case_mm | gasket_thickness_mm | E_gasket_eq_MPa | target_preload_per_bolt_N | internal_pressure_MPa |
|---|---:|---:|---:|---:|---:|
| B01 | 27.1 | 2.48 | 770 | 36712 | 3.82 |
| B02 | 25.7 | 1.99 | 264 | 48289 | 1.01 |
| B03 | 31.5 | 1.77 | 565 | 43073 | 1.77 |
| B04 | 22.3 | 2.94 | 1092 | 57357 | 1.25 |
| B05 | 24.7 | 1.59 | 654 | 59691 | 2.33 |
| B06 | 29.0 | 2.84 | 797 | 64139 | 0.86 |
| B07 | 21.0 | 2.73 | 1174 | 39607 | 3.63 |
| B08 | 26.9 | 2.14 | 522 | 45080 | 1.92 |
| B09 | 30.2 | 2.04 | 896 | 41940 | 3.11 |
| B10 | 23.2 | 2.58 | 438 | 53027 | 2.67 |
| B11 | 28.4 | 1.67 | 1006 | 60787 | 3.44 |
| B12 | 20.6 | 2.26 | 365 | 50669 | 2.37 |

---

## 8. 24 个正式 case 输入表

| case_id | base_id | subset | preload_scatter_ratio | K_flange_thickness_case_mm | gasket_thickness_mm | E_gasket_eq_MPa | target_preload_per_bolt_N | internal_pressure_MPa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| C01 | B01 | S0_uniform | 0.00 | 27.1 | 2.48 | 770 | 36712 | 3.82 |
| C02 | B01 | S1_scattered | 0.10 | 27.1 | 2.48 | 770 | 36712 | 3.82 |
| C03 | B02 | S0_uniform | 0.00 | 25.7 | 1.99 | 264 | 48289 | 1.01 |
| C04 | B02 | S1_scattered | 0.10 | 25.7 | 1.99 | 264 | 48289 | 1.01 |
| C05 | B03 | S0_uniform | 0.00 | 31.5 | 1.77 | 565 | 43073 | 1.77 |
| C06 | B03 | S1_scattered | 0.10 | 31.5 | 1.77 | 565 | 43073 | 1.77 |
| C07 | B04 | S0_uniform | 0.00 | 22.3 | 2.94 | 1092 | 57357 | 1.25 |
| C08 | B04 | S1_scattered | 0.10 | 22.3 | 2.94 | 1092 | 57357 | 1.25 |
| C09 | B05 | S0_uniform | 0.00 | 24.7 | 1.59 | 654 | 59691 | 2.33 |
| C10 | B05 | S1_scattered | 0.10 | 24.7 | 1.59 | 654 | 59691 | 2.33 |
| C11 | B06 | S0_uniform | 0.00 | 29.0 | 2.84 | 797 | 64139 | 0.86 |
| C12 | B06 | S1_scattered | 0.10 | 29.0 | 2.84 | 797 | 64139 | 0.86 |
| C13 | B07 | S0_uniform | 0.00 | 21.0 | 2.73 | 1174 | 39607 | 3.63 |
| C14 | B07 | S1_scattered | 0.10 | 21.0 | 2.73 | 1174 | 39607 | 3.63 |
| C15 | B08 | S0_uniform | 0.00 | 26.9 | 2.14 | 522 | 45080 | 1.92 |
| C16 | B08 | S1_scattered | 0.10 | 26.9 | 2.14 | 522 | 45080 | 1.92 |
| C17 | B09 | S0_uniform | 0.00 | 30.2 | 2.04 | 896 | 41940 | 3.11 |
| C18 | B09 | S1_scattered | 0.10 | 30.2 | 2.04 | 896 | 41940 | 3.11 |
| C19 | B10 | S0_uniform | 0.00 | 23.2 | 2.58 | 438 | 53027 | 2.67 |
| C20 | B10 | S1_scattered | 0.10 | 23.2 | 2.58 | 438 | 53027 | 2.67 |
| C21 | B11 | S0_uniform | 0.00 | 28.4 | 1.67 | 1006 | 60787 | 3.44 |
| C22 | B11 | S1_scattered | 0.10 | 28.4 | 1.67 | 1006 | 60787 | 3.44 |
| C23 | B12 | S0_uniform | 0.00 | 20.6 | 2.26 | 365 | 50669 | 2.37 |
| C24 | B12 | S1_scattered | 0.10 | 20.6 | 2.26 | 365 | 50669 | 2.37 |

---

## 9. 12 个 scattered case 的 8 根螺柱具体预紧力

### B01 / C02（F0 = 36712 N）
40383 / 33041 / 38548 / 34876 / 39465 / 33959 / 37630 / 35794 N

### B02 / C04（F0 = 48289 N）
53118 / 43460 / 50703 / 45875 / 51911 / 44667 / 49496 / 47082 N

### B03 / C06（F0 = 43073 N）
47380 / 38766 / 45227 / 40919 / 46303 / 39843 / 44150 / 41996 N

### B04 / C08（F0 = 57357 N）
63093 / 51621 / 60225 / 54489 / 61658 / 53056 / 58791 / 55923 N

### B05 / C10（F0 = 59691 N）
65660 / 53722 / 62676 / 56706 / 64168 / 55214 / 61183 / 58199 N

### B06 / C12（F0 = 64139 N）
70553 / 57725 / 67346 / 60932 / 68949 / 59329 / 65742 / 62536 N

### B07 / C14（F0 = 39607 N）
43568 / 35646 / 41587 / 37627 / 42578 / 36636 / 40597 / 38617 N

### B08 / C16（F0 = 45080 N）
49588 / 40572 / 47334 / 42826 / 48461 / 41699 / 46207 / 43953 N

### B09 / C18（F0 = 41940 N）
46134 / 37746 / 44037 / 39843 / 45085 / 38795 / 42988 / 40892 N

### B10 / C20（F0 = 53027 N）
58330 / 47724 / 55678 / 50376 / 57004 / 49050 / 54353 / 51701 N

### B11 / C22（F0 = 60787 N）
66866 / 54708 / 63826 / 57748 / 65346 / 56228 / 62307 / 59267 N

### B12 / C24（F0 = 50669 N）
55736 / 45602 / 53202 / 48136 / 54469 / 46869 / 51936 / 49402 N

---

## 10. 输出字段（统一命名）

| 字段名 | 单位 | 定义 |
|---|---|---|
| p_min_gasket_MPa | MPa | 垫片有效密封环上最小接触压力 |
| p_req_seal_MPa | MPa | 密封判定阈值，本版固定 5.0 MPa |
| seal_margin_MPa | MPa | p_min_gasket_MPa - p_req_seal_MPa |
| seal_pass | 0/1 | 若 seal_margin_MPa >= 0，则为 1 |
| contact_uniformity_index | / | 垫片有效接触区域压力 p05 / p50 |
| contact_area_ratio | / | 有效接触面积 / 垫片总面积 |
| flange_opening_max_mm | mm | 工作载荷后法兰密封面最大开口量 |
| preload_actual_mean_N | N | 最终 8 根螺柱轴力均值 |
| preload_actual_std_N | N | 最终 8 根螺柱轴力标准差 |

---

## 11. 你现在可以直接交给师兄的版本

一句话版本：

- 法兰几何：只按 **EN 1092-1 Type 11, DN80, PN40** 的 A/B/C/D/E/F/G/H/K/M/N/R 建模；
- 垫片几何：只按 **EN 1514-1 Form IBC, DN80 PN40** 的 `89 × 142 mm` 环形垫片建模；
- 24 个 case：只改变  
  `K_flange_thickness_case_mm`、`gasket_thickness_mm`、`E_gasket_eq_MPa`、`target_preload_per_bolt_N`、`internal_pressure_MPa`、`preload_scatter_ratio`；
- 其余全部固定。
