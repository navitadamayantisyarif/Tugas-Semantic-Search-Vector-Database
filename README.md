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

Alur indexing:

1. Endpoint `/index` mengambil 26 dokumen dari `data.py`.
2. SentenceTransformer mengubah setiap teks menjadi vector embedding berukuran 384.
3. Aplikasi membuat collection Qdrant dengan metrik cosine, lalu menyimpan vector dan payload dokumen.

Alur pencarian:

1. Pengguna mengirim kalimat dan `top_k` ke endpoint `/search`.
2. Model yang sama mengubah query menjadi vector.
3. Qdrant mencari vector dokumen terdekat berdasarkan cosine similarity.
4. API mengembalikan teks, kategori, dan similarity score untuk setiap hasil.

Embedding adalah representasi numerik teks yang menempatkan teks bermakna mirip pada vector yang berdekatan. Qdrant bertugas menyimpan vector dan mencari tetangga terdekatnya; payload yang disimpan bersama setiap vector berisi `text` dan `category`, agar aplikasi dapat menampilkan hasil yang bisa dibaca. Tidak ada LLM yang digunakan.

## Embedding Model

Model yang digunakan adalah `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Fungsinya mengubah teks dokumen dan query menjadi embedding vector dengan representasi yang sama, sehingga kedekatan makna antara query dan dokumen dapat dihitung. Pada project ini ukuran vector model adalah 384.

## Vector Database

Qdrant menyimpan embedding dalam collection `programming_concepts` dan mencari vector dokumen yang paling dekat dengan vector query menggunakan cosine similarity. Payload setiap point menyimpan teks asli pada field `text` dan label topik pada field `category`; vector digunakan untuk pencarian, sedangkan payload menyediakan isi yang ditampilkan pada hasil.

## Menjalankan Aplikasi

Aktifkan virtual environment, lalu jalankan:

```powershell
.\venv\Scripts\Activate.ps1
fastapi dev main.py
```

Pada pemakaian pertama, model embedding diunduh dari Hugging Face. Buka dokumentasi interaktif di <http://127.0.0.1:8000/docs>.

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/index -Method Post
```

Indexing tanpa body menggunakan dataset bawaan dan mengganti isi collection agar indeks mencerminkan dataset tersebut. Endpoint juga menerima dataset sendiri:

```json
{
  "documents": [
    {
      "text": "FastAPI digunakan untuk membangun backend API.",
      "category": "backend"
    }
  ]
}
```

Jalankan indexing sebelum mencari. Database lokal disimpan di `qdrant_data/` dan diabaikan oleh Git.

```powershell
$body = @{ query = "framework Python untuk backend web"; top_k = 3 } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/search -Method Post -ContentType "application/json" -Body $body
```

## API Endpoint

| Method | Path | Fungsi |
|---|---|---|
| `GET` | `/health` | Memeriksa status aplikasi dan model |
| `POST` | `/index` | Index dataset bawaan jika body kosong; atau menerima `{"documents":[{"text":"...","category":"..."}]}` untuk dataset pilihan |
| `POST` | `/search` | Mencari data semantik; menerima `{"query":"...","top_k":3}` |

`top_k` bernilai 1 sampai 50 dan default-nya 3. Query dan teks dokumen harus tidak kosong. Jika pencarian diminta sebelum indexing, API mengembalikan HTTP 409; request tidak valid ditolak dengan HTTP 422.

### Pengujian endpoint yang dilakukan

- `GET /health` mengembalikan status `OK` dan model `ready`.
- `POST /index` berhasil mengindeks 26 dokumen dan membuat collection `programming_concepts`.
- Lima query berbeda dijalankan melalui `POST /search` dengan `top_k: 3`.
- Query Top-K yang sama dijalankan dengan `top_k` 1, 3, dan 5.
- Satu query di luar topik dataset dijalankan untuk mengamati bad retrieval.
- Validasi `top_k` di luar rentang diuji dan API mengembalikan HTTP 422.
- Request indexing dataset kustom dan pengindeksan ulang dataset bawaan juga diuji.

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

Kelima query berikut menguji makna dengan susunan kata yang berbeda dari dokumen. Setiap baris berisi hasil aktual teratas dari endpoint `/search` dengan `top_k: 3`; skornya adalah cosine similarity dari Qdrant.

### Query 1

- **Query:** Bahasa yang cocok untuk mengolah data dan membuat sistem pintar
- **Top result:** Python adalah bahasa pemrograman yang mudah dibaca dan banyak digunakan untuk otomasi, analisis data, dan kecerdasan buatan.
- **Kategori:** `bahasa-pemrograman`
- **Similarity score:** `0.5828`
- **Penilaian:** Relevan karena dokumen secara eksplisit membahas analisis data dan kecerdasan buatan, sesuai dengan makna query.

### Query 2

- **Query:** Cara membuat situs bisa merespons klik pengguna
- **Top result:** JavaScript memungkinkan halaman web menjadi interaktif dan dapat berjalan di browser maupun server menggunakan Node.js.
- **Kategori:** `bahasa-pemrograman`
- **Similarity score:** `0.5649`
- **Penilaian:** Relevan. Interaktivitas halaman web adalah konsep yang sesuai dengan situs yang merespons tindakan pengguna.

### Query 3

- **Query:** Alat untuk menyimpan informasi dan mencarinya kembali secara terstruktur
- **Top result:** Redis menyimpan data dalam memori dan sering digunakan sebagai cache atau penyimpanan sementara yang cepat.
- **Kategori:** `database`
- **Similarity score:** `0.5090`
- **Penilaian:** Sebagian relevan karena Redis menyimpan data, tetapi hasilnya tidak sepenuhnya menggambarkan pencarian terstruktur. Query terlalu luas sehingga database relasional tidak otomatis berada di posisi pertama.

### Query 4

- **Query:** Program di sisi server untuk menerima permintaan dari aplikasi
- **Top result:** REST API menyediakan sumber daya melalui HTTP dengan metode seperti GET, POST, PUT, dan DELETE.
- **Kategori:** `backend`
- **Similarity score:** `0.4805`
- **Penilaian:** Cukup relevan karena REST API menjelaskan komunikasi permintaan antara aplikasi dan backend. Namun, hasil ini menjelaskan antarmuka API, bukan framework server tertentu.

### Query 5

- **Query:** Bagaimana mempercepat aplikasi dengan menyimpan jawaban yang sering dipakai
- **Top result:** Caching menyimpan hasil yang sering diminta agar aplikasi dapat merespons lebih cepat dan mengurangi beban database.
- **Kategori:** `backend`
- **Similarity score:** `0.7182`
- **Penilaian:** Sangat relevan karena hasil menjelaskan penyimpanan hasil yang sering diminta untuk mempercepat respons.

## Experiment 2 - Top-K

- **Query:** Framework Python untuk membuat layanan web
- **Top-K = 1 (hasil aktual):**
  1. `Flask adalah framework web Python yang ringan dan memberi kebebasan untuk memilih komponen aplikasi.` — kategori `backend`, skor `0.5825`.
- **Top-K = 3 (hasil aktual):**
  1. `Flask adalah framework web Python yang ringan dan memberi kebebasan untuk memilih komponen aplikasi.` — kategori `backend`, skor `0.5825`.
  2. `Python adalah bahasa pemrograman yang mudah dibaca dan banyak digunakan untuk otomasi, analisis data, dan kecerdasan buatan.` — kategori `bahasa-pemrograman`, skor `0.5408`.
  3. `Django menyediakan banyak fitur bawaan seperti autentikasi, ORM, dan panel admin untuk aplikasi web Python.` — kategori `backend`, skor `0.5137`.
- **Top-K = 5 (hasil aktual):**
  1. `Flask adalah framework web Python yang ringan dan memberi kebebasan untuk memilih komponen aplikasi.` — kategori `backend`, skor `0.5825`.
  2. `Python adalah bahasa pemrograman yang mudah dibaca dan banyak digunakan untuk otomasi, analisis data, dan kecerdasan buatan.` — kategori `bahasa-pemrograman`, skor `0.5408`.
  3. `Django menyediakan banyak fitur bawaan seperti autentikasi, ORM, dan panel admin untuk aplikasi web Python.` — kategori `backend`, skor `0.5137`.
  4. `FastAPI adalah framework Python untuk membangun backend API yang cepat dengan validasi data otomatis.` — kategori `backend`, skor `0.4854`.
  5. `HTML memberikan struktur dan makna pada konten halaman web melalui elemen seperti judul, tautan, dan formulir.` — kategori `frontend`, skor `0.4309`.

Ketika Top-K diperbesar dari 1 menjadi 3 lalu 5, jumlah kandidat yang dikembalikan bertambah dan urutan hasil tetap dari skor tertinggi ke terendah. Hasil tambahan memiliki skor yang lebih rendah; Python adalah bahasa, bukan framework, dan HTML adalah bahasa markup, bukan framework Python. **Apakah menambah Top-K selalu membuat hasil lebih baik? Tidak.** Dari percobaan ini, Top-K yang lebih tinggi menambah pilihan tetapi juga memasukkan hasil yang kurang spesifik. Top-K perlu dipilih sesuai kebutuhan pencarian.

## Experiment 3 - Bad Retrieval

- **Query:** Siapa yang memenangkan pertandingan sepak bola tadi malam?
- **Actual results dan similarity score:**
  1. `Node.js menjalankan JavaScript di sisi server dan cocok untuk membuat layanan jaringan yang menangani banyak koneksi.` — kategori `backend`, skor `0.0561`.
  2. `PostgreSQL adalah database relasional yang mendukung query kompleks, transaksi, dan berbagai tipe data.` — kategori `database`, skor `0.0434`.
  3. `Qdrant adalah vector database yang menyimpan embedding dan mencari data berdasarkan kemiripan vektor.` — kategori `database`, skor `0.0280`.
- **Kenapa retrieval kurang bagus?** Tidak ada hasil yang menjawab pertanyaan tentang pertandingan sepak bola; hasil teratas membahas Node.js, database, dan vector database, bukan olahraga.
- **Kemungkinan penyebab:** Dataset hanya berisi konsep pemrograman dan tidak mencakup informasi sepak bola. Vector search tetap mengurutkan kandidat yang tersedia meskipun query berada di luar cakupan dataset. Skor yang rendah (`0.0561` sampai `0.0280`) mendukung bahwa kandidat tersebut tidak mirip dengan query. Untuk aplikasi yang lebih besar, cakupan dataset dan ambang skor relevansi dapat dipertimbangkan.

## Personal Reflection

1. **Sebelum mengerjakan tugas ini, bagaimana membayangkan search engine bekerja? Apakah ada perbedaan setelah mempelajari semantic search?**
   Sebelum mengerjakan project ini, saya membayangkan search engine terutama mencari kata yang sama dengan kata dalam dokumen. Setelah mempelajari semantic search, saya memahami bahwa query dapat diubah menjadi embedding dan dibandingkan berdasarkan kedekatan makna. Karena itu, query dengan susunan kata berbeda masih dapat menemukan dokumen yang sesuai, seperti query tentang “mengolah data dan membuat sistem pintar” yang menemukan deskripsi Python tentang analisis data dan kecerdasan buatan.
2. **Apa perbedaan terbesar antara keyword search dan semantic search?**
   Keyword search mengutamakan kecocokan kata atau istilah, sedangkan semantic search membandingkan representasi makna dari query dan dokumen. Semantic search lebih toleran terhadap parafrasa, tetapi bukan berarti selalu benar: hasil tetap bergantung pada model, dataset, dan cara query dirumuskan.
3. **Apa fungsi embedding di dalam semantic search?**
   Embedding mengubah teks menjadi vector angka yang mewakili pola makna teks. Vector query dibandingkan dengan vector dokumen; vector yang lebih dekat menurut metrik yang digunakan menjadi kandidat hasil yang lebih mirip.
4. **Kenapa embedding tidak cukup hanya disimpan di list Python jika jumlah data menjadi sangat banyak?**
   List Python cocok untuk demonstrasi dengan data sedikit. Saat data bertambah, aplikasi memerlukan penyimpanan persisten, pencarian tetangga terdekat yang efisien, dan cara mengelola payload serta collection. Vector database seperti Qdrant menyediakan kemampuan tersebut sehingga aplikasi tidak perlu membandingkan query secara manual terhadap semua vector dalam list.
5. **Bagian project mana yang paling sulit dipahami?**
   Bagian yang paling menantang adalah memahami hubungan ukuran embedding dengan konfigurasi vector Qdrant, serta memastikan vector, teks, dan kategori disimpan pada point yang sama. Saya juga perlu menafsirkan hasil yang kurang tepat, misalnya hasil Redis untuk query penyimpanan informasi yang sebenarnya terlalu luas.
6. **Bagian kode mana yang paling banyak dibantu oleh AI?**
   Bantuan paling banyak digunakan untuk menyusun struktur endpoint FastAPI dan menghubungkan proses encoding SentenceTransformer dengan indexing dan pencarian Qdrant. AI juga membantu merapikan dokumentasi dan menyiapkan format pengujian. Hasil endpoint dijalankan untuk memeriksa bahwa implementasinya bekerja.
7. **Jelaskan dengan bahasa sendiri bagaimana bagian kode tersebut bekerja.**
   Saat `/index` dipanggil tanpa body, aplikasi mengambil dokumen dari `data.py`, mengubah teks menjadi embedding, membuat collection dengan ukuran vector model dan metrik cosine, lalu menyimpan vector beserta `text` dan `category` ke payload Qdrant. Saat `/search` dipanggil, aplikasi mengubah query menjadi embedding yang sama jenisnya, meminta Qdrant mengambil sebanyak `top_k` vector terdekat, lalu mengembalikan teks, kategori, dan score tiap hasil.
8. **Aplikasi ini bisa dikembangkan menjadi aplikasi apa jika project dilanjutkan?**
   Aplikasi dapat dikembangkan menjadi pencarian dokumentasi pemrograman berbahasa Indonesia. Pengembang dapat menambah dokumen tutorial dan FAQ, memperbarui dataset tanpa mengganti seluruh collection, menyediakan filter kategori, lalu menguji relevansi dengan kumpulan query dan penilaian pengguna.

## AI Usage

- **AI tools:** GitHub Copilot.
- **AI digunakan untuk membantu bagian apa?** Menyusun struktur awal aplikasi FastAPI, validasi request Pydantic, integrasi SentenceTransformer dengan Qdrant, draf README, dan penyusunan skenario eksperimen.
- **Bagian apa yang diubah atau ditentukan sendiri setelah mendapat hasil AI?** Tema dan isi dataset konsep pemrograman ditentukan dalam proses pengerjaan dengan bantuan AI; endpoint diuji langsung; query eksperimen, Top-K, dan bad retrieval diperiksa dari respons API; isi README disesuaikan dengan skor dan hasil aktual. AI tidak digunakan untuk menghasilkan jawaban pencarian saat aplikasi berjalan.

## Batasan

Hasil pencarian dibatasi pada isi dataset kecil yang tersedia dan tidak menjawab pertanyaan faktual di luar cakupannya. Score cosine similarity membantu mengurutkan kandidat, tetapi bukan jaminan bahwa hasil benar atau relevan untuk setiap query.
