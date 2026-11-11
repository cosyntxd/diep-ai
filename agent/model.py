import torch.nn as nn
from torch.nn import TransformerEncoder, TransformerEncoderLayer, MultiheadAttention
import torch

from agent.parse import ModelInputProcessed

OBJECTS_MAX_COUNT = 256
OBJECT_EMBEDDING = 32
OBJECT_INPUT_DIM = 80

BOT_INPUT_DIM = 64
MODEL_OUTPUT_DIM = 32

D_MODEL = 128


class DiepModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed_object = nn.Embedding(OBJECTS_MAX_COUNT, OBJECT_EMBEDDING)
        nn.init.normal_(self.embed_object.weight, mean=0.0, std=1.0)

        self.ego_encoder = nn.Linear(BOT_INPUT_DIM, D_MODEL)
        self.obj_encoder = nn.Linear(OBJECT_INPUT_DIM, D_MODEL)

        sab_layer = TransformerEncoderLayer(
            d_model=D_MODEL,
            nhead=16,
            dim_feedforward=D_MODEL * 2,
            dropout=0.0,
            activation="gelu",
            norm_first=True
        )
        self.initial_sab = TransformerEncoder(sab_layer, num_layers=2)
        self.cross_atnn = MultiheadAttention(embed_dim=D_MODEL, num_heads=8, batch_first=True)
        self.cross_norm = nn.LayerNorm(D_MODEL)
        self.final_sab = TransformerEncoder(sab_layer, num_layers=4)

        self.global_action_head = nn.Linear(D_MODEL, MODEL_OUTPUT_DIM)
        self.pointer_query = nn.Linear(D_MODEL, D_MODEL)
        self.pointer_key = nn.Linear(D_MODEL, D_MODEL)

    def forward(self, ego_stats: torch.Tensor, objects: ModelInputProcessed) -> torch.Tensor:
        ego = self.ego_encoder(ego_stats).unsqueeze(1)  # (B, 1, D)

        types = torch.tensor(
            [t for t, _ in objects.objects],
            dtype=torch.long,
            device=ego_stats.device,
        )
        features = torch.stack([x for _, x in objects.objects]).to(
            device=ego_stats.device, dtype=ego_stats.dtype
        )

        obj = self.obj_encoder(features) + nn.functional.pad(
            self.embed_object(types),
            (0, D_MODEL - OBJECT_EMBEDDING),
        )
        obj = obj.unsqueeze(0).expand(ego.shape[0], -1, -1)
        obj = self.initial_sab(obj.transpose(0, 1)).transpose(0, 1)

        cross, _ = self.cross_atnn(ego, obj, obj, need_weights=False)
        ego = self.cross_norm(ego + cross)

        tokens = torch.cat((ego, obj), dim=1)
        tokens = self.final_sab(tokens.transpose(0, 1)).transpose(0, 1)
        ego, obj = tokens[:, 0], tokens[:, 1:]

        actions = self.global_action_head(ego)
        query = self.pointer_query(ego).unsqueeze(1)
        keys = self.pointer_key(obj)
        pointers = (query @ keys.transpose(1, 2)).squeeze(1) / D_MODEL**0.5

        return torch.cat((actions, pointers), dim=-1)
