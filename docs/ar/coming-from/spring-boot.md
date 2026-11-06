# من Spring Boot إلى Nexy

في Nexy، تصبح طريقة Spring `@RestController` وظيفة في ملف ضمن `src/routes/`، أو طريقة لفئة `@Controller` في جهاز التوجيه المعياري: يصبح التحقق من صحة Bean Pydantic، ويتم تضمين صفحة OpenAPI الخاصة بـ Springdoc.

يعرض كل قسم أدناه عادة Spring Boot، ثم نفس الشيء في Nexy.

## وحدة تحكم

```java filename="HelloController.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

مسار الملف هو عنوان URL، واسم الوظيفة هو طريقة HTTP:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` و `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` هو مقطع `[id]`؛ معلمة الطلب هي معلمة ذات قيمة افتراضية:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

إجابات غير رقمية `id` `404`، معلمة طلب غير صالحة `422`.

## `@RequestBody`، `@Valid` و `ResponseEntity`

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

السجل وشروحه نموذج Pydantic، يتم التحقق من صحته دائمًا:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `@RequestMapping` على الصف

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

المجلد هو التعيين:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` والحقن المنشئ

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

في ملف المسار، الخدمة هي تبعية:

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

بالنسبة للفئات `@Service` التي يتم حقنها من خلال المُنشئات، مع نطاقات فردية ونطاقات طلب، استخدم [[الموجه المعياري](../routing/modular/dependency-injection.md): يعمل `@Injectable()` و `@Controller()` بالطريقة التي يعمل بها `@Service` و `@RestController`.

## أمن الربيع

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

`/admin/**` هو المجلد `admin/`، و `dependencies.py` هي القاعدة:

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## المرشحات و `HandlerInterceptor`

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

## `ResponseStatusException` و `@ControllerAdvice`

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

الجواب `{"detail": "No such order"}`. بالنسبة إلى HTML `error/404.html`، ضع `notfound.nexy` في جذر المسارات:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## ورق الزعتر

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

```html filename="قوالب/users.html"
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

`th:text` يهرب و `{{ }}` لا: يهرب مما كتبه الزائر `| e`.

## كيانات ومستودعات JPA

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

باستخدام SQLModel، يمكن لأحد ORMs `nx new` أن يدعم:

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

تصبح عمليات ترحيل مسار الطيران أو Liquibase `nx migrate -m "add posts"` و `nx migrate --upgrade`. انظر [قواعد البيانات](../guides/databases.md).

## `application.properties`

| التمهيد الربيع | نكسي |
|---|---|
| `server.port=8080` | `usePort = 8080` في `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` في `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`، مفعل بشكل افتراضي |
| `src/main/resources/static/` | `public/`، خدم في `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## صحة المشغل

```properties filename="application.properties"
management.endpoints.web.exposure.include=health
```

الفحص الصحي هو طريق مثل أي طريق آخر:

```python filename="src/routes/health.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` و `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

العمل الذي يتم تشغيله بعد الإجابة هو مهمة خلفية:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

بالنسبة لمهام `@Scheduled`، قم بتشغيل برنامج جدولة مثل APScheduler، أو مهمة cron، بجوار `nx start`.

## WebSockets

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

## الاختبارات باستخدام MockMvc

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

```python filename="الاختبارات/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## الجري

| التمهيد الربيع | نكسي |
|---|---|
| start.spring.io | `nx new` |
| `./mvnw spring-boot:run` مع أدوات التطوير | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`، ثم `nx start` |
| `./mvnw test` | `nx test` |

## الخطوات التالية

- [من NestJS إلى Nexy](nestjs.md): جهاز التوجيه المعياري، فئة تلو الأخرى
- [حقن التبعية](../routing/modular/dependency-injection.md)
- [معالجات الطريق](../routing/fbr/handlers/README.md)
- [قواعد البيانات](../guides/databases.md)
