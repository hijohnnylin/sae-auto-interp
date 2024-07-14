from .model import Sae
from typing import List
from ..wrapper import AutoencoderLatents

from ..OpenAI.model import ACTIVATIONS_CLASSES, TopK
    
DEVICE = "cuda:0"

def load_eai_autoencoders(
    model, 
    ae_layers: List[int], 
    weight_dir:str
):
    submodule = {}

    for layer in ae_layers:
        path = f"{weight_dir}/layer_{layer}.pt"
        sae = Sae.load_from_disk(path, DEVICE)

        def _forward(x):
            encoded = sae.encode(x)
            trained_k = sae.cfg.k
            topk = TopK(trained_k, postact_fn=ACTIVATIONS_CLASSES["Identity"]())
            return topk(encoded)

        submodule = model.model.layers[layer]
        submodule.ae = AutoencoderLatents(_forward)

        submodule[layer] = submodule
    
    with model.edit(" "):
        for _, submodule in submodule.items():
            acts = submodule.output[0]
            submodule.ae(acts, hook=True)

    return submodule	