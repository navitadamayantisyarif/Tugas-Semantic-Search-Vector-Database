# Semantic Search & Vector Database

## Project Information

- **Nama project:** Semantic Search Konsep Pemrograman
- **Tema dataset:** Bahasa pemrograman, backend, frontend, dan database
- **Deskripsi:** API pencarian yang mengambil konsep pemrograman berdasarkan kemiripan makna, bukan hanya kecocokan kata.

## Dataset

- **Jumlah data:** 26
- **Kategori:** `bahasa-pemrograman`, `backend`, `frontend`, `database`
- **Alasan memilih dataset:** Topik pemrograman dekat dengan materi project, dan istilah teknisnya cocok untuk membandingkan pencarian kata dengan pencarian berdasarkan makna.

Data sumber ada di [`data.py`](./data.py). Setiap item memiliki `text` dan `category`.

## Tech Stack

- Python
- FastAPI dan Pydantic
- SentenceTransformers: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Qdrant Client dengan penyimpanan lokal persisten

## Application Flow

Saat indexing, aplikasi mengubah teks setiap dokumen menjadi embedding dengan SentenceTransformer. Vector beserta teks dan kategorinya disimpan sebagai payload di collection Qdrant. Saat pencarian, query diubah menjadi vector dengan model yang sama. Qdrant membandingkan vector query terhadap vector tersimpan menggunakan cosine similarity dan mengembalikan hasil terdekat sebanyak `top_k`.

Embedding mewakili makna teks sebagai kumpulan angka. Qdrant menyimpan dan mengambil vector berdasarkan kedekatan makna, sementara payload mempertahankan teks dan kategori agar hasilnya dapat dibaca.

## Menjalankan Aplikasi

Aktifkan virtual environment, lalu jalankan:

```powershell
fastapi dev main.py
```

Pada pemakaian pertama, model embedding diunduh dari Hugging Face. Buka dokumentasi interaktif di <http://127.0.0.1:8000/docs>.

```powershell
curl.exe -X POST http://127.0.0.1:8000/index
```

```powershell
curl.exe -X POST http://127.0.0.1:8000/search `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"framework Python untuk backend web\",\"top_k\":3}"
```

## API Endpoint

| Method | Path | Fungsi |
|---|---|---|
| `GET` | `/health` | Memeriksa status aplikasi dan model |
| `POST` | `/index` | Index dataset bawaan; menerima `{"documents":[{"text":"...","category":"..."}]}` untuk dataset pilihan |
| `POST` | `/search` | Mencari data semantik; menerima `{"query":"...","top_k":3}` |

`top_k` bernilai 1 sampai 50 dan default-nya 3. Panggil `/index` setidaknya sekali sebelum `/search`. Collection disimpan di `qdrant_data/`, yang tidak perlu dimasukkan ke repository.

## Example Request dan Response

Request yang digunakan:

```json
{
  "query": "framework Python untuk membuat layanan web",
  "top_k": 3
}
```

Response aktual dan hasil experiment di bawah ini berasal dari pemanggilan endpoint aplikasi.

Contoh response aktual:

```json
{
  "query": "framework Python untuk membuat layanan web",
  "results": [
    {
      "text": "Flask adalah framework web Python yang ringan dan memberi kebebasan untuk memilih komponen aplikasi.",
      "category": "backend",
      "score": 0.5825
    },
    {
      "text": "Python adalah bahasa pemrograman yang mudah dibaca dan banyak digunakan untuk otomasi, analisis data, dan kecerdasan buatan.",
      "category": "bahasa-pemrograman",
      "score": 0.5408
    },
    {
      "text": "Django menyediakan banyak fitur bawaan seperti autentikasi, ORM, dan panel admin untuk aplikasi web Python.",
      "category": "backend",
      "score": 0.5137
    }
  ]
}
```

## Experiment 1 - Semantic Search

Skor adalah cosine similarity yang dikembalikan Qdrant. Query dibuat berbeda dari kalimat dataset.

| Query | Top result | Score | Penilaian |
|---|---|---:|---|
| Bahasa yang cocok untuk mengolah data dan membuat sistem pintar | Python untuk otomasi, analisis data, dan kecerdasan buatan | 0.5828 | Relevan; deskripsi Python menyebut analisis data dan AI. |
| Cara membuat situs bisa merespons klik pengguna | JavaScript untuk membuat halaman web interaktif | 0.5649 | Relevan; interaksi halaman berkaitan dengan perilaku yang dipicu pengguna. |
| Alat untuk menyimpan informasi dan mencarinya kembali secara terstruktur | Redis untuk menyimpan data dalam memori | 0.5090 | Sebagian relevan; Redis menyimpan data, tetapi query kurang spesifik dan hasil database relasional tidak muncul di posisi pertama. |
| Program di sisi server untuk menerima permintaan dari aplikasi | REST API dengan sumber daya dan metode HTTP | 0.4805 | Cukup relevan; REST API menjelaskan cara aplikasi berkomunikasi, walau bukan framework server tertentu. |
| Bagaimana mempercepat aplikasi dengan menyimpan jawaban yang sering dipakai | Caching untuk menyimpan hasil yang sering diminta | 0.7182 | Sangat relevan; hasil menyebut caching, penyimpanan hasil, dan respons lebih cepat. |

## Experiment 2 - Top-K

- **Query:** Framework Python untuk membuat layanan web
- **Top-K = 1:** Flask (backend), skor `0.5825`.
- **Top-K = 3:** Flask (`0.5825`), Python (`0.5408`), Django (`0.5137`).
- **Top-K = 5:** Flask (`0.5825`), Python (`0.5408`), Django (`0.5137`), FastAPI (`0.4854`), HTML (`0.4309`).

Ketika Top-K diperbesar, aplikasi mengembalikan lebih banyak kandidat dengan skor yang semakin rendah atau sama. Flask, Django, dan FastAPI adalah framework yang sesuai, tetapi Python dan HTML merupakan hasil yang lebih umum/kurang tepat untuk query tersebut. Jadi, menambah Top-K memberi lebih banyak opsi tetapi tidak otomatis membuat semua hasil lebih relevan.

## Experiment 3 - Bad Retrieval

- **Query:** Siapa yang memenangkan pertandingan sepak bola tadi malam?
- **Actual results dan similarity score:**
  1. Node.js untuk layanan jaringan di sisi server — `0.0561`
  2. PostgreSQL untuk database relasional — `0.0434`
  3. Qdrant untuk pencarian vector — `0.0280`
- **Analisis:** Tidak ada hasil yang menjawab pertanyaan tentang pertandingan sepak bola. Dataset hanya berisi konsep pemrograman, tetapi vector search tetap mengurutkan kandidat yang tersedia. Skor yang rendah menunjukkan bahwa kandidat tersebut tidak mirip dengan query; aplikasi produksi dapat mempertimbangkan ambang skor agar hasil yang sangat tidak relevan tidak ditampilkan.

## Personal Reflection

1. Sebelum memahami semantic search, saya membayangkan mesin pencari terutama mencocokkan kata yang diketik dengan kata yang tersimpan. Pada project ini, query yang memakai ungkapan berbeda tetap dapat menemukan konsep yang maknanya berdekatan.
2. Keyword search mencari kecocokan istilah, sedangkan semantic search membandingkan representasi makna. Semantic search lebih toleran terhadap parafrasa, tetapi hasilnya masih bergantung pada model dan isi dataset.
3. Embedding mengubah teks menjadi vector numerik sehingga kemiripan makna dapat dihitung dan dibandingkan.
4. List Python cukup untuk contoh kecil, tetapi tidak menyediakan pencarian vector dan pengelolaan data besar secara efisien seperti vector database.
5. Tantangan utama project ini adalah memahami alur yang menghubungkan hasil encoding, ukuran vector, collection Qdrant, dan payload, lalu membaca hasil yang tidak selalu relevan seperti kandidat Redis pada query penyimpanan data.
6. AI membantu menyusun kerangka API, validasi request, indexing, serta dokumentasi. Model embedding dan hasil pencarian tetap diuji melalui endpoint.
7. Endpoint indexing meng-encode dokumen dan menyimpan vector serta payload ke Qdrant. Endpoint search meng-encode query, meminta vector terdekat, lalu mengembalikan teks, kategori, dan skor.
8. Project ini dapat dikembangkan menjadi pencarian dokumentasi teknis atau katalog produk dengan dataset yang sesuai dan evaluasi relevansi yang lebih luas.

## AI Usage

- **AI tools:** GitHub Copilot.
- **Bantuan AI:** Menyusun struktur aplikasi, validasi request, integrasi embedding dengan Qdrant, serta draf dokumentasi dan skenario pengujian.
- **Penyesuaian/validasi:** Dataset konsep pemrograman disusun untuk project ini; aplikasi dijalankan dan query eksperimen dikirim melalui API untuk memeriksa hasil aktual.

## Batasan

Hasil pencarian dibatasi pada isi dataset kecil yang tersedia dan tidak menjawab pertanyaan faktual di luar cakupannya. Score cosine similarity membantu mengurutkan kandidat, tetapi bukan jaminan bahwa hasil benar atau relevan untuk setiap query.
