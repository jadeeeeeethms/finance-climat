import pandas as pd
from pathlib import Path

def load_and_process_itr_data():
    """
    Charge les données ITR depuis le dossier data/itr/ et extrait les métriques clés.
    """
    base_dir = Path(__file__).resolve().parent.parent / "data" / "itr"

    try:
        assets = pd.read_csv(base_dir / "itr_assets_data.csv", sep=";")
        sector = pd.read_csv(base_dir / "itr_sector_indicator.csv", sep=";")
        asset_class = pd.read_csv(base_dir / "itr_asset_class_indicator.csv", sep=";")
        coverage = pd.read_csv(base_dir / "itr_coverage_metrics.csv", sep=";")
        summary_raw = pd.read_csv(base_dir / "itr_summary.csv", sep=";")

        summary = summary_raw.set_index("metric")["value"]

        portfolio_itr = float(summary.get("portfolio_itr", 0.0))
        baseline_temp = float(summary.get("scenario_baseline", 1.5))
        weighted_dqs = float(summary.get("weighted_dqs", 0.0))

        return {
            "success": True,
            "assets": assets,
            "sector": sector,
            "asset_class": asset_class,
            "coverage": coverage,
            "portfolio_itr": portfolio_itr,
            "baseline_temp": baseline_temp,
            "weighted_dqs": weighted_dqs
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error": "Les fichiers CSV sont introuvables. Vérifiez qu'ils sont bien dans data/itr/."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors du chargement des données ITR : {e}"
        }
