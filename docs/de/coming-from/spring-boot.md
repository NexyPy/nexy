# Von Spring Boot bis Nexy

Der modulare Router von Nexy behält die Form einer Spring Boot-App: Eine `@RestController` ist eine `@Controller`-Klasse, eine `@Service` ist eine über `__init__` injizierte `@Injectable` und ein Modul gruppiert sie. Die Bean-Validierung wird zu Pydantic und die Seite OpenAPI von springdoc ist integriert.

Jeder Abschnitt unten zeigt eine Spring Boot-Gewohnheit, dann dasselbe in Nexy.

## Einschalten des modularen Routers

```java filename="DemoApplication.java"
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) { SpringApplication.run(DemoApplication.class, args); }
}
```

Das Stammmodul ist ein Feld von `nexyconfig.py` und `nx dev` bedient es:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

Der Frühling findet seine Stärken, indem er Pakete scannt; Ein Nexy-Modul listet sie auf, sodass die Aufgaben eines Moduls an einer Stelle geschrieben werden.

## Ein Controller

```java filename="HelloController.java"
@RestController
@RequestMapping("/api/hello")
public class HelloController {
    @GetMapping
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

Der Pfad ist das erste Argument von `@Controller` und der Methodenname ist das HTTP-Verb:

```python filename="src/apps/hello/hello_controller.py"
from nexy.decorators import Controller


@Controller("/api/hello")
class HelloController:
    async def get(self) -> dict:
        return {"message": "Hello"}
```

Ein Controller hat einen Handler pro Verb, daher sind `@GetMapping` und `@PostMapping` auf einem Pfad die Methoden `get` und `post` einer Klasse. `GET /items` und `GET /items/{id}` sind zwei Controller.

## `@PathVariable` und `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` bleibt im Pfad und wird zu einem typisierten Parameter; Ein Anforderungsparameter ist ein Parameter mit einem Standardwert:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/api/users/{id}")
class UserController:
    async def get(self, id: int, fields: str = "") -> dict:
        return {"id": id, "fields": fields}
```

Ein nicht numerischer Wert `id` antwortet `404` und ein Anforderungsparameter vom falschen Typ `422`.

## `@RequestBody`, `@Valid` und `ResponseEntity`

```java filename="NewItem.java"
public record NewItem(@NotBlank @Size(max = 100) String name,
                      @Positive double price) {}
```

```java filename="ItemController.java"
@PostMapping("/api/items")
public ResponseEntity<NewItem> create(@Valid @RequestBody NewItem item) {
    return ResponseEntity.status(HttpStatus.CREATED).body(item);
}
```

Der Datensatz und seine Anmerkungen sind ein Pydantic-Modell, immer validiert, und `@UseResponse` legt den Status fest:

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

## `@Service` und Konstruktorinjektion

```java filename="GreetingService.java"
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

`@Service` ist `@Injectable()`, und die Annotation von `__init__` teilt dem Container mit, was injiziert werden soll:

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

Eine Bean ist standardmäßig ein Singleton, wie in Spring. `@RequestScope` ist `@Injectable(scope=Scope.REQUEST)` und `@Scope("prototype")` ist `Scope.TRANSIENT`. Siehe [Abhängigkeitsinjektion](../routing/modular/dependency-injection.md).

## `@Configuration` Kurse und Module

Ein Modul listet seine Controller und die von ihnen genutzten Dienste auf und exportiert, was andere Module möglicherweise injizieren:

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

Das Root-Modul importiert die anderen:

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

## `@RequestMapping` über die Klasse

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

Eine gemeinsame Zuordnung ist die `prefix` eines Moduls, und jeder Unterpfad ist ein Controller dieses Moduls:

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

## Frühlingssicherheit

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

Ein Guard ist eine Funktion, die ausgelöst wird, wenn die Anfrage möglicherweise nicht ausgeführt wird. `@UseGuard` legt es auf einen Controller oder auf eine Methode, wie `@PreAuthorize`:

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

Ein Filter für jede Anfrage ist eine ASGI-Middleware-Klasse, aufgeführt in `nexyconfig.py`:

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

Ein `HandlerInterceptor`, der nur vor einigen Controllern läuft, schützt sie.

## `ResponseStatusException` und `@ControllerAdvice`

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

Ein API-Client, der `Accept: application/json` sendet, erhält `{"detail": "No such order"}` mit dem von Ihnen ausgelösten Status; Ein Browser erhält die HTML-Seite „Nicht gefunden“.

## Thymianblatt

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

```html filename="templates/users.html"
<ul>
  <li th:each="user : ${users}" th:text="${user.name}"></li>
</ul>
```

Ein Controller gibt eine Ansicht auf die Art und Weise zurück, wie er `"users"` zurückgibt: `useViews` rendert eine `.nexy`-Datei, und ihr `context` ist das `Model`:

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

`th:text` entgeht und `{{ }}` nicht: Entkommt dem, was ein Besucher mit `| e` eingegeben hat. Eine Seite kann auch eine Datei von `src/routes/` sein, die neben den Controllern bereitgestellt wird.

## JPA-Entitäten und Repositorys

```java filename="Post.java"
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

Die Entität ist eine SQLModel-Klasse und das Repository ein injizierbarer Dienst rund um eine Sitzung:

```python filename="src/models/post_model.py"
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

Flyway- oder Liquibase-Migrationen werden zu `nx migrate -m "add posts"` und `nx migrate --upgrade`. Siehe [Datenbanken](../guides/databases.md).

## `application.properties`

| Frühlingsstiefel | Nexy |
|---|---|
| `server.port=8080` | `usePort = 8080` in `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` in `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, standardmäßig aktiviert |
| `src/main/resources/static/` | `public/`, zugestellt in `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Aktuatorzustand

```properties filename="application.properties"
management.endpoints.web.exposure.include=health
```

Ein Gesundheitscheck ist ein Controller wie jeder andere, hier der `/admin/health` oben. Ein öffentliches Modul befindet sich im Root-Modul:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class PublicHealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

## `@Async` und `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

Die Arbeit, die nach der Antwort ausgeführt wird, ist eine Hintergrundaufgabe, die als Parameter verwendet wird:

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

Führen Sie für `@Scheduled`-Jobs einen Planer wie APScheduler oder einen Cron-Job neben `nx start` aus.

## WebSockets

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

Eine `socket`-Methode öffnet eine WebSocket auf dem Pfad ihres Controllers:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def socket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Clients stellen eine Verbindung zu `/ws/echo/` mit dem abschließenden Schrägstrich her.

## Tests mit MockMvc

```java filename="HelloControllerTest.java"
@WebMvcTest(HelloController.class)
class HelloControllerTest {
    @Autowired MockMvc mvc;

    @Test
    void hello() throws Exception {
        mvc.perform(get("/api/hello")).andExpect(jsonPath("$.message").value("Hello"));
    }
}
```

```python filename="tests/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Laufen

| Frühlingsstiefel | Nexy |
|---|---|
| start.spring.io | `nx new`, mit dem modularen Router |
| `./mvnw spring-boot:run` mit DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, dann `nx start` |
| `./mvnw test` | `nx test` |

## Nächste Schritte

- [Modulares Routing](../routing/modular/README.md)
- [Abhängigkeitsinjektion](../routing/modular/dependency-injection.md)
- [Guards und Metadaten](../routing/modular/guards-and-metadata.md)
- [Von NestJS zu Nexy](nestjs.md): derselbe Router, von TypeScript
