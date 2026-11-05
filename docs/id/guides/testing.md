# Pengujian

`nx test` menjalankan pengujian server dengan pytest, dan klien menguji dengan vitest saat Anda memintanya.

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## Apa yang berjalan

| Bagian | Perintah | Kondisi |
|---|---|---|
| Server | `pytest` | berjalan pada `tests/` jika ada, sebaliknya pada root proyek; dilewati dengan peringatan ketika pytest tidak diinstal |
| Klien | `npx vitest run` | hanya dengan `--client`, dan hanya jika `vitest.config.ts` ada atau `vitest` muncul di `package.json` |

Tidak ada pelari end-to-end bawaan. Jalankan server dengan `TestClient` dan tambahkan Playwright atau Cypress sendiri untuk perilaku browser.

## Uji servernya

Klien pengujian berbicara dengan aplikasi ASGI yang sedang dalam proses: tidak ada server untuk memulai, tidak ada port untuk dipilih.

```python filename="tes/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` adalah aplikasi yang dirakit, dibuat saat pertama kali dibaca. Bunyinya `nexyconfig.py` dari direktori kerja, jadi jalankan pytest dari root proyek.

Saat pengujian mengubah konfigurasi atau rute, buatlah aplikasi baru alih-alih menggunakan kembali aplikasi tingkat modul:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` merakit kembali rute, middleware, sesi dan terjemahan, sehingga setiap panggilan dimulai dari keadaan direktori proyek saat ini.

## Apa yang harus ditegaskan

Sebuah halaman mengembalikan HTML. Tegaskan statusnya, lalu konten yang Anda pedulikan:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

Pengendali API mengembalikan JSON. Kegagalan validasi adalah `422`, dan rute yang hilang adalah `404` yang dijawab oleh `notfound.nexy` ketika file tersebut ada:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

Untuk suatu tindakan, uji fungsi secara langsung - ini adalah fungsi normal - dan uji titik akhir HTTP dengan membaca jalur yang dihasilkan dari halaman yang memaparkannya:

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    response = client.post(action, data={"name": "Ada"}, follow_redirects=False)
    assert response.status_code == 303
```

Panggilan dengan JSON menjawab dengan hasilnya, dan `422` dengan bidang yang tidak valid.

> [!NOTE]
> jalur tindakan khusus untuk proyek dan dihasilkan. Jangan pernah melakukan hardcode `/_nx_<hash>` dalam pengujian.

## Uji komponen `.nexy`

`nexy.testing.render` mengkompilasi sebuah komponen, dengan komponen yang diimpornya, dan mengembalikan HTML-nya. Props adalah argumen kata kunci dan `children=` mengisi slotnya:

```python filename="tes/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

Jalankan pytest dari root proyek: file yang dikompilasi menuju ke `__nexy__/`, seperti halnya `nx dev`. Komponen yang membaca permintaan (`usePathname`, `useSession`) memerlukan pengujian halaman dengan `TestClient` sebagai gantinya.

## Uji klien

`nx test --client` mengharapkan pengaturan vitest Anda sendiri. Tes komponen minimal:

```tsx filename="src/components/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` dan perpustakaan pengujian merupakan dependensi proyek: `nexy new` tidak memasang tumpukan pengujian. Tambahkan `vitest.config.ts` dengan lingkungan yang Anda butuhkan (jsdom atau happy-dom untuk komponen).

## Integrasi berkelanjutan

Dua perintah sudah cukup untuk alur proyek:

```bash
nx build
nx test
```

`nx build` gagal karena kesalahan kompilasi; `nx test` gagal pada pernyataan yang gagal dan keluar bukan nol. `nx check` menambahkan mypy dan `tsc` ke proses.

Pengerjaan Nexy sendiri menggunakan perintah yang berbeda: lihat [KONTRIBUSI](../../CONTRIBUTING.md).

## Langkah selanjutnya

- [CLI](../reference/cli.md): setiap bendera `nx test`
- [API](../routing/fbr/handlers/README.md): apa yang dikembalikan oleh titik akhir
- [Penerapan](../deployment/README.md): buat sebelum Anda menguji di CI
