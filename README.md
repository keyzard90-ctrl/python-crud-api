# python-crud-api

Praktikum CI/CD Pipeline dengan Jenkins, GitHub, Docker, dan ngrok.

- Nama: Keyzard Nashbun Manangkali
- NIM: 101012300367

## Endpoint

| Method | Path | Keterangan |
|---|---|---|
| GET | `/health` | Status layanan |
| GET | `/messages` | Daftar pesan |
| GET | `/messages/{id}` | Satu pesan berdasarkan indeks (Tugas D) |
| POST | `/messages` | Tambah pesan, body `{"message": "..."}` |
| DELETE | `/messages?index=N` | Hapus pesan berdasarkan indeks |

## Menjalankan test

```bash
python3 -m unittest -v test_app.py
```

## Pipeline Jenkins

Checkout Code → Code Syntax Verification → Unit Test → Build Docker Image
(tag build number, `sha-<commit>`, `latest`) → Automated Deployment → Health Check.

Data disimpan pada Docker named volume `production-api-data`
(`/var/lib/backend_data/messages.json`).

## Rollback manual (Tugas D)

```bash
docker stop production-api-container && docker rm production-api-container
docker run -d --name production-api-container --network jenkins-net \
  -p 5000:5000 -v production-api-data:/var/lib/backend_data \
  python-crud-api:<BUILD_NUMBER_SEBELUMNYA>
```

Webhook test Tue, Nov  3, 2026 10:22:53 PM
