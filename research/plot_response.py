"""Standalone figures from hash-recorded released data; no solver execution."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from response_analysis import TEMPERATURES, analyze, parse_curve


def main():
    out = Path("research/figures")
    out.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    sensitivity = []
    for temperature in TEMPERATURES:
        path = Path("research/raw/Si2V6-186003/fflo_%s.0.dat" % temperature)
        rows = parse_curve(path.read_text())
        result = analyze(rows)
        sensitivity.append(result)
        axes[0].plot([r[0]*10 for r in rows], [r[3]*.5*2.3653362082e14/1e7 for r in rows],
                     ".-", label="%s K" % temperature, linewidth=1)
        axes[1].plot([w["qmax_angstrom_inverse"]*10 for w in result["windows"]],
                     [w["lambda_ratio"] for w in result["windows"]], ".-")
    axes[0].set(xlabel="Pairing momentum Q (nm⁻¹)",
                ylabel="Released current (10⁷ A/cm²)", title="V₃Si: released response curves")
    axes[0].axhline(0,color="gray",linewidth=.6)
    axes[0].legend(fontsize=8,ncol=2)
    axes[1].set(xlabel="Largest fitted Q (nm⁻¹)", ylabel="Length / one-point length",
                title="Finite-window sensitivity, not uncertainty")
    axes[1].axhline(1,color="gray",linewidth=.6)
    fig.savefig(out/"released_response.png",dpi=180)
    fig.savefig(out/"released_response.pdf")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.5,4),constrained_layout=True)
    ax.plot(TEMPERATURES,[r["author_single_point_lambda_nm"] for r in sensitivity],
            "o-",label="Archived script: one-point slope")
    ax.plot(TEMPERATURES,[r["author_peak_lambda_nm"] for r in sensitivity],
            "s-",label="Archived script: sampled peak + half-gap")
    ax.set(xlabel="Temperature (K)",ylabel="Extracted penetration depth (nm)",
           title="V₃Si: reconstruction of archived extraction")
    ax.legend(fontsize=8)
    fig.savefig(out/"extraction_routes.png",dpi=180)
    fig.savefig(out/"extraction_routes.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
