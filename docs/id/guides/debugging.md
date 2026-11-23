# Bagaimana cara men-debug kode server di Nexy?

Debug kode server `nx dev` dengan `breakpoint()` di terminal, atau dengan VS Code dan `debugpy`: server dev menjalankan Python Anda dalam prosesnya sendiri, sehingga debugger yang terpasang padanya berhenti di halaman, penangan API, dan tindakan Anda.

## Bagaimana `nx dev` menjalankan kode Anda

`nx dev` memulai uvicorn dalam prosesnya sendiri, tanpa pekerja terpisah. Ketika file Python atau halaman `.nexy` berubah, modul proyek Anda akan dilupakan dan diimpor lagi dalam proses yang sama. Oleh karena itu, debugger yang dilampirkan ke `nx dev` tetap terpasang selama pemuatan ulang, dan set breakpoint dalam file tetap ditempatkan di kode baru.

File `.nexy` dikompilasi ke modul Python di bawah `__nexy__/`, di jalur yang sama, yang dijalankan:

<!-- router:fbr,custom -->
| Anda menulis | Nexy berlari |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, fungsi `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | file itu sendiri |
<!-- /router -->

<!-- router:modular -->
| Anda menulis | Nexy berlari |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | file itu sendiri |
<!-- /router -->

Materi depan file `.nexy` (Python di antara dua baris `---`) menjadi isi fungsi modul tersebut. `__nexy__/` ditulis lagi pada setiap perubahan: jangan pernah mengeditnya.

## Berhenti di terminal dengan `breakpoint()`

Letakkan `breakpoint()` di mana Anda ingin berhenti, di file `.py` atau di bagian depan file `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/rute/tentang.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

Buka halamannya. Permintaan menunggu dan terminal `nx dev` menampilkan pdb, dalam modul yang dikompilasi:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

Buka `/users`. Permintaan menunggu dan terminal `nx dev` menampilkan pdb pada baris itu. Di bagian depan tampilan, pdb menampilkan modul yang dikompilasi di bawah `__nexy__/src/apps/`.
<!-- /router -->

Ketik `p page` untuk mencetak nilai, `n` untuk baris berikutnya, `c` untuk membiarkan permintaan dilanjutkan. Hapus baris setelah Anda selesai: permintaan berikutnya berhenti di situ lagi.

## Debug dengan Kode VS

Instal `debugpy` di lingkungan proyek:

```bash
uv add --dev debugpy
```

Kemudian tambahkan konfigurasi peluncuran. `nexy.modules.cli` adalah modul di belakang perintah `nx`, jadi ini berfungsi sama di Linux, macOS, dan Windows:

```json filename=".vscode/peluncuran.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

Tekan F5. Tetapkan breakpoint di file `.py` Anda, dan di modul yang dikompilasi di bawah `__nexy__/` untuk file `.nexy`: VS Code tidak dapat berhenti di file `.nexy`, karena file tersebut bukan Python sampai dikompilasi. Nomor baris modul yang dikompilasi mengikuti frontmatter, jadi breakpoint di sana mungkin berpindah setelah Anda mengedit halaman; `breakpoint()` di bagian depan tidak.

## Lampirkan dari terminal lain

Untuk memulai server dev sendiri dan memasang debugger nanti:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` menahan permulaan hingga debugger terpasang; biarkan saja untuk memulai sekaligus. Pada VS Code, lampirkan dengan konfigurasi `"request": "attach"` dan `"connect": { "host": "127.0.0.1", "port": 5678 }`.

debugpy mungkin memperingatkan bahwa "modul beku sedang digunakan". Mulai Python dengan `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) jika breakpoint di perpustakaan standar terlewatkan; breakpoint dalam kode Anda sendiri tidak terpengaruh.

## Langkah selanjutnya

- [Pemecahan masalah](troubleshooting.md): masalah pertama yang dialami orang
- [Pengujian](testing.md): mereproduksi bug dalam pengujian setelah Anda menemukannya
- [File .nexy](../views/nexy/README.md): frontmatter, props dan templat
