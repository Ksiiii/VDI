# -*- coding: utf-8 -*-
"""
VDI 2230-1 严格版数据集生成器（可复现脚本）
--------------------------------------------------
功能：
- 依据 VDI 2230 的核心计算链，生成“理想装配版”和“工艺扰动版”训练数据。
- 力矩-预紧力采用 R13/1 风格经验式（含 0.16/0.58、μ_G、μ_K、d2、Dk）。
- 被夹紧件回弹采用 5.1.2 的圆锥/截头圆锥近似（给出等效表达形式）。
- 预紧力损失与最小装配预紧力按 R4/R5 框架处理。
- 载荷分配 Φ 按 R3/3 思路：Φ = n·δP / (δS + n·δP)，本脚本默认同轴 n=1。
- 输出两套 CSV：严格版·理想、严格版·扰动。

注意：
1) 本脚本为工程实现，仍需要用少量实测/仿真作参数标定（μ_G, μ_K, ΔZ、扩散角等）。
2) 若需偏心/开口工况，应按 5.2.2/5.3.x 接入载荷系数 n 与上限曲线（留有扩展位）。

使用：
python vdi2230_generator_strict.py --ideal_rows 10000 --perturbed_rows 10000 --seed 123
"""
import argparse
import numpy as np
import pandas as pd

# ------------------------ 基本表/参数 ------------------------
THREAD_TABLE = pd.DataFrame([
    ("M6", 6.0, 1.0, 5.350, 20.1),
    ("M8", 8.0, 1.25, 7.188, 36.6),
    ("M10", 10.0, 1.5, 9.026, 58.0),
    ("M12", 12.0, 1.75, 10.863, 84.3),
    ("M16", 16.0, 2.0, 14.701, 157.0),
    ("M20", 20.0, 2.5, 18.376, 245.0),
    ("M24", 24.0, 3.0, 22.051, 353.0),
], columns=["series","d","P","d2","As"])

STRENGTH_TABLE = {
    "8.8":  {"Sp": 640.0, "Rm": 800.0},
    "10.9": {"Sp": 940.0, "Rm": 1040.0},
    "12.9": {"Sp": 1100.0, "Rm": 1220.0},
}

# ------------------------ 工具函数 ------------------------
def torque_from_preload_R13(FM, P, d2, Dk, muG, muK):
    """R13/1 风格经验式：M = F*( P/(2π) + 0.16 μG d2 + 0.58 μK Dk )
       单位：P,d2,Dk -> mm；F->N；M输出 N·m
    """
    term_mm = (P/(2*np.pi)) + 0.16*muG*d2 + 0.58*muK*Dk
    return (FM * term_mm) / 1000.0

def preload_from_torque_R13(MA, P, d2, Dk, muG, muK):
    denom = (P/(2*np.pi)) + 0.16*muG*d2 + 0.58*muK*Dk
    return (MA * 1000.0) / np.maximum(denom, 1e-12)

def delta_bolt(Lb, As, Eb):
    """螺栓回弹（圆柱近似）：δS = Lb / (As * Eb)；单位：mm/N"""
    return Lb / np.maximum(As*Eb, 1e-12)

def delta_plate_cone(Lk, E, Dk, alpha_deg=30.0):
    """夹紧件回弹（截头圆锥等效）：δP ≈ (4 Lk)/(π E Dk D2)，D2 = Dk + 2·tan(alpha)·Lk"""
    alpha = np.deg2rad(alpha_deg)
    D2 = Dk + 2.0*np.tan(alpha)*Lk
    D2 = np.maximum(D2, Dk + 1e-6)
    return (4.0*Lk) / (np.pi * E * Dk * D2)

def phi_factor(deltaS, deltaP, n=1.0):
    """Φ = n·δP / (δS + n·δP)"""
    return (n*deltaP) / np.maximum(deltaS + n*deltaP, 1e-12)

def build_scales(base_scales, per_base):
    """将每个基样本的缩放因子扩展为 per_base 份：第一份=1，其余=该值"""
    out = np.empty(len(base_scales)*per_base)
    for i, s in enumerate(base_scales):
        off = i*per_base
        out[off] = 1.0
        out[off+1:off+per_base] = s
    return out

# ------------------------ 主生成函数 ------------------------
def generate_vdi_dataset(n_base=8000, perturb=False, per_base=2, seed=123,
                         muG_mean=0.14, muG_std=0.03, muK_mean=0.12, muK_std=0.03,
                         alpha_deg=30.0, embed_um_min=3.0, embed_um_max=20.0,
                         target_proof_ratio=0.70, proof_cap_ratio=0.90):
    rng = np.random.default_rng(seed)
    tt = THREAD_TABLE.set_index("series")
    series = rng.choice(THREAD_TABLE["series"].values, size=n_base)
    klass  = rng.choice(np.array(list(STRENGTH_TABLE.keys())), size=n_base, p=np.array([0.45,0.40,0.15]))

    d  = np.array([tt.loc[s,"d"]  for s in series])
    P  = np.array([tt.loc[s,"P"]  for s in series])
    d2 = np.array([tt.loc[s,"d2"] for s in series])
    As = np.array([tt.loc[s,"As"] for s in series])

    Sp = np.array([STRENGTH_TABLE[c]["Sp"] for c in klass])
    Rm = np.array([STRENGTH_TABLE[c]["Rm"] for c in klass])

    # 几何/材料
    Lk = rng.uniform(2.0, 8.0, size=n_base) * d
    Eb = np.full(n_base, 210000.0)
    Ec = rng.uniform(70000.0, 210000.0, size=n_base)
    Dk = rng.uniform(1.5, 2.5, size=n_base) * d

    # 摩擦
    muG = np.clip(rng.normal(muG_mean, muG_std, size=n_base), 0.05, 0.30)
    muK = np.clip(rng.normal(muK_mean, muK_std, size=n_base), 0.05, 0.30)

    # 证明载荷与目标预紧力
    F_proof = Sp * As
    FM_nom  = target_proof_ratio * F_proof

    # R4：嵌入/温差转化为 ΔF
    deltaZ_mm = rng.uniform(embed_um_min*1e-3, embed_um_max*1e-3, size=n_base)  # μm -> mm
    Lb = Lk + 0.5*d
    dS = delta_bolt(Lb, As, Eb)
    dP = delta_plate_cone(Lk, Ec, Dk, alpha_deg=alpha_deg)
    Phi = phi_factor(dS, dP, n=1.0)
    deltaF_embed = deltaZ_mm / np.maximum(dS + dP, 1e-12)

    # 外载
    FA = rng.uniform(0.0, 0.5, size=n_base) * F_proof

    # R5：F_M,min
    FM_min = Phi*FA + deltaF_embed  # 若 F_Kerf 未给定按 0 处理
    FM_target = np.minimum(np.maximum(FM_nom, FM_min), proof_cap_ratio*F_proof)

    if not perturb:
        MA = torque_from_preload_R13(FM_target, P, d2, Dk, muG, muK)
        FM = FM_target.copy()
        deltaZ_use = deltaZ_mm
        dS_use, dP_use, Phi_use = dS, dP, Phi
    else:
        # 扰动：在名义扭矩和摩擦上施加小扰动，再反算 FM
        MA_nom = torque_from_preload_R13(FM_target, P, d2, Dk, muG, muK)
        mult_MA  = rng.normal(1.0, 0.05, size=n_base)
        mult_muG = rng.normal(1.0, 0.08, size=n_base)
        mult_muK = rng.normal(1.0, 0.08, size=n_base)

        # 展开 per_base 份
        series = np.repeat(series, per_base); klass = np.repeat(klass, per_base)
        d,P,d2,As,Sp,Rm = [np.repeat(x, per_base) for x in [d,P,d2,As,Sp,Rm]]
        Lk,Eb,Ec,Dk = [np.repeat(x, per_base) for x in [Lk,Eb,Ec,Dk]]
        muG,muK = [np.repeat(x, per_base) for x in [muG,muK]]
        F_proof, FM_target = [np.repeat(x, per_base) for x in [F_proof, FM_target]]
        FA, dS, dP, Phi = [np.repeat(x, per_base) for x in [FA, dS, dP, Phi]]
        MA_nom = np.repeat(MA_nom, per_base)
        deltaZ_use = np.repeat(deltaZ_mm, per_base)
        dS_use, dP_use, Phi_use = dS, dP, Phi

        scales_MA  = build_scales(mult_MA, per_base)
        scales_muG = build_scales(mult_muG, per_base)
        scales_muK = build_scales(mult_muK, per_base)

        muG = np.clip(muG * scales_muG, 0.05, 0.30)
        muK = np.clip(muK * scales_muK, 0.05, 0.30)
        MA  = MA_nom * scales_MA
        FM  = preload_from_torque_R13(MA, P, d2, Dk, muG, muK)

    # 外载叠加
    dF_b = Phi_use * FA
    Fb_max = FM + dF_b
    Fk_res = FM - (1.0 - Phi_use) * FA
    deltaF_embed_use = deltaZ_use / np.maximum(dS_use + dP_use, 1e-12)
    Fk_res_after = np.maximum(Fk_res - deltaF_embed_use, 0.0)

    sigma_b = Fb_max / np.maximum(As, 1e-12)
    SF_y = Sp / np.maximum(sigma_b, 1e-12)
    SF_u = Rm / np.maximum(sigma_b, 1e-12)
    pass_all = (Fk_res_after > 0.0) & (SF_y >= 1.2)
    fail_reason = np.where(~pass_all, np.where(Fk_res_after <= 0.0, "loss_of_clamp", "yield_margin"), "ok")

    df = pd.DataFrame({
        "series": series, "class": klass,
        "d_mm": d, "P_mm": P, "d2_mm": d2, "As_mm2": As, "Dk_mm": Dk,
        "Lk_mm": Lk, "Eb_MPa": Eb, "Ec_MPa": Ec,
        "muG": muG, "muK": muK, "MA_Nm": MA, "FA_N": FA,
        "deltaZ_mm": deltaZ_use,
        "deltaS_mm_per_N": dS_use, "deltaP_mm_per_N": dP_use, "Phi": Phi_use,
        "F_proof_N": F_proof, "FM_N": FM,
        "Fb_max_N": Fb_max, "Fk_residual_N": Fk_res_after,
        "sigma_b_MPa": sigma_b, "SF_yield": SF_y, "SF_ult": SF_u,
        "pass_fail": pass_all.astype(int), "fail_reason": fail_reason
    })
    return df

# ------------------------ CLI ------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal_rows", type=int, default=10000)
    ap.add_argument("--perturbed_rows", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--per_base", type=int, default=2)
    args = ap.parse_args()

    ideal_df = generate_vdi_dataset(n_base=args.ideal_rows, perturb=False, seed=args.seed)
    pert_df  = generate_vdi_dataset(n_base=args.perturbed_rows//args.per_base, perturb=True,
                                    per_base=args.per_base, seed=args.seed)

    ideal_path = "VDI2230_vdiStrict_ideal_{}.csv".format(len(ideal_df))
    pert_path  = "VDI2230_vdiStrict_perturbed_{}.csv".format(len(pert_df))
    ideal_df.to_csv(ideal_path, index=False, encoding="utf-8-sig")
    pert_df.to_csv(pert_path, index=False, encoding="utf-8-sig")

    print("Saved:", ideal_path, pert_path)

if __name__ == "__main__":
    main()
