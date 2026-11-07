# Dari Boot Musim Semi hingga Nexy

Router modular Nexy mempertahankan bentuk aplikasi Spring Boot: `@RestController` adalah kelas `@Controller`, `@Service` adalah `@Injectable` yang disuntikkan melalui `__init__`, dan modul mengelompokkannya. Validasi Kacang menjadi Pydantic, dan halaman OpenAPI springdoc sudah ada di dalamnya.

Setiap bagian di bawah ini menunjukkan kebiasaan Spring Boot, lalu hal yang sama di Nexy.

## Menghidupkan router modular

```java filename="DemoAplikasi.java"
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) { SpringApplication.run(DemoApplication.class, args); }
}
```

Modul root adalah bidang `nexyconfig.py`, dan `nx dev` menyajikannya:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

Spring menemukan masalahnya dengan memindai paket; modul Nexy mencantumkannya, jadi apa yang disajikan modul ditulis di satu tempat.

## Sebuah pengontrol

```java filename="HaloController.java"
@RestController
@RequestMapping("/api/hello")
public class HelloController {
    @GetMapping
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

Jalurnya adalah argumen pertama `@Controller`, dan nama metodenya adalah kata kerja HTTP:

```python filename="src/apps/hello/hello_controller.py"
from nexy.decorators import Controller


@Controller("/api/hello")
class HelloController:
    async def get(self) -> dict:
        return {"message": "Hello"}
```

Sebuah pengontrol memiliki satu pengendali per kata kerja, jadi `@GetMapping` dan `@PostMapping` pada satu jalur adalah metode `get` dan `post` dari satu kelas. `GET /items` dan `GET /items/{id}` adalah dua pengontrol.

## `@PathVariable` dan `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` tetap berada di jalur dan menjadi parameter yang diketik; parameter permintaan adalah parameter dengan default:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/api/users/{id}")
class UserController:
    async def get(self, id: int, fields: str = "") -> dict:
        return {"id": id, "fields": fields}
```

Jawaban non-numerik `id` `404`, dan parameter permintaan bertipe salah `422`.

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

Catatan dan anotasinya adalah model Pydantic, selalu divalidasi, dan `@UseResponse` menetapkan status:

```python filename="src/apps/items/items_controller.py"
from pydantic import BaseModel, Field

from nexy.decorators import Controller, UseResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


@Controller("/api/items")
class ItemsController:
    @UseResponse(status_code=201)
    async def post(self, item: NewItem) -> NewItem:
        return item
```

## `@Service` dan injeksi konstruktor

```java filename="SalamLayanan.java"
@Service
public class GreetingService {
    public String greet(String name) { return "Hello " + name; }
}

@RestController
@RequestMapping("/api/greet")
public class GreetingController {
    private final GreetingService greetings;

    public GreetingController(GreetingService greetings) { this.greetings = greetings; }

    @GetMapping
    public Map<String, String> greet(@RequestParam String name) {
        return Map.of("message", greetings.greet(name));
    }
}
```

`@Service` adalah `@Injectable()`, dan anotasi `__init__` memberi tahu container apa yang harus disuntikkan:

```python filename="src/apps/greet/greeting_service.py"
from nexy.decorators import Injectable


@Injectable()
class GreetingService:
    def greet(self, name: str) -> str:
        return f"Hello {name}"
```

```python filename="src/apps/greet/greeting_controller.py"
from nexy.decorators import Controller

from .greeting_service import GreetingService


@Controller("/api/greet")
class GreetingController:
    def __init__(self, greetings: GreetingService) -> None:
        self.greetings = greetings

    async def get(self, name: str) -> dict:
        return {"message": self.greetings.greet(name)}
```

Kacang adalah singleton secara default, seperti di Spring. `@RequestScope` adalah `@Injectable(scope=Scope.REQUEST)`, dan `@Scope("prototype")` adalah `Scope.TRANSIENT`. Lihat [Injeksi ketergantungan](../routing/modular/dependency-injection.md).

## `@Configuration` kelas dan modul

Sebuah modul mencantumkan pengontrolnya dan layanan yang mereka gunakan, dan mengekspor apa yang mungkin dimasukkan oleh modul lain:

```python filename="src/apps/greet/greet_module.py"
from nexy.decorators import Module

from .greeting_controller import GreetingController
from .greeting_service import GreetingService


@Module()
class GreetModule:
    controllers = [GreetingController]
    providers = [GreetingService]
    exports = [GreetingService]
```

Modul root mengimpor yang lain:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .admin.admin_module import AdminModule
from .greet.greet_module import GreetModule
from .health_controller import PublicHealthController
from .hello.hello_controller import HelloController
from .items.items_controller import ItemsController
from .orders.orders_controller import OrderController
from .posts.posts_module import PostsModule
from .signup.signup_controller import SignupController
from .users.user_controller import UserController
from .users.users_page_controller import UsersPageController
from .ws.echo_controller import EchoController


@Module()
class AppModule:
    controllers = [
        HelloController,
        UserController,
        ItemsController,
        OrderController,
        SignupController,
        PublicHealthController,
        UsersPageController,
        EchoController,
    ]
    imports = [GreetModule, AdminModule, PostsModule]
```

## `@RequestMapping` di kelas

```java filename="AdminController.java"
@RestController
@RequestMapping("/admin")
public class AdminController {
    @GetMapping("/stats")
    public Map<String, Integer> stats() { return Map.of("users", 3); }

    @GetMapping("/health")
    public Map<String, String> health() { return Map.of("status", "UP"); }
}
```

Pemetaan bersama adalah `prefix` dari sebuah modul, dan setiap sub-jalur adalah pengontrol modul tersebut:

```python filename="src/apps/admin/admin_controllers.py"
from nexy.decorators import Controller, UseGuard

from .guards import require_admin


@Controller("/stats")
@UseGuard(require_admin)
class StatsController:
    async def get(self) -> dict:
        return {"users": 3}


@Controller("/health")
@UseGuard(require_admin)
class HealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

```python filename="src/apps/admin/admin_module.py"
from nexy.decorators import Module

from .admin_controllers import HealthController, StatsController


@Module(prefix="/admin")
class AdminModule:
    controllers = [StatsController, HealthController]
```

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

Penjaga adalah fungsi yang muncul ketika permintaan tidak dapat dilanjutkan. `@UseGuard` meletakkannya di pengontrol, atau pada satu metode, seperti `@PreAuthorize`:

```python filename="src/apps/admin/guards.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
```

## Filter

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

Filter untuk setiap permintaan adalah kelas middleware ASGI, yang tercantum di `nexyconfig.py`:

```python filename="src/middlewares/app_header.py"
from starlette.middleware.base import BaseHTTPMiddleware


class AppHeader(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["x-app"] = "demo"
        return response
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule
from src.middlewares.app_header import AppHeader


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useMiddlewares = [(AppHeader, {})]
```

Sebuah `HandlerInterceptor` yang hanya berjalan sebelum beberapa pengontrol menjadi penjaganya.

## `ResponseStatusException` dan `@ControllerAdvice`

```java filename="OrderController.java"
@GetMapping("/api/orders/{id}")
public Order order(@PathVariable long id) {
    return orders.findById(id)
        .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "No such order"));
}
```

```python filename="src/apps/orders/orders_controller.py"
from nexy.decorators import Controller
from nexy.http import HTTPException

ORDERS = {1: {"id": 1, "total": 42}}


@Controller("/api/orders/{id}")
class OrderController:
    async def get(self, id: int) -> dict:
        if id not in ORDERS:
            raise HTTPException(status_code=404, detail="No such order")
        return ORDERS[id]
```

Klien API yang mengirimkan `Accept: application/json` mendapat `{"detail": "No such order"}` dengan status yang Anda naikkan; browser mendapatkan halaman HTML tidak ditemukan.

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

Pengontrol mengembalikan tampilan seperti mengembalikan `"users"`: `useViews` merender file `.nexy`, dan `context`-nya adalah `Model`:

```nexy filename="src/apps/users/users_view.nexy"
---
users: prop[list]
---
<ul>
  {% for user in users %}
  <li>{{ user.name | e }}</li>
  {% endfor %}
</ul>
```

```python filename="src/apps/users/users_page_controller.py"
from nexy import useViews
from nexy.decorators import Controller


@Controller("/users")
class UsersPageController:
    async def get(self):
        users = [{"name": "Ada"}, {"name": "Alan"}]
        return useViews("src/apps/users/users_view.nexy", context={"users": users})
```

`th:text` lolos dan `{{ }}` tidak: lolos dari apa yang diketik pengunjung dengan `| e`. Sebuah halaman juga dapat menyimpan file `src/routes/`, yang disajikan di sebelah pengontrol.

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

Entitasnya adalah kelas SQLModel, dan repositorinya merupakan layanan yang dapat diinjeksi selama satu sesi:

```python filename="src/model/post_model.py"
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    published: bool = False
```

```python filename="src/apps/posts/post_repository.py"
from sqlmodel import Session, select

from nexy.decorators import Injectable
from src.configs.db import engine
from src.models.post_model import Post


@Injectable()
class PostRepository:
    def find_by_published_true(self) -> list[Post]:
        with Session(engine) as session:
            return list(session.exec(select(Post).where(Post.published)))
```

```python filename="src/apps/posts/posts_controller.py"
from nexy.decorators import Controller

from .post_repository import PostRepository


@Controller("/api/posts/published")
class PublishedPostsController:
    def __init__(self, posts: PostRepository) -> None:
        self.posts = posts

    async def get(self) -> dict:
        return {"titles": [post.title for post in self.posts.find_by_published_true()]}
```

```python filename="src/apps/posts/posts_module.py"
from nexy.decorators import Module

from .post_repository import PostRepository
from .posts_controller import PublishedPostsController


@Module()
class PostsModule:
    controllers = [PublishedPostsController]
    providers = [PostRepository]
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

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Kesehatan aktuator

```properties filename="aplikasi.properti"
management.endpoints.web.exposure.include=health
```

Pemeriksaan kesehatan adalah pengontrol seperti yang lainnya, berikut `/admin/health` di atas. Yang publik masuk ke modul root:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class PublicHealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

## `@Async` dan `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

Pekerjaan yang berjalan setelah jawabannya adalah tugas latar belakang, yang diambil sebagai parameter:

```python filename="src/apps/signup/signup_controller.py"
from nexy.decorators import Controller, UseResponse
from nexy.http import BackgroundTasks


def send_welcome(email: str) -> None: ...


@Controller("/api/signup")
class SignupController:
    @UseResponse(status_code=202)
    async def post(self, email: str, tasks: BackgroundTasks) -> dict:
        tasks.add_task(send_welcome, email)
        return {"queued": True}
```

Untuk tugas `@Scheduled`, jalankan penjadwal seperti APScheduler, atau tugas cron, di sebelah `nx start`.

## soket web

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

Metode `socket` membuka WebSocket di jalur pengontrolnya:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def socket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Klien terhubung ke `/ws/echo/`, dengan garis miring di belakangnya.

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
| mulai.spring.io | `nx new`, dengan router modular |
| `./mvnw spring-boot:run` dengan DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, lalu `nx start` |
| `./mvnw test` | `nx test` |

## Langkah selanjutnya

- [Perutean modular](../routing/modular/README.md)
- [Injeksi ketergantungan](../routing/modular/dependency-injection.md)
- [Penjaga dan metadata](../routing/modular/guards-and-metadata.md)
- [Dari NestJS ke Nexy](nestjs.md): router yang sama, dari TypeScript
