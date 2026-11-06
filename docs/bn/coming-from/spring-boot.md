# স্প্রিং বুট থেকে নেক্সি পর্যন্ত

Nexy এ স্প্রিং `@RestController` পদ্ধতিটি `src/routes/` এর অধীনে একটি ফাইলে একটি ফাংশন হয়ে যায়, অথবা মডুলার রাউটারে একটি `@Controller` ক্লাসের একটি পদ্ধতি: বিন যাচাইকরণ Pydantic হয়ে যায়, এবং স্প্রিংডকের OpenAPI পৃষ্ঠা তৈরি হয়।

নীচের প্রতিটি বিভাগ একটি স্প্রিং বুট অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একজন নিয়ামক

```java filename="HelloController.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

ফাইল পাথ হল URL, ফাংশনের নাম হল HTTP পদ্ধতি:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` এবং `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` একটি `[id]` সেগমেন্ট; একটি অনুরোধ প্যারামিটার একটি ডিফল্ট সহ একটি প্যারামিটার:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

একটি অ-সংখ্যাসূচক `id` উত্তর দেয় `404`, একটি খারাপ অনুরোধের পরামিতি `422`।

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

রেকর্ড এবং এর টীকাগুলি একটি Pydantic মডেল, সর্বদা বৈধ:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## ক্লাসে `@RequestMapping`

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

ফোল্ডারটি ম্যাপিং:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` এবং কনস্ট্রাক্টর ইনজেকশন

```java filename="GreetingService.java"
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

একটি রুট ফাইলে, পরিষেবাটি একটি নির্ভরতা:

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

সিঙ্গলটন এবং রিকোয়েস্ট স্কোপ সহ কনস্ট্রাক্টরের মাধ্যমে ইনজেকশন করা `@Service` ক্লাসের জন্য, [মডুলার রাউটার](../routing/modular/dependency-injection.md) ব্যবহার করুন: `@Injectable()` এবং `@Controller()` `@Service` এবং `@RestController` যেভাবে কাজ করে।

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

`/admin/**` হল `admin/` ফোল্ডার, এবং এর `dependencies.py` হল নিয়ম:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## ফিল্টার এবং `HandlerInterceptor`

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

## `ResponseStatusException` এবং `@ControllerAdvice`

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

উত্তর হল `{"detail": "No such order"}`। একটি HTML `error/404.html` এর জন্য, রুট রুটে একটি `notfound.nexy` রাখুন:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

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

```nexy filename="src/routes/users.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

`th:text` পালিয়ে যায় এবং `{{ }}` করে না: একজন দর্শক `| e` দিয়ে যা টাইপ করেন তা এড়িয়ে যান।

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

SQLModel এর সাথে, একটি ওআরএম `nx new` ভারা হতে পারে:

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

ফ্লাইওয়ে বা লিকুইবেস মাইগ্রেশন হয়ে যায় `nx migrate -m "add posts"` এবং `nx migrate --upgrade`। [ডাটাবেস](../guides/databases.md) দেখুন।

## `application.properties`

| বসন্ত বুট | নেক্সি |
|---|---|
| `server.port=8080` | `usePort = 8080` `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` `.env` মধ্যে |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, ডিফল্টরূপে চালু |
| `src/main/resources/static/` | `public/`, `/` এ পরিবেশিত |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## অ্যাকচুয়েটর স্বাস্থ্য

```properties filename="application.properties"
management.endpoints.web.exposure.include=health
```

একটি স্বাস্থ্য পরীক্ষা অন্য যে কোনো মত একটি রুট:

```python filename="src/routes/health.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` এবং `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

উত্তরের পরে যে কাজ চলে তা হল একটি ব্যাকগ্রাউন্ড টাস্ক:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
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

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

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
| start.spring.io | `nx new` |
| `./mvnw spring-boot:run` DevTools সহ | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, তারপর `nx start` |
| `./mvnw test` | `nx test` |

## পরবর্তী পদক্ষেপ

- [থেকে NestJS থেকে Nexy](nestjs.md): মডুলার রাউটার, ক্লাস বাই ক্লাস
- [নির্ভরতা ইনজেকশন ](../routing/modular/dependency-injection.md)
- [রুট হ্যান্ডলার](../routing/fbr/handlers/README.md)
- [ডাটাবেস](../guides/databases.md)
