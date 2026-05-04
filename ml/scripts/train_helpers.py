"""
Helpers compartits entre entrenament i inferència.

Conté la lògica de construcció de models perquè el backend pugui reconstruir
l'arquitectura abans de carregar els pesos del checkpoint.
"""
from __future__ import annotations

import torch
import torch.nn as nn


def build_model_for_inference(backbone: str, num_classes: int) -> nn.Module:
    """Construeix l'arquitectura sense carregar pesos pre-entrenats.

    Útil per a inferència: el backbone pretrained=False i després es carrega
    el state_dict del checkpoint.
    """
    backbone = backbone.lower()

    if backbone in ("convnext_tiny", "convnext_small"):
        from torchvision import models as tvm
        if backbone == "convnext_tiny":
            m = tvm.convnext_tiny(weights=None)
        else:
            m = tvm.convnext_small(weights=None)
        in_feat = m.classifier[2].in_features
        m.classifier[2] = nn.Linear(in_feat, num_classes)
        return m

    if backbone == "efficientnetv2_s":
        from torchvision import models as tvm
        m = tvm.efficientnet_v2_s(weights=None)
        in_feat = m.classifier[1].in_features
        m.classifier[1] = nn.Linear(in_feat, num_classes)
        return m

    if backbone == "vit_b_16":
        from torchvision import models as tvm
        m = tvm.vit_b_16(weights=None)
        in_feat = m.heads.head.in_features
        m.heads.head = nn.Linear(in_feat, num_classes)
        return m

    if backbone.startswith("dinov2_"):
        repo = "facebookresearch/dinov2"
        if backbone == "dinov2_vits14_lc":
            base = torch.hub.load(repo, "dinov2_vits14")
            embed_dim = 384
        elif backbone == "dinov2_vitb14_lc":
            base = torch.hub.load(repo, "dinov2_vitb14")
            embed_dim = 768
        elif backbone == "dinov2_vitl14_lc":
            base = torch.hub.load(repo, "dinov2_vitl14")
            embed_dim = 1024
        else:
            raise ValueError(f"DINOv2 variant unknown: {backbone}")

        class DinoClassifier(nn.Module):
            def __init__(self, base, embed_dim, num_classes):
                super().__init__()
                self.base = base
                self.head = nn.Sequential(
                    nn.LayerNorm(embed_dim),
                    nn.Linear(embed_dim, num_classes),
                )

            def forward(self, x):
                feats = self.base(x)
                return self.head(feats)

        return DinoClassifier(base, embed_dim, num_classes)

    raise ValueError(f"Backbone desconegut: {backbone}")
