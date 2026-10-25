# Preliminary hand estimate for BRD §6. Annual figures, full rollout (300 RMs).
pert = lambda lo, ml, hi: (lo + 4*ml + hi) / 6
# scenario: (freq lo, ml, hi per year), (magnitude lo, ml, hi $ per event)
S = {
 "S1 Cross-client exposure":   ((2, 6, 15),     (50e3, 150e3, 750e3)),
 "S2 Injection exfiltration":  ((0.05, 0.2, 0.5),(1e6, 4e6, 15e6)),
 "S3 System prompt leak":      ((1, 3, 8),      (10e3, 40e3, 150e3)),
 "S4 Abuse / cost overrun":    ((2, 4, 10),     (5e3, 20e3, 75e3)),
 "S5 Shadow AI leak":          ((0.1, 0.4, 1.0),(0.5e6, 2e6, 6e6)),
}
def eal(f, m, fr=1.0, mr=1.0):  # fr: frequency multiplier after controls
    return pert(*f)*fr * pert(*m)*mr
base = {k: eal(*v) for k, v in S.items()}
lo = {k: v[0][0]*v[1][0] for k, v in S.items()}
hi = {k: v[0][2]*v[1][2] for k, v in S.items()}
print("BASELINE (accept the risk)")
for k in S: print(f"  {k:28s} low {lo[k]/1e3:8.0f}K  mean {base[k]/1e3:8.0f}K  high {hi[k]/1e3:8.0f}K")
print(f"  TOTAL mean {sum(base.values())/1e6:.2f}M  low {sum(lo.values())/1e6:.2f}M  high {sum(hi.values())/1e6:.2f}M")

queries = 300*15*250
def friction(fbr, mins=3, rate=95): return fbr*queries*mins/60*rate
# options: remaining fraction of frequency per scenario, run cost, false-block rate, S5 multiplier
O = {
 "B Vendor AI firewall":        ({"S1":0.7,"S2":0.4,"S3":0.5,"S4":1.0}, 250e3, 0.03),
 "C Our guardrails GR-01..05":  ({"S1":0.3,"S2":0.25,"S3":0.2,"S4":0.2}, 120e3, 0.02),
 "D Guardrails + index fix":    ({"S1":0.1,"S2":0.25,"S3":0.2,"S4":0.2}, 120e3+50e3, 0.02),
}
elasticity = 0.5  # S5 frequency x (1 + e * fbr/2%)
B = sum(base.values())
for name, (rem, run, fbr) in O.items():
    tot = 0
    for k in S:
        key = k[:2]
        if key == "S5": tot += base[k]*(1+elasticity*fbr/0.02)
        else: tot += base[k]*rem.get(key, 1.0)
    fr = friction(fbr); cost = run+fr; red = B-tot
    print(f"{name:28s} EAL {tot/1e6:.2f}M  reduction {red/1e6:.2f}M  run {run/1e3:.0f}K friction {fr/1e3:.0f}K cost {cost/1e3:.0f}K  ratio {red/cost:.1f}:1  friction%hard {fr/2e6*100:.0f}%")
