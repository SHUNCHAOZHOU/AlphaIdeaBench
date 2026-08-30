---
id: fintech-credit-shift
field: fintech
title: Robust credit-risk models under distribution shift with a small compute budget
keywords:
  - fintech
  - credit risk
  - distribution shift
  - tabular deep learning
budget:
  gpu: "1x RTX 4090 24GB"
  gpu_hours: 40
  calendar_weeks: 4
  api_usd: 50
  annotator_hours: 0
  notes: "Public data only (no bank-internal loan tapes). No paid third-party bureau APIs. A meaningful evaluation must include strong tabular baselines (logistic regression, gradient boosting), at least one ablation, and a temporal or geographic shift split — not only i.i.d. CV."
---

# Research background

Consumer credit scoring is a core fintech problem: predict default / serious delinquency from tabular features (income proxies, credit history, utilization). Production models fail when the **population or policy shifts** — new lending products, underwriting changes, macroeconomic regimes, or a different geography. A small lab cannot train foundation models on proprietary bank data. The question is: **on public credit datasets, can we make a tabular model more robust to realistic shifts than gradient boosting, without exceeding a 4090 / 40 GPU-hour budget?**

## Related work and limitations

- **Logistic regression / scorecards** remain the compliance baseline. They are cheap and interpretable, but miss nonlinear interactions and usually assume stationarity.
- **Gradient boosting (XGBoost / LightGBM)** is the default strong tabular baseline (Grinsztajn et al., 2022, NeurIPS; Shwartz-Ziv & Armon, 2022). Limitation: tree ensembles can latch onto spurious correlations that break under temporal or geographic shift.
- **Tabular deep learning** (FT-Transformer, TabNet, MLP with embeddings) sometimes matches GBDT on i.i.d. splits, but the literature often **does not evaluate temporal shift** that actually matters in lending.
- **Domain adaptation / invariant risk** (IRM, GroupDRO, CORAL) is mostly studied in vision. Applying it to sparse, mixed-type credit tables with a **single public source** is under-specified: what is a "domain" when you only have one FICO-style dataset?
- **Fairness-aware credit models** (Hardt et al., 2016 and follow-ups) constrain group error rates, but fairness constraints are **not the same as shift robustness**, and many papers still report only random CV.

Public datasets that fit the budget: **Give Me Some Credit** (Kaggle), **Home Credit Default Risk** (Kaggle, large but CPU/GPU feasible if subsampled), **Taiwan credit card default** (UCI), **Lending Club** public snapshots (use a documented time cutoff). Do not assume access to FICO, Experian, or bank production logs.

## Open problems in this topic

1. A **shift protocol** for public credit data that is more realistic than shuffled CV (e.g. train on earlier vintages / one product, test on later vintages or another geography).
2. Whether **simple recency / importance weighting**, **adversarial validation**, or a light tabular adapter beats GBDT under that protocol, or whether boosting already saturates the public-data ceiling.
3. When robustness methods **hurt** AUC / KS on the shifted test set (negative transfer), and how to detect that without labels from the target period.
4. Evaluation that reports **calibration** (ECE / reliability of predicted PD) and **cost-sensitive** metrics, not only ROC-AUC.

## Allowed evaluation setting

- Models must be trainable on one 4090 in minutes to hours, not days.
- Must compare against logistic regression and LightGBM/XGBoost with a documented hyperparameter search that fits the GPU/CPU budget.
- Must include at least one **non-i.i.d. split** (time or geography). If the chosen public set has no timestamp, construct an explicit proxy (e.g. sort by a date-like feature, or hold out a feature-defined subpopulation) and justify it.
- No synthetic "LLM-generated loan applications" as the sole test set.
