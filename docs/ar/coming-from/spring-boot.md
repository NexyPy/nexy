# من Spring Boot إلى Nexy

يحافظ جهاز التوجيه المعياري الخاص بـ Nexy على شكل تطبيق Spring Boot: a `@RestController` هو فئة `@Controller`، و `@Service` هو `@Injectable` يتم حقنه من خلال `__init__`، ووحدة نمطية تجمعهم. يصبح التحقق من صحة الفول Pydantic، ويتم تضمين صفحة OpenAPI الخاصة بـ Springdoc.

يعرض كل قسم أدناه عادة Spring Boot، ثم نفس الشيء في Nexy.

## تشغيل جهاز التوجيه المعياري

```java filename="DemoApplication.java"
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) { SpringApplication.run(DemoApplication.class, args); }
}
```

الوحدة الجذرية عبارة عن حقل `nexyconfig.py`، و `nx dev` يخدمها:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

يجد الربيع حبوبه عن طريق مسح الطرود؛ تسردها وحدة Nexy، لذا فإن ما تخدمه الوحدة يتم كتابته في مكان واحد.

## وحدة تحكم

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

المسار هو الوسيطة الأولى لـ `@Controller`، واسم الطريقة هو فعل HTTP:

```python filename="src/apps/hello/hello_controller.py"
from nexy.decorators import Controller


@Controller("/api/hello")
class HelloController:
    async def get(self) -> dict:
        return {"message": "Hello"}
```

تحتوي وحدة التحكم على معالج واحد لكل فعل، لذا فإن `@GetMapping` و `@PostMapping` على مسار واحد هما الطريقتان `get` و `post` لفئة واحدة. `GET /items` و `GET /items/{id}` هما متحكمان.

## `@PathVariable` و `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` يبقى في المسار ويصبح معلمة مكتوبة؛ معلمة الطلب هي معلمة ذات قيمة افتراضية:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/api/users/{id}")
class UserController:
    async def get(self, id: int, fields: str = "") -> dict:
        return {"id": id, "fields": fields}
```

إجابات `id` غير رقمية `404`، ومعلمة طلب من النوع الخطأ `422`.

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

السجل وتعليقاته هي نموذج Pydantic، ويتم التحقق من صحته دائمًا، و `@UseResponse` يحدد الحالة:

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

## `@Service` والحقن المنشئ

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

`@Service` هو `@Injectable()`، والتعليق على `__init__` يخبر الحاوية بما يجب حقنه:

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

الفاصوليا هي مفردة بشكل افتراضي، كما هو الحال في الربيع. `@RequestScope` هو `@Injectable(scope=Scope.REQUEST)`، و `@Scope("prototype")` هو `Scope.TRANSIENT`. انظر [حقن التبعية](../routing/modular/dependency-injection.md).

## `@Configuration` الفصول والوحدات

تسرد الوحدة وحدات التحكم الخاصة بها والخدمات التي تستخدمها، وتقوم بتصدير ما يمكن للوحدات الأخرى إدخاله:

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

تستورد الوحدة الجذرية الوحدات الأخرى:

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

## `@RequestMapping` على الصف

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

التعيين المشترك هو `prefix` للوحدة، وكل مسار فرعي هو وحدة التحكم في تلك الوحدة:

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

الحارس هو وظيفة يتم رفعها عندما لا يستمر الطلب. `@UseGuard` يضعه على وحدة تحكم، أو على طريقة واحدة، مثل `@PreAuthorize`:

```python filename="src/apps/admin/guards.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
```

## المرشحات

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

المرشح لكل طلب هو فئة ASGI الوسيطة، المدرجة في `nexyconfig.py`:

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

`HandlerInterceptor` الذي يتم تشغيله فقط قبل أن يكون بعض وحدات التحكم حارسًا عليهم.

## `ResponseStatusException` و `@ControllerAdvice`

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

عميل API الذي يرسل `Accept: application/json` يحصل على `{"detail": "No such order"}` بالحالة التي قمت برفعها؛ يحصل المتصفح على صفحة HTML التي لم يتم العثور عليها.

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

تقوم وحدة التحكم بإرجاع طريقة عرض بالطريقة التي تُرجع بها `"users"`: يعرض `useViews` ملفًا `.nexy`، و `context` هو `Model`:

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

`th:text` يهرب و `{{ }}` لا: يهرب مما كتبه الزائر `| e`. يمكن للصفحة أيضًا أن تظل ملفًا لـ `src/routes/`، يتم تقديمه بجوار وحدات التحكم.

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

الكيان عبارة عن فئة SQLModel، والمستودع عبارة عن خدمة قابلة للحقن خلال الجلسة:

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

تصبح عمليات ترحيل مسار الطيران أو Liquibase `nx migrate -m "add posts"` و `nx migrate --upgrade`. انظر [قواعد البيانات](../guides/databases.md).

## `application.properties`

| التمهيد الربيع | نكسي |
|---|---|
| `server.port=8080` | `usePort = 8080` في `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` في `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`، مفعل افتراضيا |
| `src/main/resources/static/` | `public/`، خدم في `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## صحة المشغل

```properties filename="application.properties"
management.endpoints.web.exposure.include=health
```

الفحص الصحي هو وحدة تحكم مثل أي جهاز آخر، هنا `/admin/health` أعلاه. يتم إدخال عام في الوحدة الجذرية:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class PublicHealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

## `@Async` و `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

العمل الذي يتم تنفيذه بعد الإجابة هو مهمة خلفية، ويتم أخذها كمعلمة:

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

بالنسبة لوظائف `@Scheduled`، قم بتشغيل برنامج جدولة مثل APScheduler، أو مهمة cron، بجوار `nx start`.

## WebSockets

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

تفتح الطريقة `socket` WebSocket على مسار وحدة التحكم الخاصة بها:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def socket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

يتصل العملاء بـ `/ws/echo/`، باستخدام الشرطة المائلة اللاحقة.

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
| start.spring.io | `nx new`، مع جهاز التوجيه المعياري |
| `./mvnw spring-boot:run` مع أدوات التطوير | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`، ثم `nx start` |
| `./mvnw test` | `nx test` |

## الخطوات التالية

- [التوجيه المعياري](../routing/modular/README.md)
- [حقن التبعية](../routing/modular/dependency-injection.md)
- [الحراس والبيانات الوصفية](../routing/modular/guards-and-metadata.md)
- [من NestJS إلى Nexy](nestjs.md): نفس جهاز التوجيه، من TypeScript
