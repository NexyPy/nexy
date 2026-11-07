# স্প্রিং বুট থেকে নেক্সি পর্যন্ত

Nexy-এর মডুলার রাউটার একটি স্প্রিং বুট অ্যাপের আকৃতি রাখে: একটি `@RestController` একটি `@Controller` ক্লাস, একটি `@Service` হল একটি `@Injectable` যা `__init__` এর মাধ্যমে ইনজেক্ট করা হয়, এবং একটি মডিউল তাদের দলবদ্ধ করে। বিন বৈধকরণ হয়ে যায় Pydantic, এবং স্প্রিংডকের OpenAPI পৃষ্ঠা তৈরি হয়।

নীচের প্রতিটি বিভাগ একটি স্প্রিং বুট অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## মডুলার রাউটার চালু করা হচ্ছে

```java filename="DemoApplication.java"
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) { SpringApplication.run(DemoApplication.class, args); }
}
```

রুট মডিউল হল `nexyconfig.py` এর একটি ক্ষেত্র, এবং `nx dev` এটি পরিবেশন করে:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

প্যাকেজ স্ক্যান করে বসন্ত তার মটরশুটি খুঁজে পায়; একটি Nexy মডিউল তাদের তালিকা করে, তাই একটি মডিউল যা পরিবেশন করে তা এক জায়গায় লেখা হয়।

## একজন নিয়ামক

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

পাথ হল `@Controller` এর প্রথম আর্গুমেন্ট, এবং পদ্ধতির নাম হল HTTP ক্রিয়া:

```python filename="src/apps/hello/hello_controller.py"
from nexy.decorators import Controller


@Controller("/api/hello")
class HelloController:
    async def get(self) -> dict:
        return {"message": "Hello"}
```

একটি কন্ট্রোলারের প্রতি ক্রিয়াপদের একটি হ্যান্ডলার থাকে, তাই `@GetMapping` এবং `@PostMapping` এক পথে একটি শ্রেণীর `get` এবং `post` পদ্ধতি। `GET /items` এবং `GET /items/{id}` দুটি নিয়ন্ত্রক।

## `@PathVariable` এবং `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` পথে থাকে এবং একটি টাইপ করা প্যারামিটার হয়ে যায়; একটি অনুরোধ প্যারামিটার একটি ডিফল্ট সহ একটি প্যারামিটার:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/api/users/{id}")
class UserController:
    async def get(self, id: int, fields: str = "") -> dict:
        return {"id": id, "fields": fields}
```

একটি অ-সাংখ্যিক `id` উত্তর দেয় `404`, এবং ভুল ধরনের একটি অনুরোধ প্যারামিটার `422`।

## `@RequestBody`, `@Valid` এবং `ResponseEntity`

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

রেকর্ড এবং এর টীকা হল একটি Pydantic মডেল, সর্বদা যাচাই করা হয় এবং `@UseResponse` স্থিতি সেট করে:

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

## `@Service` এবং কনস্ট্রাক্টর ইনজেকশন

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

`@Service` হল `@Injectable()`, এবং `__init__` এর টীকাটি কন্টেইনারকে কী ইনজেকশন করতে হবে তা বলে:

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

একটি মটরশুটি ডিফল্টভাবে একটি সিঙ্গলটন, যেমন বসন্তে। `@RequestScope` হল `@Injectable(scope=Scope.REQUEST)`, এবং `@Scope("prototype")` হল `Scope.TRANSIENT`। দেখুন [নির্ভরতা ইনজেকশন](../routing/modular/dependency-injection.md)।

## `@Configuration` ক্লাস এবং মডিউল

একটি মডিউল তার নিয়ামক এবং তারা যে পরিষেবাগুলি ব্যবহার করে তা তালিকাভুক্ত করে এবং অন্যান্য মডিউলগুলি কী ইনজেকশন করতে পারে তা রপ্তানি করে:

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

রুট মডিউল অন্যদের আমদানি করে:

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

## ক্লাসে `@RequestMapping`

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

একটি ভাগ করা ম্যাপিং হল একটি মডিউলের `prefix`, এবং প্রতিটি উপ-পাথ সেই মডিউলের একটি নিয়ামক:

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

## বসন্ত নিরাপত্তা

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

একটি গার্ড একটি ফাংশন যা উত্থাপন যখন অনুরোধ না যেতে পারে. `@UseGuard` এটি একটি নিয়ামক বা একটি পদ্ধতিতে রাখে, যেমন `@PreAuthorize`:

```python filename="src/apps/admin/guards.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
```

## ফিল্টার

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

প্রতিটি অনুরোধের জন্য একটি ফিল্টার হল একটি ASGI মিডলওয়্যার ক্লাস, `nexyconfig.py` এ তালিকাভুক্ত:

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

একটি `HandlerInterceptor` যা কেবলমাত্র কিছু নিয়ন্ত্রকের সামনে চলে তাদের উপর একটি প্রহরী।

## `ResponseStatusException` এবং `@ControllerAdvice`

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

একটি এপিআই ক্লায়েন্ট যেটি `Accept: application/json` পাঠায় সে আপনার উত্থাপিত স্ট্যাটাস সহ `{"detail": "No such order"}` পায়; একটি ব্রাউজার এইচটিএমএল না পাওয়া পৃষ্ঠা পায়।

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

একটি কন্ট্রোলার একটি দৃশ্য ফেরত দেয় যেভাবে এটি ফেরত দেয় `"users"`: `useViews` একটি `.nexy` ফাইল রেন্ডার করে এবং এটির `context` হল `Model`:

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

`th:text` পালিয়ে যায় এবং `{{ }}` করে না: একজন দর্শক `| e` দিয়ে যা টাইপ করেন তা এড়িয়ে যান। একটি পৃষ্ঠাও একটি ফাইল থাকতে পারে `src/routes/`, কন্ট্রোলারের পাশে পরিবেশিত হয়।

## JPA সত্তা এবং সংগ্রহস্থল

```java filename="পোস্ট.জাভা"
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

সত্তাটি একটি SQLModel শ্রেণি, এবং সংগ্রহস্থলটি একটি সেশনের চারপাশে একটি ইনজেকশনযোগ্য পরিষেবা:

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

ফ্লাইওয়ে বা লিকুইবেস মাইগ্রেশন `nx migrate -m "add posts"` এবং `nx migrate --upgrade` হয়ে যায়। [ডেটাবেস](../guides/databases.md) দেখুন।

## `application.properties`

| বসন্ত বুট | নেক্সি |
|---|---|
| `server.port=8080` | `usePort = 8080` `nexyconfig.py` মধ্যে |
| `spring.datasource.url` | `DATABASE_URL` `.env` মধ্যে |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, ডিফল্টরূপে চালু |
| `src/main/resources/static/` | `public/`, `/` এ পরিবেশিত |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## অ্যাকচুয়েটর স্বাস্থ্য

```properties filename="application.properties"
management.endpoints.web.exposure.include=health
```

একটি স্বাস্থ্য পরীক্ষা অন্য যে কোন মত একটি নিয়ন্ত্রক, এখানে `/admin/health` উপরে একটি. একটি সর্বজনীন রুট মডিউলে যায়:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class PublicHealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

## `@Async` এবং `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

উত্তরের পরে যে কাজটি চলে তা হল একটি ব্যাকগ্রাউন্ড টাস্ক, একটি প্যারামিটার হিসাবে নেওয়া হয়েছে:

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

`@Scheduled` কাজের জন্য, `nx start` এর পাশে APScheduler বা ক্রোন কাজের মতো একটি সময়সূচী চালান।

## ওয়েবসকেট

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

একটি `socket` পদ্ধতি তার নিয়ামকের পথে একটি WebSocket খোলে:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def socket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

ক্লায়েন্টরা `/ws/echo/` এর সাথে সংযোগ স্থাপন করে, ট্রেলিং স্ল্যাশ সহ।

## MockMvc এর সাথে পরীক্ষা

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

## চলছে

| বসন্ত বুট | নেক্সি |
|---|---|
| start.spring.io | `nx new`, মডুলার রাউটার সহ |
| `./mvnw spring-boot:run` DevTools সহ | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, তারপর `nx start` |
| `./mvnw test` | `nx test` |

## পরবর্তী পদক্ষেপ

- [মডুলার রাউটিং](../routing/modular/README.md)
- [নির্ভরতা ইনজেকশন](../routing/modular/dependency-injection.md)
- [গার্ড এবং মেটাডেটা](../routing/modular/guards-and-metadata.md)
- [থেকে NestJS থেকে Nexy](nestjs.md): একই রাউটার, TypeScript থেকে
