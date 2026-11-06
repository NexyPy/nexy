# От Spring Boot до Nexy

В Nexy метод Spring `@RestController` становится функцией в файле под `src/routes/` или методом класса `@Controller` в модульном маршрутизаторе: проверка bean-компонента становится Pydantic, а страница Springdoc OpenAPI встроена.

В каждом разделе ниже показаны привычки Spring Boot, а затем то же самое в Nexy.

## Контроллер

```java filename="Приветконтроллер.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

Путь к файлу — это URL-адрес, имя функции — метод HTTP:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` и `@RequestParam`

```java filename="Пользовательконтроллер.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` — сегмент `[id]`; параметр запроса — это параметр со значением по умолчанию:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

Нечисловой `id` отвечает на `404`, неправильный параметр запроса `422`.

## `@RequestBody`, `@Valid` и `ResponseEntity`

```java filename="НовыйItem.java"
public record NewItem(@NotBlank @Size(max = 100) String name,
                      @Positive double price) {}
```

```java filename="ItemController.java"
@PostMapping("/api/items")
public ResponseEntity<NewItem> create(@Valid @RequestBody NewItem item) {
    return ResponseEntity.status(HttpStatus.CREATED).body(item);
}
```

Запись и ее аннотации представляют собой модель Pydantic, всегда проверенную:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `@RequestMapping` в классе

```java filename="Админконтроллер.java"
@RestController
@RequestMapping("/admin")
public class AdminController {
    @GetMapping("/stats")
    public Map<String, Integer> stats() {
        return Map.of("users", 3);
    }
}
```

Папка представляет собой сопоставление:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` и внедрение конструктора

```java filename="ПриветствиеService.java"
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

В файле маршрута служба является зависимостью:

```python filename="src/services/greeting.py"
class GreetingService:
    def greet(self, name: str) -> str:
        return f"Hello {name}"


def get_greetings() -> GreetingService:
    return GreetingService()
```

```python filename="src/routes/api/greet.py"
from nexy.http import Depends

from src.services.greeting import GreetingService, get_greetings


async def GET(name: str, greetings: GreetingService = Depends(get_greetings)):
    return {"message": greetings.greet(name)}
```

Для классов `@Service`, внедренных через конструкторы, с одноэлементными и запросными областями, используйте [модульный маршрутизатор](../routing/modular/dependency-injection.md): `@Injectable()` и `@Controller()` работают так же, как `@Service` и `@RestController`.

## Весенняя безопасность

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

`/admin/**` — это папка `admin/`, а ее `dependencies.py` — это правило:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Фильтры и `HandlerInterceptor`

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

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `ResponseStatusException` и `@ControllerAdvice`

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

Ответ: `{"detail": "No such order"}`. Для HTML `error/404.html` поместите `notfound.nexy` в корень маршрута:

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
```

## Тимелиф

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

```html filename="шаблоны/users.html"
<ul>
  <li th:each="user : ${users}" th:text="${user.name}"></li>
</ul>
```

```nexy filename="src/маршруты/users.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

`th:text` экранируется, а `{{ }}` — нет: экранируйте то, что посетитель набрал с помощью `| e`.

## Объекты и репозитории JPA

```java filename="Пост.java"
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

С помощью SQLModel один из ORM `nx new` может формировать:

```python filename="src/models/post_model.py"
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

Миграции Flyway или Liquibase становятся `nx migrate -m "add posts"` и `nx migrate --upgrade`. См. [Базы данных](../guides/databases.md).

## `application.properties`

| Весенние ботинки | Некси |
|---|---|
| `server.port=8080` | `usePort = 8080` в `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` в `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, включено по умолчанию |
| `src/main/resources/static/` | `public/`, служил в `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Состояние привода

```properties filename="application.properties"
management.endpoints.web.exposure.include=health
```

Проверка работоспособности — это такой же маршрут, как и любой другой:

```python filename="src/routes/health.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` и `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

Работа, выполняемая после ответа, является фоновой задачей:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Для заданий `@Scheduled` запустите планировщик, например APScheduler, или задание cron рядом с `nx start`.

## Вебсокеты

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

## Тесты с MockMvc

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

```python filename="тесты/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Бег

| Весенние ботинки | Некси |
|---|---|
| start.spring.io | `nx new` |
| `./mvnw spring-boot:run` с DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, затем `nx start` |
| `./mvnw test` | `nx test` |

## Следующие шаги

- [От NestJS до Nexy](nestjs.md): модульный маршрутизатор, класс за классом
- [Внедрение зависимостей](../routing/modular/dependency-injection.md)
- [Обработчики маршрутов](../routing/fbr/handlers/README.md)
- [Базы данных](../guides/databases.md)
