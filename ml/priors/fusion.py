"""
Fusió bayesiana entre la predicció del CNN i el prior geo-temporal.

Ús típic des del backend Flask:

    from ml.priors.fusion import GeoTemporalPrior

    prior = GeoTemporalPrior.load("ml/priors/geo_temporal_prior.pkl")
    fused = prior.fuse(image_probs, month=11, lat=41.6, lon=2.3, alpha=1.0, beta=0.5)
    # fused és un np.ndarray amb la distribució posterior re-normalitzada
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Optional

import numpy as np


class GeoTemporalPrior:
    def __init__(self, species_list, kdes, kde_global, counts, bandwidth, laplace_alpha):
        self.species_list = species_list
        self.kdes = kdes
        self.kde_global = kde_global
        self.counts = counts
        self.bandwidth = bandwidth
        self.laplace_alpha = laplace_alpha
        self._index = {sp: i for i, sp in enumerate(species_list)}

    @classmethod
    def load(cls, path: str | Path) -> "GeoTemporalPrior":
        with open(path, "rb") as f:
            d = pickle.load(f)
        return cls(
            species_list=d["species_list"],
            kdes=d["kdes"],
            kde_global=d["kde_global"],
            counts=d["counts"],
            bandwidth=d["bandwidth"],
            laplace_alpha=d["laplace_alpha"],
        )

    @staticmethod
    def _encode(month: int, lat: float, lon: float) -> np.ndarray:
        angle = 2 * np.pi * float(month) / 12.0
        return np.array([[float(lat), float(lon), np.sin(angle), np.cos(angle)]])

    def prior_probs(self, month: int, lat: float, lon: float) -> np.ndarray:
        """Retorna P(s | mes, lat, lon) sobre totes les espècies (re-normalitzat)."""
        x = self._encode(month, lat, lon)
        global_log = float(self.kde_global.score_samples(x)[0])
        log_priors = np.empty(len(self.species_list), dtype=np.float64)
        for i, sp in enumerate(self.species_list):
            kde = self.kdes.get(sp)
            if kde is None:
                # fallback: usa global (penalitzat per laplace)
                log_priors[i] = global_log
            else:
                log_priors[i] = float(kde.score_samples(x)[0])
        # Estabilització numèrica
        log_priors -= log_priors.max()
        priors = np.exp(log_priors) + self.laplace_alpha
        priors /= priors.sum()
        return priors

    def fuse(
        self,
        image_probs: np.ndarray,
        month: Optional[int] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        alpha: float = 1.0,
        beta: float = 0.5,
    ) -> np.ndarray:
        """Fusió log-lineal:  posterior ∝ image_probs^α · prior^β

        Si falten month/lat/lon, retorna image_probs sense modificar.
        """
        image_probs = np.asarray(image_probs, dtype=np.float64)
        if image_probs.ndim != 1 or len(image_probs) != len(self.species_list):
            raise ValueError(
                f"image_probs ha de ser 1D de mida {len(self.species_list)}, "
                f"rebut shape={image_probs.shape}"
            )
        if month is None or lat is None or lon is None or beta <= 0:
            return image_probs / max(image_probs.sum(), 1e-12)

        priors = self.prior_probs(month, lat, lon)
        # Estabilització: evita zeros
        eps = 1e-12
        log_post = alpha * np.log(image_probs + eps) + beta * np.log(priors + eps)
        log_post -= log_post.max()
        post = np.exp(log_post)
        post /= post.sum()
        return post

    def topk(
        self,
        image_probs: np.ndarray,
        k: int = 3,
        **kwargs,
    ) -> list[dict]:
        """Versió pràctica que retorna top-k amb noms i prob fusionada."""
        post = self.fuse(image_probs, **kwargs)
        idx = np.argsort(-post)[:k]
        return [
            {
                "class_index": int(i),
                "class_name": self.species_list[int(i)],
                "prob": float(post[int(i)]),
                "prior_prob": float(self.prior_probs(
                    kwargs.get("month"), kwargs.get("lat"), kwargs.get("lon"))[int(i)])
                    if (kwargs.get("month") is not None and kwargs.get("lat") is not None
                        and kwargs.get("lon") is not None and kwargs.get("beta", 0.5) > 0)
                    else None,
                "image_prob": float(image_probs[int(i)]),
            }
            for i in idx
        ]
