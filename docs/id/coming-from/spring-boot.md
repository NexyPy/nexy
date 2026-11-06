# Dari Boot Musim Semi hingga Nexy

Di Nexy, metode Spring `@RestController` menjadi fungsi dalam file di bawah `src/routes/`, atau metode kelas `@Controller` di router modular: Validasi Bean menjadi Pydantic, dan halaman OpenAPI springdoc sudah ada di dalamnya.

Setiap bagian di bawah ini menunjukkan kebiasaan Spring Boot, lalu hal yang sama di Nexy.

## Sebuah pengontrol

```java filename="HaloController.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

Jalur file adalah URL, nama fungsinya adalah metode HTTP:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` dan `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` adalah segmen `[id]`; parameter permintaan adalah parameter dengan default:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

`id` non-numerik menjawab `404`, parameter permintaan buruk `422`.

## `@RequestBody`, `@Valid` dan `ResponseEntity`

```java filename="Item Baru.java"
public record NewItem(@NotBlank @Size(max = 100) String name,
                      @Positive double price) {}
```

```java filename="ItemController.java"
@PostMapping("/api/items")
public ResponseEntity<NewItem> create(@Valid @RequestBody NewItem item) {
    return ResponseEntity.status(HttpStatus.CREATED).body(item);
}
```

Catatan dan anotasinya adalah model Pydantic, selalu divalidasi:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `@RequestMapping` di kelas

```java filename="AdminController.java"
@RestController
@RequestMapping("/admin")
public class AdminController {
    @GetMapping("/stats")
    public Map<String, Integer> stats() {
        return Map.of("users", 3);
    }
}
```

Foldernya adalah pemetaannya:

```python filename="src/route/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` dan injeksi konstruktor

```java filename="SalamLayanan.java"
@Service
public class GreetingService {
    public String greet(String name) { return "Hello " + name; }
}

@RestController
public class GreetingController {
    private final GreetingService greetings;

    public GreetingController(GreetingService greetings) { this.greetings = greetings; }

    @GetMapping("/api/greet")
    public Map<String, String> greet(@RequestParam String name) {
        return Map.of("message", greetings.greet(name));
    }
}
```

Dalam file rute, layanannya adalah ketergantungan:

```python filename="src/layanan/greeting.py"
class GreetingService:
    def greet(self, name: str) -> str:
        return f"Hello {name}"


def get_greetings() -> GreetingService:
    return GreetingService()
```

```python filename=""
from nexy.http import Depends

from src.services.greeting import GreetingService, get_greetings


async def GET(name: str, greetings: GreetingService = Depends(get_greetings)):
    return {"message": greetings.greet(name)}
```

Untuk kelas `@Service` yang disuntikkan melalui konstruktor, dengan cakupan tunggal dan permintaan, gunakan [router modular](../routing/modular/dependency-injection.md): `@Injectable()` dan `@Controller()` bekerja seperti yang dilakukan `@Service` dan `@RestController`.

## Keamanan Musim Semi

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

`/admin/**` adalah folder `admin/`, dan `dependencies.py`-nya adalah aturannya:

```python filename="src/rute/admin/dependensi.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Filter dan `HandlerInterceptor`

```java filename="AppHeaderFilter.java"
@Component
public class AppHeaderFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
        res.setHeader("X-App", "demo");
        chain.doFilter(req, res);
    }
}
```

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `ResponseStatusException` dan `@ControllerAdvice`

```java filename="OrderController.java"
@GetMapping("/api/orders/{id}")
public Order order(@PathVariable long id) {
    return orders.findById(id)
        .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "No such order"));
}
```

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException

ORDERS = {1: {"id": 1, "total": 42}}


async def GET(id: int):
    if id not in ORDERS:
        raise HTTPException(status_code=404, detail="No such order")
    return ORDERS[id]
```

Jawabannya adalah `{"detail": "No such order"}`. Untuk HTML `error/404.html`, letakkan `notfound.nexy` di root rute:

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
```

## daun thyme

```java filename="UserPageController.java"
@Controller
public class UserPageController {
    @GetMapping("/users")
    public String users(Model model) {
        model.addAttribute("users", List.of(new User("Ada"), new User("Alan")));
        return "users";
    }
}
```

```html filename="templat/pengguna.html"
<ul>
  <li th:each="user : ${users}" th:text="${user.name}"></li>
</ul>
```

```nexy filename="src/rute/pengguna.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

`th:text` lolos dan `{{ }}` tidak: lolos dari apa yang diketik pengunjung dengan `| e`.

## Entitas dan repositori JPA

```java filename="Posting.java"
@Entity
public class Post {
    @Id @GeneratedValue Long id;
    String title;
    boolean published;
}

public interface PostRepository extends JpaRepository<Post, Long> {
    List<Post> findByPublishedTrue();
}
```

Dengan SQLModel, salah satu ORM `nx new` dapat melakukan perancah:

```python filename="src/model/post_model.py"
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    published: bool = False
```

```python filename="src/routes/api/posts/published.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


async def GET():
    with Session(engine) as session:
        posts = session.exec(select(Post).where(Post.published)).all()
    return {"titles": [post.title for post in posts]}
```

Migrasi jalur terbang atau Liquibase menjadi `nx migrate -m "add posts"` dan `nx migrate --upgrade`. Lihat [Database](../guides/databases.md).

## `application.properties`

| sepatu bot musim semi | Nexy |
|---|---|
| `server.port=8080` | `usePort = 8080` di `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` di `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, aktif secara default |
| `src/main/resources/static/` | `public/`, bertugas di `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Kesehatan aktuator

```properties filename="aplikasi.properti"
management.endpoints.web.exposure.include=health
```

Pemeriksaan kesehatan adalah rute yang sama seperti rute lainnya:

```python filename="src/rute/kesehatan.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` dan `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

Pekerjaan yang berjalan setelah jawabannya adalah tugas latar belakang:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Untuk tugas `@Scheduled`, jalankan penjadwal seperti APScheduler, atau tugas cron, di samping `nx start`.

## soket web

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Tes dengan MockMvc

```java filename="HaloControllerTest.java"
@WebMvcTest(HelloController.class)
class HelloControllerTest {
    @Autowired MockMvc mvc;

    @Test
    void hello() throws Exception {
        mvc.perform(get("/api/hello")).andExpect(jsonPath("$.message").value("Hello"));
    }
}
```

```python filename="tes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Berlari

| sepatu bot musim semi | Nexy |
|---|---|
| mulai.spring.io | `nx new` |
| `./mvnw spring-boot:run` dengan DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, lalu `nx start` |
| `./mvnw test` | `nx test` |

## Langkah selanjutnya

- [Dari NestJS hingga Nexy](nestjs.md): router modular, kelas demi kelas
- [Injeksi ketergantungan](../routing/modular/dependency-injection.md)
- [Pengendali rute](../routing/fbr/handlers/README.md)
- [Basis Data](../guides/databases.md)
