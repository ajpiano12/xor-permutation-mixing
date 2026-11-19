"""Render the three-page teammate brief. Run with uv run --extra four-bit python -m research.progress_brief."""
from datetime import datetime, timezone
import json
from pathlib import Path

import matplotlib as mpl
mpl.use("pdf")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
ATLAS = "https://pairwise-mixing-atlas.laceyorangutan4.chatgpt.site/library/"
INK, MUTED, TEAL, LIGHT = "#152F34", "#445C61", "#006D65", "#E7F2ED"
BLUE, PALE, GOLD, RULE = "#285A7A", "#EAF1F6", "#905215", "#B8CACA"
PAPER = "#FFFFFF"
mpl.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "mathtext.fontset": "dejavusans"})


def text(ax, x, y, words, size=11, *, color=INK, bold=False, family=None, align="left", url=None):
    ax.text(x, y, words, fontsize=size, va="top", ha=align, color=color, fontfamily=family,
            fontweight="bold" if bold else "normal", linespacing=1.38, url=url)


def line(ax, x1, y1, x2, y2, color=RULE, width=1):
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, solid_capstyle="round", clip_on=False)


def box(ax, x, y, w, h, color, radius=5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                linewidth=0, facecolor=color))


def arrow(ax, x1, y1, x2, y2, color=TEAL):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
                                 linewidth=1.35, color=color))


def page(title, section, number):
    fig = plt.figure(figsize=(8.5, 11), facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 612), ylim=(792, 0))
    ax.set_axis_off()
    text(ax, 41, 27, "DIFFERENCE ATLAS", 9, color=TEAL, bold=True)
    text(ax, 571, 27, section, 9, color=MUTED, align="right")
    line(ax, 41, 46, 571, 46)
    text(ax, 41, 62, title, 25, family="DejaVu Serif")
    line(ax, 41, 749, 571, 749)
    text(ax, 41, 760, "Problem 4  /  19 November 2026", 8.5, color=MUTED)
    text(ax, 571, 760, f"{number} / 3", 8.5, color=MUTED, align="right")
    return fig, ax


def source(ax, x, y, label, document):
    url = document if document.startswith("https://") else ATLAS + document + ".html"
    text(ax, x, y, label, 9, color=TEAL, bold=True, url=url)


def foundations(pdf, upper):
    fig, ax = page("When does a keyed permutation mix?", "MODEL AND EVIDENCE", 1)
    text(ax, 41, 108,
         "Fix a public permutation P on n-bit words. At each round, XOR the same fresh\n"
         "uniform key into t distinct inputs, then apply P to each. Compare their joint\n"
         "outputs with those of a uniform random permutation. Our target is TV ≤ 2⁻¹²⁸\n"
         "for every start. TV is the largest probability gap over any event.", 10.8)

    text(ax, 41, 186, "One key moves all four inputs together", 15, bold=True)
    text(ax, 41, 212, "A worked three-bit round. Each row follows one point.", 10.5, color=MUTED)
    box(ax, 41, 238, 530, 168, PALE)
    columns = [97, 222, 352, 492]
    for x, label in zip(columns, ["Input", "XOR with 101", "Apply P", "XOR with first output"]):
        text(ax, x, 252, label, 9, color=BLUE, bold=True, align="center")
    rows = [("000", "101", "010", "000"), ("001", "100", "111", "101"),
            ("011", "110", "011", "001"), ("110", "011", "110", "100")]
    for i, row in enumerate(rows):
        y = 279 + i * 29
        for j, val in enumerate(row):
            text(ax, columns[j], y, val, 13, family="DejaVu Sans Mono", align="center",
                 color=TEAL if j == 3 and i else INK, bold=(j == 3 and i > 0))
        for left, right in zip(columns, columns[1:]):
            arrow(ax, left + 28, y + 8, right - 29, y + 8, "#719295")
    text(ax, 41, 418,
         "The displayed P is inversion in the eight-element field, with zero fixed. Three\n"
         "differences describe the four points up to a common shift. A final fresh key\n"
         "makes that shift uniform, so tracking the differences saves one coordinate.", 10.6)

    text(ax, 41, 491, "What the small cases established", 15, bold=True)
    for x, count, caption in [(41, "80.00%", "of three-bit tables mix pairs"),
                               (310, "99.77%", "of four-bit tables mix pairs")]:
        line(ax, x, 527, x + 241, 527, TEAL, 2)
        text(ax, x, 538, count, 22, color=TEAL, bold=True)
        text(ax, x, 570, caption, 10.5)
    text(ax, 41, 604,
         "These fractions are exact before rounding. Eventual convergence says little\n"
         "about speed. Two equally large three-bit families both need four rounds on\n"
         "triples at TV ¼, yet need 88 and 129 rounds at our smaller target.", 10.6)
    text(ax, 41, 672, "What to tell the team", 10.5, bold=True, color=BLUE)
    text(ax, 41, 691, f"One 128-bit design provably mixes four inputs within {upper} rounds. Another 128-bit\n"
         "design needs more than 7.48 × 10³⁹ rounds on the very same four-input test.", 10.1)
    source(ax, 41, 725, "Small-error census", "small_error_data")
    source(ax, 177, 725, "Four-bit count", "four_bit_count")
    source(ax, 294, 725, "Project brief and model", "brief_and_progress")
    pdf.savefig(fig)
    plt.close(fig)


def construction(pdf, rounds, window_count):
    fig, ax = page("A round bound on 128 bits", "PROVED FOR A SPECIFIED FAMILY", 2)
    text(ax, 41, 108,
         "The public rule updates a 16-bit block, then rotates the word. Its short formula\n"
         "lets us bound every four-input start without listing any 128-bit truth table.", 11)
    text(ax, 41, 162, "How the update moves through the word", 15, bold=True)
    start_x, block_w = 120, 55
    for row, (label, active) in enumerate([("Update 1", 0), ("Update 2", 1), ("Update 8", 7)]):
        y = 198 + row * 37
        text(ax, 41, y + 5, label, 10, color=MUTED)
        for i in range(8):
            box(ax, start_x + i * block_w, y, block_w - 4, 24, TEAL if i == active else PALE, radius=2)
            text(ax, start_x + (i + .5) * block_w - 2, y + 6, str(i + 1), 9,
                 color="white" if i == active else BLUE, align="center", bold=(i == active))
    text(ax, 41, 311,
         "The highlighted block gets an XOR offset computed from the other 112 bits.\n"
         "Those bits specify a field element. Invert it and take 16 output bits. The diagram\n"
         "labels original positions, so rotation appears as a moving update window.", 10.3)
    text(ax, 41, 384, "Where the true four-input mixing time lies", 15, bold=True)
    left, right = 51, 558
    def tick(r):
        return left + (r - 1) * (right - left) / 85
    line(ax, left, 449, right, 449, RULE, 2)
    line(ax, tick(10), 449, tick(rounds), 449, TEAL, 5)
    for value, color in [(10, INK), (rounds, TEAL), (81, MUTED)]:
        ax.add_patch(Circle((tick(value), 449), 4.2, color=color))
        text(ax, tick(value), 414, str(value), 18, bold=True, color=color, align="center")
    for value, desc in [(10, "necessary"), (rounds, "sufficient now"), (81, "earlier bound")]:
        text(ax, tick(value), 463, desc, 9, align="center", color=MUTED)
    text(ax, 41, 505, "Why the endpoints differ", 11, color=TEAL, bold=True)
    text(ax, 41, 527,
         "For the lower bound, start all four inputs with the same 112 control bits. The\n"
         "first update gives them the same offset. After nine rounds, far too few output\n"
         "patterns are reachable. For the upper bound, three warmup updates make\n"
         "collisions rare. One eight-update sweep spreads out the initial distribution.\n"
         "Three further sweeps shrink its remaining bias. One final round gives 36.", 10.5)
    box(ax, 41, 638, 530, 60, LIGHT)
    text(ax, 53, 651, "A second construction", 10.5, color=TEAL, bold=True)
    text(ax, 53, 673, f"A 12-bit update with any degree-15 control polynomial certifies {window_count} rounds.", 10)
    text(ax, 41, 705, "These round counts are project derivations using published shuffle and character-sum methods.", 8.4, color=MUTED)
    source(ax, 41, 725, "Warmup proof", "warmup_bounds")
    source(ax, 149, 725, "Inverse construction", "spectral_certificate")
    source(ax, 299, 725, "Polynomial construction", "polynomial_update")
    source(ax, 466, 725, "Prior work", "literature_review")
    pdf.savefig(fig)
    plt.close(fig)


def speeds(pdf, empirical, slow_span):
    fig, ax = page("How to tell fast from slow", "RANKING TABLES AND PROVING SLOWDOWN", 3)
    text(ax, 41, 108,
         "Two tools answer different questions. A short numerical probe ranks small tables\n"
         "for follow-up. Closeness to an affine map can prove that convergence is slow.", 11)

    text(ax, 41, 165, "A short probe predicts pairwise round counts", 15, bold=True)
    text(ax, 41, 195,
         "Build the transition table on nonzero XOR differences. Twelve matrix–vector\n"
         "steps estimate how fast a surviving bias decays. Check predictions against\n"
         "exact worst-start counts on fresh, uniformly sampled permutations.", 10.5)
    source(ax, 41, 725, "Benchmark and data", "rate_heuristic")
    source(ax, 200, 725, "Slow-family proof", "round_bounds")
    source(ax, 346, 725, "Earlier results and provenance", "literature_review")
    plot = fig.add_axes([.105, .472, .42, .177])
    for row in empirical["prediction_bins"]:
        x, y = row["median_prediction"], row["actual_median"]
        plot.vlines(x, row["actual_q25"], row["actual_q75"], color=TEAL, lw=1, zorder=2)
        plot.scatter(x, y, color=TEAL, edgecolor="white", s=30, zorder=3)
    lo, hi = 68, 192
    plot.plot([lo, hi], [lo, hi], color=MUTED, linewidth=1, linestyle="--", zorder=2)
    plot.set_xlim(lo, hi)
    plot.set_ylim(lo, hi)
    plot.set_xlabel("Predicted rounds", fontsize=8, labelpad=2)
    plot.set_ylabel("Exact rounds", fontsize=8, labelpad=1)
    plot.grid(axis="both", color="#DCE7E5", linewidth=.6, zorder=0)
    plot.tick_params(labelsize=7, colors=MUTED, length=2)
    for side in ("left", "bottom"):
        plot.spines[side].set_color(RULE)
    for side in ("top", "right"):
        plot.spines[side].set_visible(False)

    metrics = empirical["metrics"]
    text(ax, 350, 270, "256 four-bit holdouts", 11, color=TEAL, bold=True)
    text(ax, 350, 293, f'Mean error was {metrics["arnoldi"]["mae"]:.2f} rounds.\n'
         f'A constant guess missed by\n{metrics["constant"]["mae"]:.1f} rounds on average.\n'
         f'The largest probe miss was\n{metrics["arnoldi"]["max_abs_error"]} rounds.', 10.1)
    text(ax, 350, 381, "Dots give medians within 10-round\n"
         "prediction bins. Bars span the\n"
         "middle half of exact counts.", 9.1, color=MUTED)
    text(ax, 41, 469, "A structural witness proves a long wait", 15, bold=True)
    text(ax, 41, 500,
         "Start with a linear map that cycles through all nonzero words. Swap just two\n"
         "inputs. The resulting permutation mixes four inputs. Most keys still send each\n"
         "input difference along its old deterministic path. Deviations are rare.", 10.5)
    box(ax, 41, 568, 530, 63, LIGHT)
    text(ax, 54, 580, slow_span, 15, bold=True, color=TEAL)
    text(ax, 54, 608, "Full rounds for this 128-bit example on four inputs at TV 2⁻¹²⁸. Compare page 2.", 9.6)
    text(ax, 41, 652,
         "The numerical probe builds a table with roughly 2²ⁿ entries. Its accuracy at\n"
         "large widths or for quadruples remains unmeasured. The separate affine\n"
         "screen takes O(n · 2ⁿ) word operations on a supplied permutation table.", 10.4)
    pdf.savefig(fig)
    plt.close(fig)


def main():
    from research.round_bounds import family_bounds
    from research.sweep_bounds import sweep_analysis

    def upper_for(width, control):
        bounds = sweep_analysis(128, width, 4, [128], 0, control)["2^-128"]
        candidates = [bounds["short_blocks"]]
        if bounds["sweep_norm"]:
            candidates.append(bounds["sweep_norm"]["rounds"])
        return min(r for r in candidates if r is not None)

    upper = upper_for(16, "inverse")
    polynomial_upper = upper_for(12, "power15")
    data = json.loads((ROOT / "results/rate_heuristic.json").read_text())["4"]["holdout"]["128"]
    slow = family_bounds(128, 128, order=4)
    unit = 10**37
    lower = slow["necessary_cipher_rounds"] // unit
    upper_hundredths = -(-slow["sufficient_cipher_rounds"] // unit)
    span = f"{lower / 100:.2f} × 10³⁹  <  rounds  <  {upper_hundredths / 100:.2f} × 10³⁹"
    date = datetime(2026, 11, 19, tzinfo=timezone.utc)
    metadata = {"Title": "When does a keyed permutation mix?", "Author": "Difference Atlas",
                "Subject": "Illustrated progress brief on Problem 4", "CreationDate": date, "ModDate": date}
    with PdfPages(ROOT / "results/progress-brief.pdf", metadata=metadata) as pdf:
        foundations(pdf, upper)
        construction(pdf, upper, polynomial_upper)
        speeds(pdf, data, span)


if __name__ == "__main__":
    main()
