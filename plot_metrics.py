import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_metrics.py <chemin_metrics.csv>")
        sys.exit(1)
    csv_path = sys.argv[1]
    if not os.path.isfile(csv_path):
        print(f"Fichier introuvable: {csv_path}")
        sys.exit(1)
    metrics = pd.read_csv(csv_path)

    # Moyenne glissante sur 20 épisodes
    window = 50
    metrics['score_smooth'] = metrics['score'].rolling(window, min_periods=1).mean()
    metrics['reward_smooth'] = metrics['total_reward'].rolling(window, min_periods=1).mean()
    metrics['steps_smooth'] = metrics['steps'].rolling(window, min_periods=1).mean()

    plt.figure(figsize=(12, 10))
    # Score, Reward total et Epsilon sur le même graphique
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(metrics['episode'], metrics['score_smooth'], label='Score (moyenne 50)', color='tab:blue')
    # Ajout du reward total
    ax2 = ax1.twinx()
    ax2.plot(metrics['episode'], metrics['reward_smooth'], label='Reward total (moyenne 50)', color='tab:green')
    # Ajout de l'epsilon
    if 'epsilon' in metrics.columns:
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        ax3.plot(metrics['episode'], metrics['epsilon'], label='Epsilon', color='tab:red', linestyle='dashed', alpha=0.5)
        ax3.set_ylabel('Epsilon', color='tab:red')
        ax3.tick_params(axis='y', labelcolor='tab:red')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Score', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylabel('Reward total', color='tab:green')
    ax2.tick_params(axis='y', labelcolor='tab:green')
    # Légendes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    if 'epsilon' in metrics.columns:
        lines3, labels3 = ax3.get_legend_handles_labels()
        ax1.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc='upper left')
    else:
        ax1.legend(lines + lines2, labels + labels2, loc='upper left')
    ax1.set_title('Score, Reward total et Epsilon par épisode (moyenne glissante 50)')

    # Steps
    ax4 = plt.subplot(3, 1, 2)
    ax4.plot(metrics['episode'], metrics['steps_smooth'], label='Steps (moyenne 50)', color='tab:purple')
    ax4.set_xlabel('Episode')
    ax4.set_ylabel('Steps')
    ax4.set_title('Nombre de steps par épisode (moyenne glissante 50)')
    ax4.legend()
    # Loss (si dispo)
    if 'loss_avg' in metrics.columns and metrics['loss_avg'].notnull().any():
        plt.subplot(3, 1, 3)
        plt.plot(metrics['episode'], metrics['loss_avg'], label='Loss moyenne', color='tab:orange')
        plt.xlabel('Episode')
        plt.ylabel('Loss moyenne')
        plt.title('Loss moyenne par épisode')
        plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()




