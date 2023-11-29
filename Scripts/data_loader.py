import torch
import librosa
import numpy as np
import h5py
from torch.utils.data import Dataset, DataLoader
from config import PARAS

"""
Be careful:
We use log mel-spectrogram for training,
while the mask generated is for power mel-spectrogram
"""


def create_binary_mask(vocal_spec, bg_spec):
    """
    Take in log spectrogram and return a mask map for TF bins
    1 if the vocal sound is dominated in the TF-bin, while 0 for not
    """
    vocal_spec = vocal_spec.numpy()
    bg_spec = bg_spec.numpy()
    return np.array(vocal_spec > bg_spec, dtype=np.float32)


def create_scale_mask(vocal_spec, bg_spec):
    """
    Take in log spectrogram and return a mask map for TF bins
    1 if the vocal sound is dominated in the TF-bin, while 0 for not
    """
    vocal_spec = librosa.db_to_power(vocal_spec.numpy())
    bg_spec = librosa.db_to_power(bg_spec.numpy())
    return np.array(vocal_spec / (vocal_spec+bg_spec), dtype=np.float32)


class TorchData(Dataset):

    def __init__(self, dataset_path):
        """
        Take the h5py dataset
        """
        super(TorchData, self).__init__()
        self.dataset = h5py.File(dataset_path, 'r')
        self.bg = self.dataset['bg']
        self.vocal = self.dataset['vocal']
        self.mix = self.dataset['mix']
        self.len = self.bg.shape[0]

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        bg = self.bg[index].astype(np.float32)
        vocal = self.vocal[index].astype(np.float32)
        mix = self.mix[index].astype(np.float32)

        mix = torch.from_numpy(mix)
        bg = torch.from_numpy(bg)
        vocal = torch.from_numpy(vocal)
        binary_target = torch.from_numpy(create_binary_mask(vocal, bg))
        mask_target = torch.from_numpy(create_scale_mask(vocal, bg))

        sample = {
            'vocal': vocal,  # this is used for test
            'bg': bg,  # this is used for test
            'mix': mix,
            'binary_mask': binary_target,
            'scale_mask': mask_target,
        }

        return sample


# define the data loaders
def torch_dataset_loader(dataset, batch_size, shuffle, kwargs):
    """
    take the h5py dataset
    """
    loader = DataLoader(TorchData(dataset),
                        batch_size=batch_size,
                        shuffle=shuffle,
                        **kwargs)
    return loader


if __name__ == '__main__':
    test_loader = torch_dataset_loader(PARAS.DATASET_PATH+'test.h5', PARAS.BATCH_SIZE, True, PARAS.kwargs)

    for index, data_item in enumerate(test_loader):
        print(data_item['vocal'].shape)
        print(data_item['bg'].shape)
        print(data_item['mix'].shape)
        print(data_item['binary_mask'].shape)
        break
