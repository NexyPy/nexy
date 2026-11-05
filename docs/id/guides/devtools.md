# Bilah alat pengembang

`nexy dev` menambahkan toolbar ke setiap halaman HTML. Itu terletak di sudut kiri bawah, menunjukkan rute yang Anda lalui dan berapa lama waktu yang dibutuhkan server, dan terbuka di panel. Ini tidak pernah menjadi bagian dari respons produksi.

| Tab | Menampilkan |
|---|---|
| Halaman | URL, rute, pengendali, file asalnya (dengan tautan yang membukanya di editor Anda), status, waktu server, byte pertama, cat pertama, konten utama, perubahan tata letak (bernilai hijau, kuning atau merah), DOM siap |
| Merutekan | setiap rute aplikasi dengan metodenya, filter, dan rute saat ini yang ditandai; masing-masing tertaut ke filenya |
| Kesalahan | kesalahan server sejak `nexy dev` dimulai dan kesalahan yang dimunculkan browser |
| Pengaturan | tema (cocok dengan halaman, gelap atau terang), posisi, ukuran, sembunyikan, reset |

## Pindahkan itu

Seret tombol: tombol ini mengikuti penunjuk dan langsung menuju ke sudut terdekat saat Anda melepaskannya. Panel terbuka ke arah tengah layar dari mana pun tombolnya berada. Posisinya disimpan di browser ini. Anda juga dapat memilih sudut di **Pengaturan**.

`Shift` + `Alt` + `D` menyembunyikan dan menampilkan toolbar. `Esc` menutup panel.

## Kesalahan

Kesalahan yang tidak tertangkap di browser membuka dialog pada halaman dengan pesan dan tumpukan; dengan beberapa kesalahan, lewati kesalahan tersebut (1 dari 3). Kesalahan server menjawab dengan halaman yang sejenis: kesalahan, tempat munculnya, dan kode di sekitarnya.

## Matikan

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useDevTools = False
```

Bilah alat adalah blok gaya dan skrip yang ditambahkan sebelum `</body>`: tidak ada permintaan eksternal, tidak ada ketergantungan. JSON, file dan setiap respon yang bukan HTML dibiarkan begitu saja.

## Langkah selanjutnya

- [Konfigurasi](../reference/config.md): setiap opsi
- [Pengujian](testing.md): menguji halaman atau komponen
