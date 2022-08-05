import pandas as pd
import torch

from classifier.features.__main__ import Main as Runner
from classifier.util import timing
from .._neural.util import get_device

META_ID: str = 'metacritic_id'
META_COLS: list = ['metascore', 'userscore']


class Main(Runner):

    #  -------- __init__ -----------
    #
    def __init__(self):
        super().__init__()

        # load and encode metacritic information
        self.metacritic = pd.read_csv(self.config['model']['hybrid']['metacritic_path'])
        self.encoder.df_encode(self.metacritic, col='summary', label=self.config['model']['hybrid']['metacritic_path'])

        # match metacritic into datasets
        for data_label, dataset in self.data.items():
            self.match(dataset.data)
            dataset.data[[dataset.target_label, META_ID]].to_csv(f'{self.config["out_path"]}meta.{data_label}.csv')

    #  -------- __call__ -----------
    #
    def __call__(self, *args) -> None:
        super(
            type(self).__bases__[0], self
        ).__call__(
            # IMDb & metacritic embedding + features pipeline (variable) + META_COLS
            2 * int(self.encoder.dim) + len(self.pipeline.col_names) + len(META_COLS),
            self.__collation_fn
        )

    #
    #
    #  -------- __collation_fn -----------
    #
    def __collation_fn(self, batch: list) -> tuple:
        return (
            torch.concat([
                self.collate_encoder(batch),
                self.collate_features(batch),
                self.collate_meta_features(batch),
                self.collate_meta_encoder(batch)
            ], dim=1),
            self.collate_target_label(batch)
        )

    #
    #
    #  -------- collate_meta_features -----------
    #
    def collate_meta_features(self, batch: list) -> torch.Tensor:
        return torch.stack([
            (
                torch.tensor(
                    self.metacritic.iloc[sample[META_ID]][META_COLS].values,
                    device=get_device()
                )
                .squeeze()
                .float()
            ) for sample in batch
        ])

    #
    #
    #  -------- collate_meta_encoder -----------
    #
    def collate_meta_encoder(self, batch: list) -> torch.Tensor:
        return torch.stack([
            self.metacritic.iloc[sample[META_ID]][self.encoder.col_name].values[0]
            for sample in batch
        ]).to(get_device())

    #
    #
    #  -------- match -----------
    #
    @timing
    def match(self, data: pd.DataFrame) -> None:
        pool = torch.stack(self.metacritic[self.encoder.col_name].tolist()).float().to(get_device())

        data[META_ID] = data.apply(
            lambda row: torch.norm(
                pool - row[self.encoder.col_name].to(get_device()).unsqueeze(0),
                dim=1
            )
            .argmin()
            .item(),
            axis=1
        )


#
#
#  -------- __main__ -----------
#
if __name__ == "__main__":
    Main()()
