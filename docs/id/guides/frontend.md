# Bagian depan

Nexy tidak mengirimkan sistem komponennya sendiri untuk klien. Itu dibangun di atas Vite: React, Vue, Svelte, Solid dan Preact semuanya didukung, dan halaman vanilla berfungsi tanpa kerangka klien sama sekali.

## Aktifkan kerangka kerja

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()   # vue(), svelte(), solid(), preact()
```

`useVite` defaultnya adalah `True`; tetap aktifkan saat kerangka kerja dikonfigurasi.

## File rute

| Ekstensi | Dirender |
|---|---|
| `.nexy`, `.md` | oleh Nexy pada waktu permintaan |
| `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte` | oleh kerangka klien; dipra-render ke HTML pada waktu pembuatan, kemudian diambil alih oleh bundel klien |

Rute kerangka kerja adalah halaman normal, bukan pulau khusus klien: HTML sudah ada sebelum bundel berjalan, jadi pengecatan pertama tidak menunggu JavaScript.

Penyiapan per kerangka: [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md).

## Pembangunan

`nx dev` memulai satu server pada satu port:

1. aplikasi mengkompilasi ulang rute yang Anda ubah, server dan klien;
2. Vite berjalan pada port internal dan melayani modul kerangka kerja;
3. Nexy memproksi titik akhir Vite melalui asalnya sendiri.

Browser hanya berbicara ke port `3000`. Tidak ada URL kedua untuk dibuka dan tidak ada CORS untuk dikonfigurasi.

## Membangun

`nx build` menghasilkan:

- HTML yang telah dirender sebelumnya untuk rute kerangka kerja;
- paket klien, dengan aset di bawah `__nexy__/client/`;
- rute Python yang dikompilasi.

Vite menangani bundel klien; SSR HTML diproduksi per file oleh esbuild.

> [!CATATAN]
> rute yang rendering servernya gagal dilaporkan sebagai rute khusus klien dan bukannya menggagalkan keseluruhan build.

## Penataan gaya

`nexy new` meminta mode gaya dan mengaturnya untuk kerangka klien yang Anda pilih: Tailwind, UnoCSS atau CSS biasa. Token desain (warna, font, tema gelap) adalah variabel CSS di `src/globale.css`, file yang dibuat oleh scaffold.

| Mode | Halaman awal ditulis dengan |
|---|---|
| Tailwind, UnoCSS | kelas utilitas dalam markup, dengan token dipetakan ke nama kelas |
| Nama kelas semantik CSS biasa | dan CSS di `src/globale.css` |

Ikuti mode proyek Anda saat Anda menambahkan halaman: kelas utilitas dalam proyek utilitas, CSS dalam CSS biasa. Simpan komponen CSS yang tidak dapat diungkapkan oleh utilitas di blok `<style>` komponen. Dalam proyek server (`.nexy` halaman) UnoCSS membaca file `.nexy` untuk kelas; Tailwind menemukannya dengan sendirinya.

## Font, gambar, skrip

Letakkan file statis di `public/` - file tersebut disajikan dari `/` dalam pengembangan dan produksi.

## Langkah selanjutnya

- [Tampilan](../views/README.md): pilih format halaman
- [Config](../reference/config.md): `useFF`, `useVite`, alias
- [Deploy](../deployment/README.md): apa yang dihasilkan oleh build
