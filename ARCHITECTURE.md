## 🧠 PROJECT MAP – AI Productivity Manager

### 1. Tujuan Akhir

Membangun **AI asisten personal** yang:

* Memantau aktivitas digital (PC dulu)
* Membedakan **aktif, AFK, produktif, distraksi**
* Memberi **ringkasan, peringatan, dan arahan kontekstual**
* Membantu pengambilan keputusan, bukan cuma nyimpen data

Tujuan utama:
**membuat perilaku pengguna terlihat dan tidak bisa dibohongi.**

---

### 2. Komponen Sistem

#### A. Tracker (Sensor)

Tugas:

* Mendeteksi aplikasi aktif
* Menghitung durasi
* Mendeteksi AFK (idle input)
* Menyimpan data mentah ke JSON

Sifat:

* Pasif
* Tidak menganalisis
* Tidak “pintar”

Output:

```
logs.json
- app
- category
- start
- end
- active_sec
- afk_sec
```

---

#### B. Scheduler (Context Provider)

Tugas:

* Membaca jadwal offline (JSON)
* Memberi peringatan sebelum kegiatan
* Tidak menyimpan histori panjang

Catatan:

* Reload setiap loop (biar perubahan file langsung kebaca)
* Alert hanya 1x per event per hari

---

#### C. Analyzer (Otak Statistik)

Tugas:

* Mengolah logs harian
* Menghitung:

  * total produktif
  * total distraksi
  * total AFK
  * pola jam rawan distraksi
* Tidak pakai ML

Output:

```
daily_summary.json
```

---

#### D. AI Manager (Decision Layer)

Ini yang kamu maksud **AI**, bukan tracker.

Tugas:

* Membaca hasil analisis
* Membaca target & rules
* Mengambil keputusan sederhana

Contoh:

* “Distraksi lewat batas → kirim alert”
* “AFK setelah sesi panjang → sarankan istirahat”
* “Besok jangan taruh task berat jam 16–17”

Catatan penting:
AI **tidak mengumpulkan data**
AI **tidak berjalan real-time berat**
AI = pengambil keputusan, bukan pengintai

---

### 3. Alur Data (Flow)

```
User Activity
   ↓
Tracker
   ↓
logs.json
   ↓
Analyzer
   ↓
daily_summary.json
   ↓
AI Manager
   ↓
Alert / Insight / Arahan
```

---

### 4. Batasan (Sengaja)

* Tidak tracking HP (privacy + ribet)
* AFK = idle input, bukan asumsi mental
* Musik di HP dianggap netral
* AI tidak menebak niat, hanya membaca pola

---

### 5. Roadmap

Tahap 1 (sekarang):

* Tracker stabil
* AFK valid
* Data konsisten

Tahap 2:

* Analyzer rapi
* Summary harian otomatis

Tahap 3:

* AI Manager aktif
* Insight berbasis kebiasaan

Tahap 4 (opsional):

* Visualisasi
* ML ringan (kalau data udah dewasa)

---