# -*- coding: utf-8 -*-
"""autoencoder_timeseries.anomaly.shitdone

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Lgah59vaMmOhR9a84Seq8m2gEt-2yteB
"""

### detect anamoly in patient heartbeat

!gdown --id 16MIleqoIr1vYxlGk4GKnGmrsCPuWkkpT
!unzip -qq ECG5000.zip

!pip install pandas liac-arff

import numpy as np
import arff as a2p
import torch
import pandas as pd

device = 'cuda' if torch.cuda.is_available() else 'cpu'
device

with open('ECG5000_TRAIN.arff', 'r') as f:
    train = a2p.load(f)

with open('ECG5000_TEST.arff', 'r') as f:
    test = a2p.load(f)

type(train)

train.keys()

print(train['description'])
print(train['relation'])
print(train['data'])
print(train['attributes'])

train_columns = [attr[0] for attr in train['attributes']]
train_data = [row for row in train['data']]
test_columns = [attr[0] for attr in test['attributes']]
test_data = [row for row in test['data']]

all_data = train_data + test_data

df = pd.DataFrame(all_data, columns=train_columns)

df.head()

df.shape

CLASS_NORMAL = 1

class_names = ['Normal', 'R on T', 'PVC', 'SP', 'UB']

new_columns = list(df.columns)
new_columns[-1] = 'target'
df.columns = new_columns
df.head()

np.unique(df['target'])

df.target.value_counts()

import matplotlib.pyplot as plt
import seaborn as sns

sns.countplot(df['target'])
plt.show()

normal_df = df[df.target == str(CLASS_NORMAL)].drop(labels="target", axis=1)
normal_df.shape

anomly_df = df[df.target != str(CLASS_NORMAL)].drop(labels="target", axis=1)
anomly_df.shape

from sklearn.model_selection import train_test_split

train_df, test_df = train_test_split(normal_df, test_size=0.15, random_state=42)
val_df, test_df = train_test_split(test_df, test_size=0.5, random_state=42)

### normal data

train_df.shape, val_df.shape, test_df.shape

df.dtypes

def create_dataset(df):
  sequences = df.astype(np.float32).to_numpy().tolist()
  dataset = [torch.tensor(s).unsqueeze(1).float() for s in sequences]
  n_seq, seq_len, n_features = torch.stack(dataset).shape
  return dataset, seq_len, n_features

train_dataset, seq_len, n_features = create_dataset(train_df)
val_dataset, _, _ = create_dataset(val_df)
test_normal_dataset, _, _ = create_dataset(test_df)
test_anomly_dataset, _, _ = create_dataset(anomly_df)

seq_len, n_features

from torch import nn

class Encoder(nn.Module):
  def __init__(self, seq_len, n_features, embedding_dim=64):
    super(Encoder, self).__init__()

    self.seq_len, self.n_features = seq_len, n_features
    self.embedding_dim, self.hidden_dim = embedding_dim, 2 * embedding_dim

    self.rnn1 = nn.LSTM(
        input_size=n_features,
        hidden_size=self.hidden_dim,
        num_layers=1,
        batch_first=True
    )

    self.rnn2 = nn.LSTM(
        input_size=self.hidden_dim,
        hidden_size=embedding_dim,
        num_layers=1,
        batch_first=True
    )

  def forward(self, x):
    x = x.reshape((1, self.seq_len, self.n_features))
    x, (_, _) = self.rnn1(x)
    x, (hidden_n, _) = self.rnn2(x)
    return hidden_n.reshape((self.n_features, self.embedding_dim))

class Decoder(nn.Module):

  def __init__(self, seq_len, input_dim=64, n_features=1):
    super(Decoder, self).__init__()
    self.seq_len, self.input_dim = seq_len, input_dim
    self.hidden_dim, self.n_features = 2 * input_dim, n_features

    self.rnn1 = nn.LSTM(
        input_size=input_dim,
        hidden_size=input_dim,
        num_layers=1,
        batch_first=True
    )

    self.rnn2 = nn.LSTM(
        input_size=input_dim,
        hidden_size=self.hidden_dim,
        num_layers=1,
        batch_first=True
    )
    self.output_layer = nn.Linear(self.hidden_dim, n_features)

  def forward(self, x):
    x = x.repeat(self.seq_len, self.n_features)
    x = x.reshape((self.n_features, self.seq_len, self.input_dim))

    x, (hidden_n, cell_n) = self.rnn1(x)
    x, (hidden_n, cell_n) = self.rnn2(x)
    x.reshape((self.seq_len, self.hidden_dim))

    return self.output_layer(x)

class RecurrentAutoencoder(nn.Module):

  def __init__(self, seq_len, n_features, embedding_dim=64):
    super(RecurrentAutoencoder, self).__init__()
    self.encoder = Encoder(seq_len, n_features, embedding_dim).to(device)
    self.decoder = Decoder(seq_len, embedding_dim, n_features).to(device)

  def forward(self, x):
    x = self.encoder(x)
    x = self.decoder(x)

    return x

model = RecurrentAutoencoder(seq_len, n_features, 128).to(device)

import copy

def train_model(model, train_dataset, val_dataset, n_epochs):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.L1Loss(reduction='sum').to(device)
    history = dict(train=[], val=[])

    best_model_wts = copy.deepcopy(model.state_dict())
    best_loss = float('inf')

    for epoch in range(1, n_epochs + 1):
        model = model.train()
        train_losses = []

        for seq_true in train_dataset:
            optimizer.zero_grad()

            seq_true = seq_true.to(device)
            seq_pred = model(seq_true)
            loss = criterion(seq_pred, seq_true)

            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())

        val_losses = []
        model = model.eval()

        with torch.no_grad():
            for seq_true in val_dataset:
                seq_true = seq_true.to(device)
                seq_pred = model(seq_true)

                loss = criterion(seq_pred, seq_true)
                val_losses.append(loss.item())

        train_loss = np.mean(train_losses)
        val_loss = np.mean(val_losses)

        history['train'].append(train_loss)
        history['val'].append(val_loss)

        if val_loss < best_loss:
            best_loss = val_loss
            best_model_wts = copy.deepcopy(model.state_dict())

        print(f'Epoch {epoch}: train loss {train_loss} val loss {val_loss}')

    model.load_state_dict(best_model_wts)
    return model.eval(), history

model, history = train_model(model, train_dataset, val_dataset, 50)

model_path = 'model.pth'
torch.save(model, model_path)

import matplotlib.pyplot as plt

plt.plot(history['train'], label='Training Loss')
plt.plot(history['val'], label='Validation Loss')
plt.title('Training and Validation Loss over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

def predict(model, dataset):
  prediction, losses = [], []
  criterion = nn.L1Loss(reduction='sum').to(device)

  with torch.no_grad():
    for seq_true in dataset:
      seq_true = seq_true.to(device)
      seq_pred = model(seq_true)
      loss = criterion(seq_pred, seq_true)

      prediction.append(seq_pred.cpu().numpy())
      losses.append(loss.item())

  return prediction, losses

_, losses = predict(model, train_dataset)
sns.displot(losses, bins=50, kde=True)

THRESHOLD = 26

predictions, pred_losses = predict(model, test_normal_dataset)
sns.displot(pred_losses, bins=50, kde=True)

correct = sum(1<= THRESHOLD for loss in pred_losses)
print(f'Number of correct predictions: {correct}/{len(test_normal_dataset)}')

#### now check the prediction for the anomolies
anamoly_dataset = test_anomly_dataset[:len(test_normal_dataset)]
predictions, pred_losses = predict(model, anamoly_dataset)
sns.displot(pred_losses, bins=50, kde=True)

correct = sum(1<= THRESHOLD for loss in pred_losses)
print(f'Number of correct predictions: {correct}/{len(anamoly_dataset)}')

