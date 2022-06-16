from typing import Union

import torch
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm


#
#
#  -------- get_device -----------
#
def get_device() -> str:
    return f"cuda:{torch.cuda.current_device()}" if torch.cuda.is_available() else "cpu"


#
#
#  -------- unpad -----------
#
def unpad(padded: Union[list, torch.Tensor], length: Union[list, torch.Tensor]) -> Union[list, torch.Tensor]:
    """Convert the given packaged sequence into a list of vectors."""
    output = []
    for v, n in zip(padded, length):
        output.append(v[:n])
    return output

#
#
#  -------- load_iterator -----------
#
def load_iterator(
        data: Dataset,
        collate_fn: callable = lambda x: x,
        batch_size: int = 8,
        shuffle: bool = False,
        num_workers: int = 0,
        desc: str = "",
        disable: bool = False):
    return enumerate(tqdm(DataLoader(
        data,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn
    ),
        leave=False,
        desc=desc,
        disable=disable,
    ))
