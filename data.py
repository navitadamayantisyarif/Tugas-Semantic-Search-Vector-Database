"""Dataset konsep pemrograman untuk semantic search."""

documents = [
    {
        "text": "Python adalah bahasa pemrograman yang mudah dibaca dan banyak digunakan untuk otomasi, analisis data, dan kecerdasan buatan.",
        "category": "bahasa-pemrograman",
    },
    {
        "text": "JavaScript memungkinkan halaman web menjadi interaktif dan dapat berjalan di browser maupun server menggunakan Node.js.",
        "category": "bahasa-pemrograman",
    },
    {
        "text": "Java sering dipakai untuk membangun aplikasi perusahaan dan aplikasi Android dengan dukungan ekosistem yang luas.",
        "category": "bahasa-pemrograman",
    },
    {
        "text": "TypeScript menambahkan sistem tipe statis pada JavaScript sehingga kesalahan dapat ditemukan lebih awal.",
        "category": "bahasa-pemrograman",
    },
    {
        "text": "Rust berfokus pada performa tinggi dan keamanan memori tanpa membutuhkan garbage collector.",
        "category": "bahasa-pemrograman",
    },
    {
        "text": "Go memiliki sintaks sederhana dan fitur konkurensi yang membantu membangun layanan jaringan yang cepat.",
        "category": "bahasa-pemrograman",
    },
    {
        "text": "SQL digunakan untuk membaca, menambah, mengubah, dan menghapus data di dalam database relasional.",
        "category": "bahasa-pemrograman",
    },
    {
        "text": "C++ banyak digunakan untuk perangkat lunak yang membutuhkan kendali dekat terhadap perangkat keras dan performa tinggi.",
        "category": "bahasa-pemrograman",
    },
    {
        "text": "FastAPI adalah framework Python untuk membangun backend API yang cepat dengan validasi data otomatis.",
        "category": "backend",
    },
    {
        "text": "Django menyediakan banyak fitur bawaan seperti autentikasi, ORM, dan panel admin untuk aplikasi web Python.",
        "category": "backend",
    },
    {
        "text": "Flask adalah framework web Python yang ringan dan memberi kebebasan untuk memilih komponen aplikasi.",
        "category": "backend",
    },
    {
        "text": "Node.js menjalankan JavaScript di sisi server dan cocok untuk membuat layanan jaringan yang menangani banyak koneksi.",
        "category": "backend",
    },
    {
        "text": "REST API menyediakan sumber daya melalui HTTP dengan metode seperti GET, POST, PUT, dan DELETE.",
        "category": "backend",
    },
    {
        "text": "Autentikasi memeriksa identitas pengguna sebelum aplikasi memberikan akses ke akun.",
        "category": "backend",
    },
    {
        "text": "Caching menyimpan hasil yang sering diminta agar aplikasi dapat merespons lebih cepat dan mengurangi beban database.",
        "category": "backend",
    },
    {
        "text": "React membantu pengembang membuat antarmuka web dari komponen yang dapat digunakan kembali.",
        "category": "frontend",
    },
    {
        "text": "CSS mengatur tampilan halaman web seperti warna, jarak, ukuran teks, dan tata letak.",
        "category": "frontend",
    },
    {
        "text": "HTML memberikan struktur dan makna pada konten halaman web melalui elemen seperti judul, tautan, dan formulir.",
        "category": "frontend",
    },
    {
        "text": "Vue adalah framework JavaScript untuk membangun antarmuka pengguna secara bertahap dan berbasis komponen.",
        "category": "frontend",
    },
    {
        "text": "Desain responsif membuat tata letak situs menyesuaikan ukuran layar ponsel, tablet, dan komputer.",
        "category": "frontend",
    },
    {
        "text": "PostgreSQL adalah database relasional yang mendukung query kompleks, transaksi, dan berbagai tipe data.",
        "category": "database",
    },
    {
        "text": "Redis menyimpan data dalam memori dan sering digunakan sebagai cache atau penyimpanan sementara yang cepat.",
        "category": "database",
    },
    {
        "text": "MongoDB menyimpan data sebagai dokumen fleksibel, bukan dalam tabel relasional dengan skema tetap.",
        "category": "database",
    },
    {
        "text": "Qdrant adalah vector database yang menyimpan embedding dan mencari data berdasarkan kemiripan vektor.",
        "category": "database",
    },
    {
        "text": "Indeks database membantu menemukan baris yang cocok tanpa harus memeriksa seluruh isi tabel.",
        "category": "database",
    },
    {
        "text": "Transaksi database mengelompokkan beberapa operasi agar perubahan data tetap konsisten dan dapat dibatalkan bila gagal.",
        "category": "database",
    },
]
