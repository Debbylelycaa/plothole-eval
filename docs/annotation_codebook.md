# Codebook Anotasi Ground Truth

Dokumen ini adalah aturan keputusan untuk menilai setiap entri GT dari movieplotholes.
Tujuannya agar keputusan konsisten dan bisa diperiksa ulang.

## Prinsip
Entri GT dipakai untuk evaluasi hanya jika plot hole-nya **dapat diverifikasi dari
teks naskah saja**. Model hanya membaca naskah, jadi menilai model terhadap hal
yang tidak ada di naskah tidak adil.

## Prosedur keputusan (urut, berhenti di langkah pertama yang cocok)

| Langkah | Pertanyaan | Jika ya |
|---|---|---|
| 1 | Masalahnya tentang dunia nyata (sains, hukum, sejarah, geografi), bukan tentang isi cerita? | `no`, **E1** |
| 2 | Masalahnya tentang produksi: casting, umur aktor, akting, efek visual, properti? | `no`, **E2** |
| 3 | Adegan atau elemen yang dibahas tidak ada di versi naskah ini? | `no`, **E3** |
| 4 | Cerita sendiri menjelaskannya, atau memang disengaja (twist, narator tak andal)? | `no`, **E6** |
| 5 | Hanya opini, "kenapa tokoh tidak melakukan X yang lebih baik", atau nitpick, tanpa dua hal di cerita yang saling bertentangan? | `no`, **E4** |
| 6 | Sama dengan entri lain di film yang sama? | `no`, **E5** |
| 7 | Lolos semua langkah di atas | `yes`, pilih tipe **T1–T4**, isi posisi |

## Kode eksklusi
- **E1** Realisme / pengetahuan di luar cerita
- **E2** Produksi, casting, akting, efek visual
- **E3** Tidak ada di versi naskah ini
- **E4** Opini / saran alternatif / nitpick, bukan inkonsistensi
- **E5** Duplikat
- **E6** Dijelaskan atau disengaja di dalam cerita

## Tipe plot hole (hanya untuk `yes`)
- **T1 Kontradiksi fakta**: fakta A dinyatakan di satu tempat, bukan-A di tempat lain.
- **T2 Pelanggaran aturan dunia**: aturan yang ditetapkan cerita (sihir, teknologi,
  hukum dunia fiksi) dilanggar.
- **T3 Inkonsistensi waktu/urutan/lokasi**: kronologi, durasi, atau posisi tidak mungkin.
- **T4 Inkonsistensi motivasi/pengetahuan tokoh**: tokoh bertindak bertentangan dengan
  tujuan atau pengetahuan yang **sudah ditetapkan cerita**.
  Bedanya dengan E4: T4 butuh dua hal di naskah yang bertentangan; E4 hanya
  "seharusnya ada cara yang lebih baik".

## Posisi (hanya untuk `yes`, nomor unit dari units.json)
- **setup_unit**: unit tempat fakta/aturan pertama kali ditetapkan.
- **violation_unit**: unit tempat fakta/aturan itu dilanggar.
- Jika hanya ada satu lokasi (mis. T4 dalam satu adegan), isi `violation_unit` saja.
- Analisis posisi (Lost in the Middle) memakai `violation_unit`.

## Contoh
- Training Day gt02, "aktris yang memerankan keponakan terlalu tua untuk siswi SMA"
  → `no`, **E2** (casting; tidak ada di naskah).
- Training Day gt01, "rencana menembak Roger tidak masuk akal, mereka bisa saja
  langsung membunuh dan mengambil uangnya" → `no`, **E4** (saran alternatif,
  tidak ada dua fakta cerita yang bertentangan).

## Uji konsistensi
Anotasi dilakukan dua putaran oleh anotator yang sama, dengan jeda minimal 7 hari,
tanpa melihat hasil putaran pertama. Kesepakatan dihitung dengan Cohen's kappa
untuk (a) keputusan include dan (b) label lengkap (tipe atau kode eksklusi).
Ketidaksepakatan diselesaikan dengan merujuk codebook ini; hasil putaran 1
yang sudah direvisi menjadi label final.