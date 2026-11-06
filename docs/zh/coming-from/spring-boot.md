# 从 Spring Boot 到 Nexy

在 Nexy 中，Spring `@RestController` 方法变为 `src/routes/` 下文件中的函数，或者模块化路由器中 `@Controller` 类的方法：Bean Validation 变为 Pydantic，并且内置了 springdoc 的 OpenAPI 页面。

下面的每个部分都展示了 Spring Boot 习惯，然后是 Nexy 中的相同内容。

## 控制器一个

```java filename="HelloController.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

文件路径是 URL，函数名称是 HTTP 方法：

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` 和 `@RequestParam`

```java filename="用户控制器.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` 是 `[id]` 段；请求参数是一个带有默认值的参数：

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

非数字 `id` 回答 `404`，错误的请求参数 `422`。

## `@RequestBody`、`@Valid` 和 `ResponseEntity`

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

记录及其注释是一个 Pydantic 模型，始终经过验证：

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `@RequestMapping` 在课堂上

```java filename="管理控制器.java"
@RestController
@RequestMapping("/admin")
public class AdminController {
    @GetMapping("/stats")
    public Map<String, Integer> stats() {
        return Map.of("users", 3);
    }
}
```

该文件夹是映射：

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` 和构造函数注入

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

在路由文件中，服务是一个依赖项：

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

对于通过构造函数注入的具有单例和请求作用域的 `@Service` 类，请使用 [模块化路由器](../routing/modular/dependency-injection.md)：`@Injectable()` 和 `@Controller()` 的工作方式与 `@Service` 和 `@RestController` 的工作方式相同。

## 春季安全

```java filename="安全配置.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

`/admin/**` 是 `admin/` 文件夹，其 `dependencies.py` 是规则：

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## 过滤器和 `HandlerInterceptor`

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

## `ResponseStatusException` 和 `@ControllerAdvice`

```java filename="订单控制器.java"
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

答案是 `{"detail": "No such order"}`。对于 HTML `error/404.html`，将 `notfound.nexy` 放在路由根目录中：

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## 百里香叶

```java filename="用户页面控制器.java"
@Controller
public class UserPageController {
    @GetMapping("/users")
    public String users(Model model) {
        model.addAttribute("users", List.of(new User("Ada"), new User("Alan")));
        return "users";
    }
}
```

```html filename="模板/users.html"
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

`th:text` 转义，而 `{{ }}` 不转义：转义访问者用 `| e` 键入的内容。

## JPA 实体和存储库

```java filename="后java"
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

使用 SQLModel，ORM `nx new` 之一可以搭建：

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

Flyway 或 Liquibase 迁移变为 `nx migrate -m "add posts"` 和 `nx migrate --upgrade`。请参阅[数据库](../guides/databases.md)。

## `application.properties`

| 春季启动 | 内克西 |
|---|---|
| `server.port=8080` | `usePort = 8080` 在 `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` 在 `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`，默认开启 |
| `src/main/resources/static/` | `public/`，服务于 `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## 执行器健康状况

```properties filename="应用程序属性"
management.endpoints.web.exposure.include=health
```

健康检查与其他途径一样：

```python filename="src/routes/health.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` 和 `@Scheduled`

```java filename="邮件服务.java"
@Async
public void sendWelcome(String email) { ... }
```

答案之后运行的工作是后台任务：

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

对于 `@Scheduled` 作业，运行 `nx start` 旁边的调度程序（例如 APScheduler）或 cron 作业。

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

## 使用 MockMvc 进行测试

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

```python filename="测试/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## 跑步

| 春季启动 | 内克西 |
|---|---|
| 启动.spring.io | `nx new` |
| `./mvnw spring-boot:run` 使用 DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`，然后 `nx start` |
| `./mvnw test` | `nx test` |

## 后续步骤

- [从 NestJS 到 Nexy](nestjs.md)：逐级模块化路由器
- [依赖注入](../routing/modular/dependency-injection.md)
- [路由处理程序](../routing/fbr/handlers/README.md)
- [数据库](../guides/databases.md)
