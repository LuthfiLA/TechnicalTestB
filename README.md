# Catatan Refaktor Kode

## 1. Perubahan Arsitektur
Saya mengubah struktur kode dari prosedural  menjadi **Object-Oriented Programming (OOP)** dengan pola **Dependency Injection**:
* **Pemisahan Lapisan:** Logika dibagi menjadi `core` (konfigurasi), `repository` (penyimpanan data), dan `services` (logika bisnis)
* **Penghapusan Global State:** Menghilangkan variabel global seperti `docs_memory` dan `USING_QDRANT`. Semua data kini terenkapsulasi di dalam kelas masing-masing
* **Service Container:** Menggunakan kelas `ServiceContainer` di `main.py` untuk mengelola siklus layanan secara terpusat

## 2. Peningkatan Teknis
* **Konfigurasi .env:** Menggunakan `pydantic-settings` untuk manajemen variabel lingkungan yang lebih aman
* **Maintainability:** Refaktor ini meningkatkan maintainability karena saya menerapkan Dependency Injection dan Service Container untuk mengelola layanan secara terpusat, sehingga kode tidak lagi saling mengunci. Saya juga menghilangkan variabel global melalui enkapsulasi ke dalam kelas-kelas yang punya tanggung jawab spesifik (Repository, Service, Controller), yang menjamin data lebih aman dan tidak bocor. Dengan struktur modular ini, setiap bagian aplikasi jadi lebih mudah diuji secara mandiri dan siap dikembangkan lebih lanjut tanpa risiko merusak logika utama. Memudahkan pengembang lain untuk melakukan *unit testing* pada setiap modul secara independen tanpa harus menjalankan server FastAPI

**Status:** Siap diuji. Seluruh fungsi endpoint (`/ask`, `/add`, `/status`) tetap bekerja sesuai spesifikasi awal

# Setup Guide

* **Setup Environment**
python -m venv venv setelah itu Aktivasi 
venv\Scripts\activate

* **Install dependencies**
pip install -r requirements.txt

* **Copy .env.example ke .env**
cp .env.example .env

* **Jalankan Aplikasi**
uvicorn app.main:app --reload
