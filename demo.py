import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import math
import random
import numpy as np

seed = 42
torch.manual_seed(seed)
np.random.seed(seed)
random.seed(seed)

sentences = [
    "kedi süt içti",
    "köpek su içti",
    "çocuk top oynadı",
    "anne yemek pişirdi",
    "adam kitap okudu",
    "kedi uyudu",
    "köpek havladı",
    "çocuk süt içti",
]

PAD = "<pad>"
BOS = "<bos>"
EOS = "<eos>"

# Vocab oluştur
tokens = set()
for s in sentences:
    tokens.update(s.split())

vocab = [PAD, BOS, EOS] + sorted(list(tokens))
stoi = {w: i for i, w in enumerate(vocab)}
itos = {i: w for w, i in stoi.items()}
vocab_size = len(vocab)

print(f"Vocab ({vocab_size} kelime): {vocab}")

def encode(s):
    toks = [BOS] + s.split() + [EOS]
    return [stoi[t] for t in toks]

encoded = [encode(s) for s in sentences]
max_len = max(len(x) for x in encoded)

def pad(seq, max_len):
    return seq + [stoi[PAD]] * (max_len - len(seq))

padded = [pad(seq, max_len) for seq in encoded]

# Girdi/çıktı çiftleri oluştur (autoregressive)
class NextTokenDataset(Dataset):
    def __init__(self, sequences):
        self.x = [torch.tensor(seq[:-1], dtype=torch.long) for seq in sequences]
        self.y = [torch.tensor(seq[1:], dtype=torch.long) for seq in sequences]
    def __len__(self): return len(self.x)
    def __getitem__(self, idx): return self.x[idx], self.y[idx]

dataset = NextTokenDataset(padded)
dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=100):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.pe = pe.unsqueeze(0)
    def forward(self, x):
        return x + self.pe[:, :x.size(1)].to(x.device)

class TinyTransformerLM(nn.Module):
    def __init__(self, vocab_size, d_model=6, nhead=2, num_layers=2, dim_ff=128, max_len=5):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model) # x'in embedding'lerin içeriği boş ise random değer üretiyor. Doluysa mevcut değerler üzerinden hesaplama yapıyor
        self.pos_enc = PositionalEncoding(d_model, max_len)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_ff)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.ln = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)
    def forward(self, x):
        emb = self.embed(x) * math.sqrt(self.embed.embedding_dim)
        emb = self.pos_enc(emb)
        out = self.encoder(emb.transpose(0,1)).transpose(0,1)
        out = self.ln(out)
        return self.head(out)

device = "cpu"
model = TinyTransformerLM(vocab_size).to(device)
criterion = nn.CrossEntropyLoss(ignore_index=stoi[PAD])
optimizer = optim.AdamW(model.parameters(), lr=1e-3)

epochs = 10
for epoch in range(1, epochs + 1):
    total_loss = 0
    for xb, yb in dataloader:
        xb, yb = xb.to(device), yb.to(device)
        logits = model(xb)
        loss = criterion(logits.view(-1, vocab_size), yb.view(-1))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch}: Loss = {total_loss / len(dataloader):.4f}")

model.eval()
with torch.no_grad():
    for seq_idx in range(len(padded)):
        inp = torch.tensor(padded[seq_idx][:-1]).unsqueeze(0)
        logits = model(inp)
        probs = torch.softmax(logits, dim=-1)
        pred = probs.argmax(dim=-1).squeeze(0).tolist()

        print("\nGirdi :", [itos[i] for i in inp.squeeze(0).tolist()])
        print("Gerçek:", [itos[i] for i in padded[seq_idx][1:]])
        print("Tahmin:", [itos[i] for i in pred])
