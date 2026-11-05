# Nexy dan NestJS

Router modular terinspirasi oleh NestJS: pengontrol, modul, dan injeksi konstruktor. Ini adalah lapisan tipis di atas FastAPI, sehingga tidak mencoba mereproduksi seluruh NestJS. Halaman ini mencantumkan kedua sisi.

## Apa yang cocok

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` dengan empat atribut kelas yang sama |
| `@Injectable()` | `@Injectable()` |
| Parameter injeksi konstruktor | `__init__` diselesaikan dari anotasi tipe |
| Cakupan tunggal, permintaan, dan sementara | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (ketergantungan FastAPI) |
| `@ApiOperation`, `@ApiResponse` (Swagger) | `@UseRoute`, `@UseResponse` (OpenAPI, bertugas di `/docs`) |
| WebSocket gateway | `async def SOCKET(...)` pada pengontrol |
| Validasi DTO (`class-validator`) | Pydantic model, asli dari FastAPI |
| Deteksi ketergantungan melingkar | `RecursionError` memberi nama kelas |

## Apa yang berbeda

- Penangan adalah metode yang diberi nama berdasarkan kata kerja HTTP (`get`, `post`...), satu per pengontrol.
- Penjaga dan dekorator middleware adalah FastAPI `Depends`, bukan kelas dengan `canActivate`.
- Parameter (`@Body`, `@Param`, `@Query`) adalah parameter FastAPI: anotasi tipe, `Query`, `Path`, `Body`.
- Pipa adalah Pydantic validasi dan FastAPI dependensi.

## Apa yang hilang

| NestJS fitur | Status di Nexy |
|---|---|
| Penyedia khusus (`useValue`, `useFactory`, `useClass`, token string) | tidak tersedia: hanya kelas `@Injectable()` |
| Menyuntikkan berdasarkan antarmuka atau kelas abstrak | tidak tersedia |
| Enkapsulasi modul | tidak diterapkan: container mencakup seluruh proses, `exports` hanya mengontrol resolusi yang diinginkan |
| Modul dinamis dan global (`forRoot`, `@Global`) | tidak tersedia |
| Kait siklus hidup (`onModuleInit`, `onApplicationShutdown`) | tidak tersedia |
| Pencegat | menggunakan middleware ASGI (`useMiddlewares`) atau dependensi |
| Filter pengecualian | menggunakan FastAPI penangan pengecualian |
| Modul pengujian dengan penyedia mengesampingkan | tanpa API publik; gunakan FastAPI `dependency_overrides` dan `TestClient` |
| Modul konfigurasi, penjadwalan, antrian, CQRS, layanan mikro, caching | bukan bagian dari Nexy; memanfaatkan ekosistem Python |

## Kapan harus mengambilnya

Pilih router modular bila Anda menginginkan struktur berbasis kelas dengan injeksi untuk API yang lebih besar. Pilih router berbasis file ketika struktur URL adalah prinsip pengorganisasiannya. Keduanya di-scaffold oleh `nx new`, dijalankan pada aplikasi FastAPI yang sama, dan dapat hidup berdampingan.

> [!CATATAN]
> item yang hilang di atas adalah kesenjangan yang jujur. Jika Anda memerlukan penyedia `useFactory` atau penyedia yang dapat diganti dalam pengujian hari ini, pertahankan logika dalam fungsi biasa dan FastAPI `Depends`, yang menyusun dan mengganti secara alami.

## Langkah selanjutnya

- [Injeksi ketergantungan](dependency-injection.md)
- [Penjaga dan metadata](guards-and-metadata.md)
- [Pengujian](../../guides/testing.md)
