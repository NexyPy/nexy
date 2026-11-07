# От Spring Boot до Nexy

Модульный маршрутизатор Nexy сохраняет форму приложения Spring Boot: `@RestController` - это класс `@Controller`, `@Service` - это `@Injectable`, внедренный через `__init__`, а модуль группирует их. Проверка bean-компонента становится Pydantic, и страница Springdoc OpenAPI встроена.

В каждом разделе ниже показаны привычки Spring Boot, а затем то же самое в Nexy.

## Включение модульного маршрутизатора

```java filename="Демо-приложение.java"
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) { SpringApplication.run(DemoApplication.class, args); }
}
```

Корневой модуль - это поле `nexyconfig.py`, а `nx dev` обслуживает его:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

Spring находит свои компоненты путем сканирования пакетов; модуль Nexy перечисляет их, поэтому то, что обслуживает модуль, написано в одном месте.

## Контроллер

```java filename="Приветконтроллер.java"
@RestController
@RequestMapping("/api/hello")
public class HelloController {
    @GetMapping
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

Путь - это первый аргумент `@Controller`, а имя метода - это HTTP-глагол:

```python filename="src/apps/hello/hello_controller.py"
from nexy.decorators import Controller


@Controller("/api/hello")
class HelloController:
    async def get(self) -> dict:
        return {"message": "Hello"}
```

Контроллер имеет один обработчик для каждой команды, поэтому `@GetMapping` и `@PostMapping` на одном пути являются методами `get` и `post` одного класса. `GET /items` и `GET /items/{id}` - два контроллера.

## `@PathVariable` и `@RequestParam`

```java filename="Пользовательконтроллер.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` остается в пути и становится типизированным параметром; параметр запроса - это параметр со значением по умолчанию:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/api/users/{id}")
class UserController:
    async def get(self, id: int, fields: str = "") -> dict:
        return {"id": id, "fields": fields}
```

Нечисловой `id` отвечает на `404` и параметр запроса неправильного типа `422`.

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

Запись и ее аннотации представляют собой модель Pydantic, всегда проверенную, а `@UseResponse` устанавливает статус:

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

## `@Service` и внедрение конструктора

```java filename="ПриветствиеService.java"
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

`@Service` - это `@Injectable()`, а аннотация `__init__` сообщает контейнеру, что нужно внедрить:

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

По умолчанию компонент является синглтоном, как и в Spring. `@RequestScope` - это `@Injectable(scope=Scope.REQUEST)`, а `@Scope("prototype")` - это `Scope.TRANSIENT`. См. [Внедрение зависимостей](../routing/modular/dependency-injection.md).

## `@Configuration` классы и модули

Модуль перечисляет свои контроллеры и службы, которые они используют, а также экспортирует то, что могут внедрить другие модули:

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

Корневой модуль импортирует остальные:

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

## `@RequestMapping` в классе

```java filename="Админконтроллер.java"
@RestController
@RequestMapping("/admin")
public class AdminController {
    @GetMapping("/stats")
    public Map<String, Integer> stats() { return Map.of("users", 3); }

    @GetMapping("/health")
    public Map<String, String> health() { return Map.of("status", "UP"); }
}
```

Общее сопоставление - это `prefix` модуля, а каждый подпуть является контроллером этого модуля:

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

Guard - это функция, которая вызывается, когда запрос не может быть выполнен. `@UseGuard` помещает его в контроллер или в один метод, например `@PreAuthorize`:

```python filename="src/apps/admin/guards.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
```

## Фильтры

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

Фильтром для каждого запроса является класс промежуточного программного обеспечения ASGI, указанный в `nexyconfig.py`:

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

`HandlerInterceptor` который запускается только перед некоторыми контроллерами, является их защитой.

## `ResponseStatusException` и `@ControllerAdvice`

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

Клиент API, который отправляет `Accept: application/json` получает `{"detail": "No such order"}` с поднятым вами статусом; браузер получает HTML-страницу, которая не найдена.

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

Контроллер возвращает представление так, как он возвращает `"users"`: `useViews` отображает файл `.nexy`, а его `context` - это `Model`:

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

`th:text` экранируется, а `{{ }}` - нет: экранируйте то, что посетитель набрал с помощью `| e`. Страница также может содержать файл `src/routes/`, обслуживаемый рядом с контроллерами.

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

Объект представляет собой класс SQLModel, а репозиторий - внедряемый сервис вокруг сеанса:

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

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Состояние привода

```properties filename="application.properties"
management.endpoints.web.exposure.include=health
```

Проверка работоспособности - это такой же контроллер, как и любой другой, здесь `/admin/health` выше. Публичный находится в корневом модуле:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class PublicHealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

## `@Async` и `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

Работа, выполняемая после ответа, является фоновой задачей, принимаемой в качестве параметра:

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

Метод `socket` открывает WebSocket на пути своего контроллера:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def socket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Клиенты подключаются к `/ws/echo/` с косой чертой в конце.

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
| start.spring.io | `nx new`, с модульным маршрутизатором |
| `./mvnw spring-boot:run` с DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, затем `nx start` |
| `./mvnw test` | `nx test` |

## Следующие шаги

- [Модульная маршрутизация](../routing/modular/README.md)
- [Внедрение зависимостей](../routing/modular/dependency-injection.md)
- [Охранники и метаданные](../routing/modular/guards-and-metadata.md)
- [От NestJS до Nexy](nestjs.md): тот же роутер, от TypeScript
