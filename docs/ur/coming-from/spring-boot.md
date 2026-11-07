# اسپرنگ بوٹ سے لے کر نیکسی تک

Nexy کا ماڈیولر راؤٹر اسپرنگ بوٹ ایپ کی شکل کو برقرار رکھتا ہے: ایک `@RestController` ایک `@Controller` کلاس ہے، ایک `@Service` ایک `@Injectable` ہے جسے `__init__` کے ذریعے انجکشن لگایا جاتا ہے، اور ایک ماڈیول ان کو گروپ کرتا ہے۔ بین کی توثیق Pydantic ہو جاتی ہے، اور springdoc کا OpenAPI صفحہ اندر بن جاتا ہے۔

ذیل میں ہر سیکشن اسپرنگ بوٹ کی عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ماڈیولر راؤٹر کو آن کرنا

```java filename="DemoApplication.java"
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) { SpringApplication.run(DemoApplication.class, args); }
}
```

روٹ ماڈیول `nexyconfig.py` کا ایک فیلڈ ہے، اور `nx dev` اس کی خدمت کرتا ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

اسپرنگ پیکجوں کو اسکین کرکے اپنی پھلیاں ڈھونڈتا ہے۔ ایک Nexy ماڈیول ان کی فہرست بناتا ہے، لہذا ماڈیول جو کام کرتا ہے وہ ایک جگہ لکھا جاتا ہے۔

## ایک کنٹرولر

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

راستہ `@Controller` کی پہلی دلیل ہے، اور طریقہ کا نام HTTP فعل ہے:

```python filename="src/apps/hello/hello_controller.py"
from nexy.decorators import Controller


@Controller("/api/hello")
class HelloController:
    async def get(self) -> dict:
        return {"message": "Hello"}
```

ایک کنٹرولر کا فی فعل ایک ہینڈلر ہوتا ہے، لہذا `@GetMapping` اور `@PostMapping` ایک راستے پر ایک طبقے کے `get` اور `post` طریقے ہیں۔ `GET /items` اور `GET /items/{id}` دو کنٹرولر ہیں۔

## `@PathVariable` اور `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` راستے میں رہتا ہے اور ٹائپ شدہ پیرامیٹر بن جاتا ہے۔ ایک درخواست پیرامیٹر ڈیفالٹ کے ساتھ ایک پیرامیٹر ہے:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/api/users/{id}")
class UserController:
    async def get(self, id: int, fields: str = "") -> dict:
        return {"id": id, "fields": fields}
```

ایک غیر عددی `id` جواب دیتا ہے `404`، اور غلط قسم کا ایک درخواست پیرامیٹر `422`۔

## `@RequestBody`، `@Valid` اور `ResponseEntity`

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

ریکارڈ اور اس کی تشریحات ایک Pydantic ماڈل ہیں، ہمیشہ توثیق کی جاتی ہیں، اور `@UseResponse` سٹیٹس سیٹ کرتی ہیں:

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

## `@Service` اور کنسٹرکٹر انجیکشن

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

`@Service` ہے `@Injectable()`، اور `__init__` کی تشریح کنٹینر کو بتاتی ہے کہ کیا انجیکشن لگانا ہے:

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

ایک بین بطور ڈیفالٹ سنگلٹن ہے، جیسا کہ بہار میں۔ `@RequestScope` ہے `@Injectable(scope=Scope.REQUEST)`، اور `@Scope("prototype")` ہے `Scope.TRANSIENT`۔ دیکھیں [انحصار انجکشن](../routing/modular/dependency-injection.md)۔

## `@Configuration` کلاسز اور ماڈیولز

ایک ماڈیول اپنے کنٹرولرز اور ان خدمات کی فہرست بناتا ہے جو وہ استعمال کرتے ہیں، اور برآمد کرتا ہے کہ دوسرے ماڈیول کیا انجیکشن لگا سکتے ہیں:

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

روٹ ماڈیول دوسروں کو درآمد کرتا ہے:

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

## `@RequestMapping` کلاس پر

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

مشترکہ نقشہ سازی ایک ماڈیول کا `prefix` ہے، اور ہر ذیلی راستہ اس ماڈیول کا کنٹرولر ہے:

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

## بہار کی حفاظت

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

گارڈ ایک ایسا فنکشن ہے جو اس وقت اٹھاتا ہے جب درخواست جاری نہ ہو۔ `@UseGuard` اسے کنٹرولر پر رکھتا ہے، یا ایک طریقہ پر رکھتا ہے، جیسے `@PreAuthorize`:

```python filename="src/apps/admin/guards.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
```

## فلٹرز

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

ہر درخواست کے لیے ایک فلٹر ASGI مڈل ویئر کلاس ہے، جو `nexyconfig.py` میں درج ہے:

```python filename="src/midlewares/app_header.py"
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

ایک `HandlerInterceptor` جو صرف کچھ کنٹرولرز سے پہلے چلتا ہے ان پر ایک محافظ ہوتا ہے۔

## `ResponseStatusException` اور `@ControllerAdvice`

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

ایک API کلائنٹ جو بھیجتا ہے `Accept: application/json` کو `{"detail": "No such order"}` حاصل ہوتا ہے اس اسٹیٹس کے ساتھ جو آپ نے اٹھایا ہے۔ ایک براؤزر کو HTML نا پایا جانے والا صفحہ ملتا ہے۔

## Thymeleaf

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

ایک کنٹرولر ایک منظر کو واپس کرتا ہے جس طرح یہ `"users"`: `useViews` ایک `.nexy` فائل کو پیش کرتا ہے، اور اس کا `context` `Model` ہے:

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

`th:text` فرار ہوتا ہے اور `{{ }}` نہیں ہوتا ہے: اس سے بچ جاتا ہے جسے ایک وزیٹر `| e` کے ساتھ ٹائپ کرتا ہے۔ ایک صفحہ `src/routes/` کی فائل بھی رہ سکتا ہے، جو کنٹرولرز کے ساتھ پیش کی جاتی ہے۔

## جے پی اے ادارے اور ذخیرے

```java filename="پوسٹ۔جاوا"
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

ہستی ایک SQLModel کلاس ہے، اور ذخیرہ ایک سیشن کے ارد گرد ایک انجیکشن قابل خدمت ہے:

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

Flyway یا Liquibase کی منتقلی `nx migrate -m "add posts"` اور `nx migrate --upgrade` بن جاتی ہے۔ دیکھیں [ڈیٹا بیس](../guides/databases.md)۔

## `application.properties`

| اسپرنگ بوٹ | نیکسی |
|---|---|
| `server.port=8080` | `usePort = 8080` میں `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` میں `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`، بطور ڈیفالٹ آن |
| `src/main/resources/static/` | `public/`، `/` میں خدمت کی |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## ایکچیویٹر کی صحت

```properties filename="application.properties"
management.endpoints.web.exposure.include=health
```

صحت کی جانچ کسی دوسرے کی طرح ایک کنٹرولر ہے، یہاں اوپر والا `/admin/health`۔ ایک عوامی روٹ ماڈیول میں جاتا ہے:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class PublicHealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

## `@Async` اور `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

جواب کے بعد چلنے والا کام ایک پس منظر کا کام ہے، جسے پیرامیٹر کے طور پر لیا گیا ہے:

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

`@Scheduled` ملازمتوں کے لیے، `nx start` کے آگے ایک شیڈیولر چلائیں جیسے APScheduler، یا کرون جاب۔

## ویب ساکٹس

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

ایک `socket` طریقہ اپنے کنٹرولر کے راستے پر ایک WebSocket کو کھولتا ہے:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def socket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

کلائنٹ ٹریلنگ سلیش کے ساتھ `/ws/echo/` سے جڑتے ہیں۔

## MockMvc کے ساتھ ٹیسٹ

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

## چل رہا ہے۔

| اسپرنگ بوٹ | نیکسی |
|---|---|
| start.spring.io | `nx new`، ماڈیولر راؤٹر کے ساتھ |
| `./mvnw spring-boot:run` DevTools کے ساتھ | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`، پھر `nx start` |
| `./mvnw test` | `nx test` |

## اگلے اقدامات

- [ماڈیولر روٹنگ](../routing/modular/README.md)
- [انحصار انجکشن](../routing/modular/dependency-injection.md)
- [گارڈز اور میٹا ڈیٹا ](../routing/modular/guards-and-metadata.md)
- [سے NestJS سے Nexy](nestjs.md): وہی راؤٹر، TypeScript سے
