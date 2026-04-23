# SAP ABAP AI Assistant

Lokal GPU üzerinde Qwen Coder modelini kullanarak SAP ABAP kodu üreten, analiz eden ve SAP sistemleriyle entegre çalışan bir AI asistanı.

## 🚀 Özellikler

- **ABAP Kod Üretimi**: Senaryo bazlı ABAP programı, function module, class üretimi
- **Kod Analizi**: Performans, güvenlik ve syntax analizi
- **SAP RFC Entegrasyonu**: PyRFC ile SAP sistemlerine doğrudan bağlantı
- **abapGit Desteği**: Azure DevOps ve Git reposu yönetimi
- **Modern UI**: Kullanıcı dostu web arayüzü

## 📋 Gereksinimler

- Python 3.8+
- NVIDIA GPU (Qwen modeli için)
- 16GB+ RAM
- 20GB+ disk alanı

## 🛠️ Kurulum

### 1. Bağımlılıkları Yükle

```bash
cd backend
pip install -r requirements.txt
```

### 2. Qwen Coder Modelini İndir

```bash
# Hugging Face'den Qwen Coder modelini indirin
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
```

Veya manuel olarak:
```bash
git lfs install
git clone https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct /models/Qwen-Coder-7B-Instruct
```

### 3. Ortam Değişkenlerini Ayarla

```bash
export MODEL_PATH="/models/Qwen-Coder-7B-Instruct"
export SAP_HOST="your-sap-host"
export SAP_PORT="3300"
export SAP_CLIENT="100"
export SAP_USER="your-user"
export SAP_PASSWORD="your-password"
export AZURE_DEVOPS_REPO="https://dev.azure.com/org/project/_git/repo"
```

## 🏃‍♂️ Çalıştırma

### Backend'i Başlat

```bash
cd backend
python main.py
```

Backend `http://localhost:8000` adresinde çalışacaktır.

### Frontend'i Aç

`frontend/index.html` dosyasını tarayıcınızda açın veya bir web sunucusu kullanın:

```bash
cd frontend
python -m http.server 3000
```

Sonra `http://localhost:3000` adresine gidin.

## 📖 API Kullanımı

### ABAP Kod Üret

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "Satış siparişi oluşturma programı",
    "output_type": "program",
    "include_tests": true
  }'
```

### Kod Analizi Yap

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "abap_code": "REPORT z_test.\nWRITE: / \"Hello\".",
    "analysis_type": "all"
  }'
```

### SAP'ye Bağlan

```bash
curl -X POST http://localhost:8000/api/sap/connect \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 3300,
    "client": "100",
    "user": "SAPUSER",
    "password": "password"
  }'
```

### Git Repository Clone

```bash
curl -X POST http://localhost:8000/api/git/clone \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/abapGit/abapGit.git",
    "branch": "master"
  }'
```

## 🔧 abapGit Entegrasyonu

Bu proje abapGit repolarından ilham almıştır:

- [abapGit](https://github.com/abapGit/abapGit)
- [abap2UI](https://github.com/abap2UI/abap2UI)
- [abap-clean-code-checks](https://github.com/SAP/abap-clean-code-checks)

abapGit fonksiyonları, Git repository yönetimi için kullanılır:
- Repository clone/pull/push
- ABAP objelerini serializasyon
- Version control

## 📊 Örnek Senaryolar

### 1. Satış Siparişi Programı

```
Senaryo: Kullanıcıdan malzeme kodu ve miktar alıp BAPI_SALESORDER_CREATEFROMDAT2 
fonksiyonunu çağırarak satış siparişi oluşturan program.
```

### 2. Malzeme Master Raporu

```
Senaryo: MARA ve MARC tablolarından malzeme bilgilerini çeken, 
ALV grid'de gösteren ve Excel'e export eden rapor.
```

### 3. Custom Function Module

```
Senaryo: Verilen müşteri numarasına göre tüm satış alanlarını döndüren 
fonksiyon module. BAPI_CUSTOMER_GETDETAIL kullanacak.
```

## 🔒 Güvenlik

- SAP şifreleri environment variable'larda saklanmalı
- Production'da HTTPS kullanılmalı
- RFC yetkileri minimum privilege prensibiyle ayarlanmalı

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

MIT License

## 📞 İletişim

Proje hakkında sorularınız için issue açabilirsiniz.

---

**Not**: Bu araç geliştirme ve öğrenme amaçlıdır. Production ortamında kullanmadan önce kapsamlı test yapılmalıdır.
