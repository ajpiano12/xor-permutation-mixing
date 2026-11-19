"""Render the illustrated teammate brief with uv run --extra four-bit python -m research.progress_brief."""
from datetime import datetime, timezone
import json
from pathlib import Path

import matplotlib as mpl
mpl.use("pdf")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.textpath import TextToPath

from research.round_bounds import family_bounds
from research.sweep_bounds import sweep_analysis

ROOT = Path(__file__).resolve().parents[1]
ATLAS = "https://pairwise-mixing-atlas.laceyorangutan4.chatgpt.site/library/"
INK, MUTED, TEAL = "#183438", "#475D60", "#00675E"
MINT, ICE, RULE, BLUE = "#E7F3ED", "#EBF1F6", "#B4C9C6", "#255675"
SANS, SERIF, MONO = "DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono"
LEFT, RIGHT = 46, 566
WIDTH = RIGHT - LEFT
MEASURE = TextToPath()
mpl.rcParams.update({"font.family": SANS, "pdf.fonttype": 42})


def text(ax, x, y, value, size=11.5, *, color=INK, bold=False, family=SANS, align="left", url=None):
    ax.text(x, y, value, fontsize=size, color=color, fontfamily=family, verticalalignment="top",
            horizontalalignment=align, fontweight="bold" if bold else "normal", url=url)


def paragraph(ax, y, value, *, x=LEFT, width=WIDTH, size=11.5, leading=17.3, color=INK):
    """Line-wrap by physical text width so the same copy fits on screen and in print."""
    font = FontProperties(family=SANS, size=size)
    words = value.split()
    current = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and MEASURE.get_text_width_height_descent(candidate, font, ismath=False)[0] > width:
            text(ax, x, y, " ".join(current), size, color=color)
            y += leading
            current = []
        current.append(word)
    if current:
        text(ax, x, y, " ".join(current), size, color=color)
        y += leading
    return y


def rule(ax, x1, y, x2, color=RULE):
    ax.plot([x1, x2], [y, y], color=color, linewidth=0.8)


def box(ax, x, y, width, height, color, radius=4):
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle=f"round,pad=0,rounding_size={radius}",
                                linewidth=0, facecolor=color))


def arrow(ax, start, end, *, both=False):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="<->" if both else "-|>",
                                 mutation_scale=10, linewidth=1.3, color=TEAL))


def new_page(title, section, number):
    fig = plt.figure(figsize=(8.5, 11), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 612), ylim=(792, 0))
    ax.set_axis_off()
    text(ax, LEFT, 28, "DIFFERENCE ATLAS", 9, bold=True, color=TEAL)
    text(ax, RIGHT, 28, section, 9, color=MUTED, align="right")
    rule(ax, LEFT, 46, RIGHT)
    text(ax, LEFT, 62, title, 24.5, family=SERIF)
    rule(ax, LEFT, 747, RIGHT)
    text(ax, LEFT, 758, "Problem 4  /  Research brief  /  19 November 2026", 8.8, color=MUTED)
    text(ax, RIGHT, 758, f"{number} / 4", 8.8, color=MUTED, align="right")
    return fig, ax


def heading(ax, y, value):
    text(ax, LEFT, y, value, 15, bold=True)
    return y + 27


def finish(pdf, fig, ax, end, links):
    if end > 713:
        raise ValueError(f"Body overlaps the source line on page {pdf.get_pagecount() + 1}: {end:.1f}")
    x = LEFT
    for label, slug in links:
        text(ax, x, 724, label, 8.8, bold=True, color=TEAL, url=ATLAS + slug + ".html")
        font = FontProperties(family=SANS, weight="bold", size=8.8)
        x += MEASURE.get_text_width_height_descent(label, font, ismath=False)[0] + 23
    pdf.savefig(fig)
    plt.close(fig)


def opening(pdf, upper):
    fig, ax = new_page("Why follow two messages at once?", "The question", 1)
    y = paragraph(ax, 108,
        "Choose two three-bit messages, 000 and 001. Encrypt each one with the same keys, then "
        "repeat the experiment with fresh keys. The first output can visit all eight positions equally often and still "
        "tell you exactly where its partner landed.")
    y = paragraph(ax, y + 10,
        "Here’s how that can happen. Each round uses a public permutation, a reversible rule that "
        "rearranges the eight words. First we draw a three-bit key, with all eight choices equally likely. "
        "A 1 in the key flips that bit in both messages. This is called XOR. Then we apply the rule. We reuse it "
        "every round and draw a new key each time.")
    y = heading(ax, y + 19, "Try the simplest possible rule")
    y = paragraph(ax, y,
        "Let the public rule leave every word where it is. With key 101, our messages become 101 and "
        "100. Whatever key we draw, the two outputs still differ only in their last bit.")
    chart = y + 10
    box(ax, LEFT, chart, WIDTH, 77, ICE)
    text(ax, LEFT + 12, chart + 9, "All eight possible destinations for the first message", 10.3, bold=True, color=BLUE)
    for i in range(4):
        x = LEFT + 14 + i * 126
        text(ax, x, chart + 32, f"{2*i:03b}", 12.3, family=MONO)
        arrow(ax, (x + 28, chart + 40), (x + 62, chart + 40), both=True)
        text(ax, x + 68, chart + 32, f"{2*i+1:03b}", 12.3, family=MONO)
    text(ax, LEFT + 12, chart + 59, "Follow an arrow from either output to find its partner.", 9.9, color=MUTED)
    y = paragraph(ax, chart + 91,
        "Now compare that with a fair shuffle of the eight words. Once we see the first output, each of "
        "the seven other positions is equally likely for its partner. Only one differs in just the last bit. "
        "A fair shuffle produces that relationship one time in seven. Our rule produces it every time, "
        "even after a thousand rounds. The probability gap is 1 − 1/7 = 6/7.")
    y = heading(ax, y + 16, "What counts as mixed?")
    y = paragraph(ax, y,
        "Total variation distance (TV) is the largest probability gap you can find by looking at the "
        "outputs. We say a rule mixes by round r if, after r rounds, that gap is at most our target "
        "even for the hardest choice of starting messages. Two messages give the pairwise test. "
        "Following four together lets us check relationships among all four. That’s the four-wise test.")
    y = paragraph(ax, y + 9,
        f"We chose a tiny target, 2⁻¹²⁸, the chance of guessing a particular 128-bit string in one try. "
        f"On page 3 we’ll see why {upper} rounds suffice for one rule to meet it on every four-message start.")
    finish(pdf, fig, ax, y, [("Problem statement and model", "brief_and_progress"),
                             ("Why differences are enough", "higher_census")])


def small_tables(pdf, data):
    fig, ax = new_page("How can we spot a faster rule?", "What the small cases teach us", 2)
    y = paragraph(ax, 108,
        "For three-bit words we can write a rule down as a list of eight destinations, one per input. "
        "There are only 8! = 40,320 ways to fill in that list. We checked them all. Exactly 32,256, "
        "or 80%, eventually mix every pair. A separate counting argument puts the four-bit share at "
        "about 99.77%. That tells us how often mixing happens. How long do we have to wait?")
    y = paragraph(ax, y + 10,
        "How close we ask the outputs to get also matters. Two families of three-bit rules both took "
        "four rounds on triples when we allowed a probability gap of ¼. When we tightened the gap "
        "to 2⁻¹²⁸, one family needed 88 rounds and the other needed 129. The looser target had "
        "hidden a real difference in speed.")
    y = heading(ax, y + 18, "Using an early pattern to predict the wait")
    y = paragraph(ax, y,
        "The XOR difference of two words marks the positions where they disagree. For 000 and 001 "
        "it’s 001. A different rule might make that pair disagree in several places after a round. "
        "On four bits there are just 15 possible nonzero differences. For each one we can try all "
        "16 keys and count how often each next difference occurs.")
    y = paragraph(ax, y + 9,
        "Under a fair shuffle each difference has chance 1/15. If one occurs more often, that extra "
        "probability is a bias we can follow through another round. Our predictor takes "
        "12 short numerical steps to estimate which bias fades most slowly. It then extrapolates "
        "how many rounds that bias will need to shrink below the target.")
    chart = y + 12
    box(ax, LEFT, chart, WIDTH, 121, MINT)
    text(ax, LEFT + 13, chart + 10, "Three answers for one four-bit rule, tested on pairs", 10.8, color=TEAL, bold=True)
    for row, (count, meaning) in enumerate([
        ("129", "rounds predicted from the early decay"),
        ("150", "rounds actually required, counting all paths for every starting pair"),
        ("157", "rounds guaranteed sufficient by a separate mathematical bound"),
    ]):
        cy = chart + 37 + row * 26
        text(ax, LEFT + 14, cy - 1, count, 14, bold=True, color=TEAL)
        text(ax, LEFT + 61, cy + 1, meaning, 10.3)
    four = data["4"]["holdout"]["128"]["metrics"]["arnoldi"]["mae"]
    five = data["5"]["holdout"]["128"]["metrics"]["arnoldi"]["mae"]
    y = paragraph(ax, chart + 134,
        f"This was the largest miss among 256 fresh four-bit rules. Across the whole group, the "
        f"prediction was off by {four:.2f} rounds on average. On 256 fresh five-bit rules the average "
        f"miss was {five:.2f}. We use the estimate to pick small tables worth a closer look.")
    y = paragraph(ax, y + 9,
        "At 128 bits even listing the possible pair differences is out of reach. To get a guarantee "
        "there, we need to use the structure of the rule itself.")
    finish(pdf, fig, ax, y, [("Three-bit census", "small_error_data"), ("Four-bit count", "four_bit_count"),
                             ("Predictor and exact checks", "rate_heuristic")])


def fast_rule(pdf, upper):
    fig, ax = new_page("Why do 36 rounds suffice?", "A fast 128-bit rule", 3)
    y = paragraph(ax, 108,
        "Take four distinct 128-bit messages. Our goal is for their four outputs, in order, to look "
        "like four distinct words drawn uniformly without replacement. To follow their relationships, "
        "we record where each of the last three words differs from the first. A shared XOR leaves "
        "all three differences unchanged. It’s the public rule that has to change them.")
    y = paragraph(ax, y + 10,
        "Split each word into eight blocks of 16 bits. After the shared key is applied, the other "
        "seven blocks determine which bits to flip in the first block. Then rotate the word by one "
        "block. The same rule will now update the next block in the original word.")
    chart = y + 12
    box(ax, LEFT, chart, WIDTH, 110, ICE)
    for r, (label, selected) in enumerate([("First update", 0), ("Second update", 1), ("Eighth update", 7)]):
        cy = chart + 11 + r * 24
        text(ax, LEFT + 12, cy + 3, label, 9.9)
        for i in range(8):
            bx = LEFT + 130 + i * 47
            box(ax, bx, cy, 42, 19, TEAL if i == selected else "white", radius=2)
            text(ax, bx + 21, cy + 2.8, chr(ord("A") + i), 10.3, align="center", bold=i == selected,
                 color="white" if i == selected else BLUE)
    text(ax, LEFT + 12, chart + 87, "Letters follow the original blocks. Eight updates give each block one turn, or one sweep.",
         9.5, color=MUTED)
    y = paragraph(ax, chart + 123,
        "How do we choose the flips? Treat the seven blocks as one number in a finite field, where "
        "each nonzero number has a unique partner that multiplies with it to give one. Take 16 bits "
        "of that partner as the flip pattern. Zero gives no flips. If two messages have identical "
        "seven-block values, their flip patterns match exactly. For different values, a published result "
        "on reciprocals bounds how strongly their flips can be related under a fresh key.")
    y = heading(ax, y + 14, "What the lower and upper bounds tell us")
    y = paragraph(ax, y,
        "Nine rounds can fail. Give all four messages the same values in blocks B through H, and "
        "four different values in A. The first update gives all four the same flips. Counting forward "
        "from this start shows that after nine rounds, most patterns of disagreement with the first "
        "output are still impossible. A fair shuffle can reach all of them.")
    y = paragraph(ax, y + 9,
        f"By {upper} rounds every start passes. After three updates, two messages are unlikely to "
        "agree on all seven blocks that choose their next flips. Using this fact and the arithmetic "
        "of the rule, we can bound how much bias survives a sweep. Four sweeps and a final keyed round bring the total "
        f"to 3 + 32 + 1 = {upper} and the worst probability gap below 2⁻¹²⁸.")
    y = paragraph(ax, y + 9,
        f"That puts the first round that works for every start somewhere from 10 through {upper}. "
        "Our earlier proof could only guarantee 81 rounds for this very same rule.")
    finish(pdf, fig, ax, y, [("Construction and lower bound", "spectral_certificate"),
                             ("Proof of the 36-round guarantee", "warmup_bounds"),
                             ("Polynomial variant", "polynomial_update")])


def slow_rule(pdf, upper, bounds):
    fig, ax = new_page("How can another rule take so long?", "A slow rule on the same test", 4)
    y = paragraph(ax, 108,
        "On page 1 the pair always differed in its last bit. A rule can also move a pair’s difference "
        "through a predictable sequence. Say the difference moves from 001 to 010 to 100. Even "
        "as the messages move around, we can still tell which bits will disagree next.")
    y = paragraph(ax, y + 10,
        "For our 128-bit example, we start with a linear rule. It respects XOR, so applying the rule "
        "to the old difference gives the next one, whatever key was drawn. We choose one that cycles "
        "through all nonzero differences. Then we exchange its outputs for inputs 0 and 1. Every "
        "other entry stays the same.")
    y = heading(ax, y + 15, "What happens to a pair in one round?")
    chart = y + 2
    box(ax, LEFT, chart, WIDTH, 101, ICE)
    text(ax, LEFT + 13, chart + 37, "Apply a fresh key", 10.6, color=BLUE, bold=True)
    arrow(ax, (LEFT + 118, chart + 45), (LEFT + 158, chart + 24))
    arrow(ax, (LEFT + 118, chart + 45), (LEFT + 158, chart + 70))
    text(ax, LEFT + 166, chart + 10, "Both words miss 0 and 1", 11, bold=True)
    text(ax, LEFT + 166, chart + 28, "The difference follows its old, predictable path.", 10.1)
    text(ax, LEFT + 166, chart + 57, "A word lands on 0 or 1", 11, bold=True)
    text(ax, LEFT + 166, chart + 75, "The swapped entries can send the difference off that path.", 10.1)
    y = paragraph(ax, chart + 114,
        "For a given pair, at most four of the 2¹²⁸ possible keys can send either word to either "
        "changed entry. So the difference can follow its predictable path for an enormous number of rounds. The full "
        "proof counts how these rare departures accumulate. It shows that the rule eventually mixes.")
    divisor = 10**37
    lower = bounds["necessary_cipher_rounds"] // divisor
    high = -(-bounds["sufficient_cipher_rounds"] // divisor)
    y = paragraph(ax, y + 9,
        f"On the same four-message test and at the same 2⁻¹²⁸ target as page 3, this rule needs "
        f"between {lower/100:.2f} × 10³⁹ and {high/100:.2f} × 10³⁹ rounds. Pairs already give the lower "
        "bound. If two outputs still show a pattern, anyone watching all four can see it too.")
    inset = y + 13
    box(ax, LEFT, inset, WIDTH, 115, MINT)
    text(ax, LEFT + 14, inset + 11, "How I’d summarize it to a teammate", 12.1, color=TEAL, bold=True)
    end = paragraph(ax, inset + 36,
        f"“We’re asking how many rounds it takes for four chosen messages to behave like four "
        f"draws from a fair shuffle. One 128-bit rule gets there by round {upper}. Another almost "
        "always carries an old difference forward and needs about 8 × 10³⁹ rounds. What I’d like "
        f"to pin down next is where the fast rule crosses the line between 10 and {upper}.”",
        x=LEFT + 14, width=WIDTH - 28, size=11.0, leading=15)
    if end > inset + 113:
        raise ValueError("Teammate summary is too tall for its panel")
    y = paragraph(ax, inset + 125,
        "The round bounds are proofs from this project. Earlier papers supply methods for following "
        "differences and analyzing shuffles. Priority for these particular bounds is still unverified.",
        size=9.5, leading=13.5, color=MUTED)
    finish(pdf, fig, ax, y, [("Slow construction and proof", "round_bounds"), ("What the literature already proves", "literature_review")])


def main():
    def bound_for(control, width):
        result = sweep_analysis(128, width, 4, [128], 0, control)["2^-128"]
        return min(r for r in (result["short_blocks"], (result["sweep_norm"] or {}).get("rounds")) if r is not None)

    upper = bound_for("inverse", 16)
    data = json.loads((ROOT / "results/rate_heuristic.json").read_text())
    bounds = family_bounds(128, 128, order=4)
    date = datetime(2026, 11, 19, tzinfo=timezone.utc)
    metadata = {"Title": "Why follow two messages at once?", "Author": "Difference Atlas",
                "Subject": "An illustrated introduction to mixing in XOR-keyed permutations",
                "CreationDate": date, "ModDate": date}
    output = ROOT / "results/progress-brief.pdf"
    draft = output.with_suffix(".draft.pdf")
    try:
        with PdfPages(draft, metadata=metadata) as pdf:
            opening(pdf, upper)
            small_tables(pdf, data)
            fast_rule(pdf, upper)
            slow_rule(pdf, upper, bounds)
        draft.replace(output)
    finally:
        draft.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
