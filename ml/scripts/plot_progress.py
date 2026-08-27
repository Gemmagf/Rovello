"""
Genera una gràfica de l'evolució d'un entrenament a partir de metrics.json.

Ús:
    python ml/scripts/plot_progress.py                            # llegeix ml/models/convnext_t_v1
    python ml/scripts/plot_progress.py --run dinov2_b_v1
    python ml/scripts/plot_progress.py --watch 60                 # re-genera cada 60s

Sortida: ml/models/<run>/progress.png
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / "ml" / "models"


def plot(run_dir: Path) -> Path:
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(f"No existeix {metrics_path}")
    with open(metrics_path) as f:
        m = json.load(f)
    history = m.get("history", [])
    if not history:
        raise RuntimeError("metrics.json sense història (cap època acabada encara)")

    epochs = [h["epoch"] for h in history]
    train_loss = [h["train"]["loss"] for h in history]
    train_top1 = [h["train"]["top1"] for h in history]
    val_loss = [h["val"]["loss"] for h in history]
    val_top1 = [h["val"]["top1"] for h in history]
    val_top5 = [h["val"]["top5"] for h in history]
    val_macro = [h["val"].get("macro_acc", 0.0) for h in history]
    times_min = [h.get("time_s", 0) / 60 for h in history]

    best_top1 = m.get("best_val_top1", max(val_top1))
    test = m.get("test")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle(
        f"Rovello — {run_dir.name}\n"
        f"època actual: {epochs[-1]}  |  millor val_top1: {best_top1:.3f}"
        + (f"  |  TEST top1: {test['top1']:.3f}" if test else ""),
        fontsize=13, fontweight="bold",
    )

    # Loss
    ax = axes[0][0]
    ax.plot(epochs, train_loss, "o-", label="train", color="#3b82f6")
    ax.plot(epochs, val_loss, "s-", label="val", color="#ef4444")
    ax.set_title("Loss")
    ax.set_xlabel("època"); ax.set_ylabel("loss")
    ax.legend(); ax.grid(alpha=0.3)

    # Accuracy
    ax = axes[0][1]
    ax.plot(epochs, train_top1, "o-", label="train top1", color="#3b82f6")
    ax.plot(epochs, val_top1, "s-", label="val top1", color="#ef4444")
    ax.plot(epochs, val_top5, "^-", label="val top5", color="#10b981")
    ax.plot(epochs, val_macro, "d--", label="val macro", color="#f59e0b", alpha=0.7)
    ax.axhline(best_top1, color="#ef4444", linestyle=":", alpha=0.4,
               label=f"best={best_top1:.3f}")
    ax.set_title("Accuracy")
    ax.set_xlabel("època"); ax.set_ylabel("accuracy")
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right"); ax.grid(alpha=0.3)

    # Temps per època
    ax = axes[1][0]
    bars = ax.bar(epochs, times_min, color="#8b5cf6", alpha=0.7)
    avg = sum(times_min) / len(times_min)
    ax.axhline(avg, color="#1f2937", linestyle="--", alpha=0.5, label=f"mitjana {avg:.1f}min")
    ax.set_title("Temps per època (min)")
    ax.set_xlabel("època"); ax.set_ylabel("minuts")
    ax.legend(); ax.grid(alpha=0.3, axis="y")
    for b, v in zip(bars, times_min):
        ax.text(b.get_x() + b.get_width()/2, v, f"{v:.0f}",
                ha="center", va="bottom", fontsize=8)

    # Resum text
    ax = axes[1][1]
    ax.axis("off")
    last = history[-1]
    txt = [
        f"Run:  {run_dir.name}",
        f"Èpoques completades:  {len(history)}",
        f"",
        f"Última època:",
        f"  train_loss = {last['train']['loss']:.3f}",
        f"  train_top1 = {last['train']['top1']:.3f}",
        f"  val_loss   = {last['val']['loss']:.3f}",
        f"  val_top1   = {last['val']['top1']:.3f}",
        f"  val_top5   = {last['val']['top5']:.3f}",
        f"  val_macro  = {last['val'].get('macro_acc', 0):.3f}",
        f"",
        f"Millor val_top1: {best_top1:.3f}",
        f"Temps total:     {sum(times_min):.1f} min  ({sum(times_min)/60:.1f} h)",
        f"Mitjana / època: {avg:.1f} min",
    ]
    if test:
        txt += [
            "",
            f"=== TEST FINAL ===",
            f"  top1 = {test['top1']:.4f}",
            f"  top5 = {test['top5']:.4f}",
            f"  macro_acc = {test.get('macro_acc', 0):.4f}",
        ]
    ax.text(0.02, 0.98, "\n".join(txt), va="top", ha="left", family="monospace",
            fontsize=10, transform=ax.transAxes)

    plt.tight_layout()
    out = run_dir / "progress.png"
    plt.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="convnext_t_v1",
                        help="Nom del run (carpeta dins ml/models/)")
    parser.add_argument("--watch", type=int, default=0,
                        help="Re-genera la gràfica cada N segons (0 = un cop)")
    args = parser.parse_args()

    run_dir = MODELS_DIR / args.run
    if not run_dir.exists():
        print(f"ERROR: {run_dir} no existeix", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            out = plot(run_dir)
            print(f"[{time.strftime('%H:%M:%S')}] Gràfica guardada: {out}")
        except (FileNotFoundError, RuntimeError) as e:
            print(f"[{time.strftime('%H:%M:%S')}] {e}")
        if args.watch <= 0:
            break
        time.sleep(args.watch)


if __name__ == "__main__":
    main()
