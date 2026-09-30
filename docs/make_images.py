"""Renders the architecture diagram + terminal-output images used in the report."""
import os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "img")

# ------------------------------------------------------------ architecture
def box(ax, x, y, w, h, text, fc, ec="#2b2b2b", fs=10, bold=True, lw=1.6, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=4, linespacing=1.4)

def arrow(ax, p1, p2, label=None, color="#111", lo=(0, 0.12), both=False, style="-|>"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=("<|-|>" if both else style),
                                 mutation_scale=16, lw=2, color=color, zorder=5))
    if label:
        ax.text((p1[0] + p2[0]) / 2 + lo[0], (p1[1] + p2[1]) / 2 + lo[1], label, ha="center",
                va="bottom", fontsize=8.5, color=color, zorder=6,
                bbox=dict(fc="white", ec="none", pad=1.2))

def architecture():
    fig, ax = plt.subplots(figsize=(14, 8.6))
    ax.set_xlim(0, 14); ax.set_ylim(-0.6, 8.4); ax.axis("off")
    ax.text(7, 8.15, "Architecture: Automated Cloud Deployment Pipeline on AWS", ha="center",
            fontsize=15, fontweight="bold")

    def region(x, y, w, h, fc, ec, lw=1.8, ls="-"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    fc=fc, ec=ec, lw=lw, ls=ls, zorder=1))
    # regions
    region(3.3, 0.2, 10.55, 6.1, "#fbfbfd", "#232f3e", 2.2)
    ax.text(3.45, 6.07, "AWS Cloud (af-south-1)", fontsize=10.5, fontweight="bold", color="#232f3e", zorder=2)
    region(3.5, 1.65, 10.15, 4.2, "#f2faf2", "#2e7d32", 1.8, "--")
    ax.text(3.65, 5.62, "VPC 10.0.0.0/16", fontsize=10, fontweight="bold", color="#2e7d32", zorder=2)
    region(3.7, 3.45, 9.8, 2.0, "#e8f3ff", "#1565c0", 1.5)
    ax.text(3.85, 5.2, "Public subnets (2 AZs)", fontsize=9.5, fontweight="bold", color="#1565c0", zorder=2)
    region(9.6, 1.85, 3.9, 1.45, "#fff2e3", "#e65100", 1.5)
    ax.text(9.75, 3.05, "Private subnets", fontsize=9, fontweight="bold", color="#e65100", zorder=2)

    # main traffic path
    box(ax, 0.3, 4.0, 1.7, 1.0, "Internet\n(user / browser)", "#e8eaf6", fs=10)
    box(ax, 4.0, 4.0, 1.4, 1.0, "Internet\nGateway", "#ffffff", fs=9.5)
    box(ax, 6.3, 3.85, 2.2, 1.3, "Application\nLoad Balancer\nSG: port 80 open", "#ffe0b2", fs=9.5)
    region(9.6, 3.6, 3.75, 1.65, "#ffffff", "#ed7100", 2)
    ax.text(11.47, 5.03, "EC2 host (Docker)", ha="center", fontsize=9.5, fontweight="bold", zorder=3)
    box(ax, 9.85, 3.75, 3.25, 1.0, "Flask app container\nport 8000  |  GET /health", "#d1ecf1", fs=9.2)
    box(ax, 10.0, 1.95, 3.1, 0.9, "Amazon RDS\nPostgreSQL 16 (encrypted)", "#ffccbc", fs=9.5)
    arrow(ax, (2.0, 4.5), (4.0, 4.5), "1  HTTP :80", lo=(0, 0.08))
    arrow(ax, (5.4, 4.5), (6.3, 4.5))
    arrow(ax, (8.5, 4.5), (9.6, 4.5), "2  :80", lo=(0, 0.08))
    arrow(ax, (11.47, 3.6), (11.47, 2.85), None)
    ax.text(11.6, 3.22, "3  SQL :5432", fontsize=8.5, va="center", zorder=6,
            bbox=dict(fc="white", ec="none", pad=1))
    ax.text(7.0, 3.6, "", fontsize=1)
    ax.text(3.8, 3.3, "Request path (responses return the same way):\nInternet \u2192 Load Balancer \u2192 EC2 container \u2192 RDS",
            fontsize=8.3, style="italic", color="#444", ha="left", va="top", zorder=3, linespacing=1.5)
    
    # top band: CI/CD
    box(ax, 0.3, 6.85, 2.7, 0.95, "S3 bucket + DynamoDB\nTerraform remote state", "#f3e5f5", fs=9)
    box(ax, 4.4, 6.85, 2.6, 0.95, "GitHub Actions\nCI/CD pipeline", "#e0e0e0", fs=10)
    box(ax, 9.0, 6.85, 2.8, 0.95, "Amazon ECR\nDocker image registry", "#e1f5fe", fs=9)
    arrow(ax, (4.4, 7.32), (3.0, 7.32), "state / lock", color="#6a1b9a", lo=(0, 0.08))
    arrow(ax, (7.0, 7.32), (9.0, 7.32), "docker push", color="#1565c0", lo=(0, 0.08))
    arrow(ax, (5.7, 6.85), (5.7, 5.85), None, color="#6a1b9a")
    ax.text(5.85, 6.55, "terraform apply", fontsize=8.5, color="#6a1b9a", va="center", zorder=6,
            bbox=dict(fc="white", ec="none", pad=1))
    arrow(ax, (11.4, 6.85), (11.4, 5.25), None, color="#1565c0")
    ax.text(11.55, 6.25, "docker pull\n(deploy via SSM)", fontsize=8.5, color="#1565c0", va="center", zorder=6,
            bbox=dict(fc="white", ec="none", pad=1))
    
    # monitoring
    box(ax, 7.0, 0.45, 2.7, 0.95, "CloudWatch Alarms\nCPU > 80%  |  HTTP 5xx rate", "#fff9c4", fs=8.8)
    box(ax, 4.0, 0.45, 2.1, 0.95, "SNS topic", "#fff9c4", fs=9.5)
    box(ax, 0.3, 0.45, 2.1, 0.95, "Admin e-mail\n(alert)", "#ffffff", fs=9.5)
    arrow(ax, (7.4, 3.85), (7.4, 1.4), None, color="#f9a825")
    ax.text(7.55, 2.3, "metrics", fontsize=8.5, color="#b8860b", zorder=6, bbox=dict(fc="white", ec="none", pad=1))
    arrow(ax, (7.0, 0.92), (6.1, 0.92), None, color="#f9a825")
    arrow(ax, (4.0, 0.92), (2.4, 0.92), "e-mail", color="#f9a825", lo=(0, 0.08))

    # legend
    lx = 0.6
    for col, lab, dx in (("#111", "user traffic", 1.9), ("#1565c0", "image build / deploy", 2.5),
                         ("#6a1b9a", "Terraform", 1.7), ("#f9a825", "monitoring / alerts", 2.2)):
        ax.plot([lx, lx + 0.5], [-0.3, -0.3], color=col, lw=2.5)
        ax.text(lx + 0.6, -0.3, lab, fontsize=9, va="center")
        lx += dx + 0.6
    fig.savefig(os.path.join(OUT, "architecture.png"), dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ------------------------------------------------------------ terminal image
def term(txt_path, png_name, title):
    text = open(txt_path).read().replace("\r", "")
    text = re.sub(r"\x1b\[[0-9;]*m", "", text).rstrip("\n")
    lines = []
    for ln in text.split("\n"):
        while len(ln) > 98:
            lines.append(ln[:98]); ln = "    " + ln[98:]
        lines.append(ln)
    import matplotlib.font_manager as fm
    font = ImageFont.truetype(fm.findfont("DejaVu Sans Mono"), 17)
    bold = ImageFont.truetype(fm.findfont("DejaVu Sans Mono:bold"), 17)
    lh, pad, top = 25, 22, 44
    w = 1000; h = top + pad * 2 + lh * len(lines)
    im = Image.new("RGB", (w, h), "#1e1e2e"); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, top - 6), fill="#313244")
    for i, c in enumerate(("#f38ba8", "#f9e2af", "#a6e3a1")):
        d.ellipse((16 + i * 26, 12, 32 + i * 26, 28), fill=c)
    d.text((110, 10), title, font=bold, fill="#cdd6f4")
    y = top + pad - 6
    for ln in lines:
        col = "#cdd6f4"
        if ln.startswith("$"): col = "#89b4fa"
        elif "PASSED" in ln or "Success" in ln or "OK" in ln or "SUCCESS" in ln or "no issues" in ln or "complete" in ln: col = "#a6e3a1"
        elif "FAILED" in ln or "!!" in ln or "503" in ln or "Traceback" in ln: col = "#f38ba8"
        elif ln.startswith(">>"): col = "#f9e2af"
        d.text((pad, y), ln, font=font, fill=col); y += lh
    im.save(os.path.join(OUT, png_name))

if __name__ == "__main__":
    architecture()
    term(f"{HERE}/evidence/01_lint_test.txt", "term_tests.png", "app/ - lint and unit tests")
    term(f"{HERE}/evidence/02_terraform.txt", "term_terraform.png", "terraform/ - fmt, init, validate")
    term(f"{HERE}/evidence/03_health_nodb.txt", "term_health.png", "app running with gunicorn - /health")
    term(f"{HERE}/rollback-simulation.txt", "term_rollback.png", "scripts/deploy.sh - rollback simulation")
