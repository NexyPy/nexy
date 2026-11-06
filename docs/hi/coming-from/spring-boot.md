# स्प्रिंग बूट से नेक्सी तक

नेक्सी का मॉड्यूलर राउटर स्प्रिंग बूट ऐप का आकार रखता है: एक `@RestController` एक `@Controller` वर्ग है, एक `@Service` एक `@Injectable` है जिसे `__init__` के माध्यम से इंजेक्ट किया जाता है, और एक मॉड्यूल उन्हें समूहित करता है। बीन वैलिडेशन Pydantic बन जाता है, और स्प्रिंगडॉक का OpenAPI पेज बनाया जाता है।

नीचे प्रत्येक अनुभाग स्प्रिंग बूट आदत दिखाता है, फिर नेक्सी में भी यही चीज़।

## मॉड्यूलर राउटर चालू करना

```java filename="डेमोएप्लिकेशन.जावा"
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) { SpringApplication.run(DemoApplication.class, args); }
}
```

रूट मॉड्यूल `nexyconfig.py` का एक क्षेत्र है, और `nx dev` इसकी सेवा करता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

स्प्रिंग पैकेजों को स्कैन करके अपनी फलियाँ ढूंढता है; एक नेक्सी मॉड्यूल उन्हें सूचीबद्ध करता है, इसलिए एक मॉड्यूल जो कार्य करता है वह एक ही स्थान पर लिखा होता है।

## एक नियंत्रक

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

पथ `@Controller` का पहला तर्क है, और विधि का नाम HTTP क्रिया है:

```python filename="src/apps/hello/hello_controller.py"
from nexy.decorators import Controller


@Controller("/api/hello")
class HelloController:
    async def get(self) -> dict:
        return {"message": "Hello"}
```

एक नियंत्रक के पास प्रति क्रिया एक हैंडलर होता है, इसलिए `@GetMapping` और `@PostMapping` एक पथ पर एक वर्ग के `get` और `post` तरीके हैं। `GET /items` और `GET /items/{id}` दो नियंत्रक हैं।

## `@PathVariable` और `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` पथ में रहता है और एक टाइप किया हुआ पैरामीटर बन जाता है; अनुरोध पैरामीटर एक डिफ़ॉल्ट पैरामीटर है:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/api/users/{id}")
class UserController:
    async def get(self, id: int, fields: str = "") -> dict:
        return {"id": id, "fields": fields}
```

एक गैर-संख्यात्मक `id` उत्तर `404`, और गलत प्रकार का एक अनुरोध पैरामीटर `422`।

## `@RequestBody`, `@Valid` और `ResponseEntity`

```java filename="NewItem.java"
public record NewItem(@NotBlank @Size(max = 100) String name,
                      @Positive double price) {}
```

```java filename="आइटमकंट्रोलर.जावा"
@PostMapping("/api/items")
public ResponseEntity<NewItem> create(@Valid @RequestBody NewItem item) {
    return ResponseEntity.status(HttpStatus.CREATED).body(item);
}
```

रिकॉर्ड और उसके एनोटेशन एक Pydantic मॉडल हैं, जो हमेशा मान्य होते हैं, और `@UseResponse` स्थिति निर्धारित करते हैं:

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

## `@Service` और कंस्ट्रक्टर इंजेक्शन

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

`@Service` है `@Injectable()`, और `__init__` का एनोटेशन कंटेनर को बताता है कि क्या इंजेक्ट करना है:

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

एक बीन डिफ़ॉल्ट रूप से एक सिंगलटन है, जैसे कि स्प्रिंग में। `@RequestScope` है `@Injectable(scope=Scope.REQUEST)`, और `@Scope("prototype")` है `Scope.TRANSIENT`। [निर्भरता इंजेक्शन](../routing/modular/dependency-injection.md) देखें।

## `@Configuration` कक्षाएं और मॉड्यूल

एक मॉड्यूल अपने नियंत्रकों और उनके द्वारा उपयोग की जाने वाली सेवाओं को सूचीबद्ध करता है, और निर्यात करता है कि अन्य मॉड्यूल क्या इंजेक्ट कर सकते हैं:

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

रूट मॉड्यूल दूसरों को आयात करता है:

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

## `@RequestMapping` कक्षा में

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

एक साझा मैपिंग एक मॉड्यूल का `prefix` है, और प्रत्येक उप-पथ उस मॉड्यूल का नियंत्रक है:

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

## स्प्रिंग सुरक्षा

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

गार्ड एक ऐसा फ़ंक्शन है जो तब उठता है जब अनुरोध जारी नहीं हो पाता। `@UseGuard` इसे नियंत्रक पर, या एक विधि पर रखता है, जैसे `@PreAuthorize`:

```python filename="src/apps/admin/guards.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
```

## फिल्टर

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

प्रत्येक अनुरोध के लिए एक फ़िल्टर एक ASGI मिडलवेयर क्लास है, जो `nexyconfig.py` में सूचीबद्ध है:

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

एक `HandlerInterceptor` जो केवल कुछ नियंत्रकों के सामने चलता है उन पर एक गार्ड है।

## `ResponseStatusException` और `@ControllerAdvice`

```java filename="ऑर्डरकंट्रोलर.जावा"
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

एक एपीआई क्लाइंट जो `Accept: application/json` भेजता है उसे आपके द्वारा बढ़ाए गए स्टेटस के साथ `{"detail": "No such order"}` मिलता है; ब्राउज़र को HTML नॉट-फाउंड पेज मिलता है।

## थाइमेलिफ़

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

एक नियंत्रक एक दृश्य को उसी तरह लौटाता है जैसे वह लौटाता है `"users"`: `useViews` एक `.nexy` फ़ाइल को प्रस्तुत करता है, और इसका `context` `Model` है:

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

`th:text` बच जाता है और `{{ }}` नहीं बचता: विज़िटर ने `| e` के साथ जो टाइप किया है वह बच जाता है। एक पेज में नियंत्रकों के बगल में `src/routes/` की फ़ाइल भी रखी जा सकती है।

## जेपीए इकाइयां और रिपॉजिटरी

```java filename="पोस्ट.जावा"
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

इकाई एक SQLModel वर्ग है, और भंडार एक सत्र के आसपास एक इंजेक्टेबल सेवा है:

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

फ्लाईवे या लिक्विबेस माइग्रेशन `nx migrate -m "add posts"` और `nx migrate --upgrade` बन जाते हैं। [डेटाबेस](../guides/databases.md) देखें।

## `application.properties`

| स्प्रिंग बूट | नेक्सी |
|---|---|
| `server.port=8080` | `usePort = 8080` में `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` में `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, डिफ़ॉल्ट रूप से चालू |
| `src/main/resources/static/` | `public/`, `/` में सेवा दी गई |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## एक्चुएटर स्वास्थ्य

```properties filename="अनुप्रयोग.गुण"
management.endpoints.web.exposure.include=health
```

स्वास्थ्य जांच किसी भी अन्य की तरह एक नियंत्रक है, यहां `/admin/health` ऊपर वाला है। एक सार्वजनिक रूट मॉड्यूल में जाता है:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class PublicHealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

## `@Async` और `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

उत्तर के बाद चलने वाला कार्य एक पृष्ठभूमि कार्य है, जिसे एक पैरामीटर के रूप में लिया जाता है:

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

`@Scheduled` नौकरियों के लिए, `nx start` के बगल में एक शेड्यूलर जैसे एपीएस शेड्यूलर, या क्रॉन जॉब चलाएँ।

## वेबसॉकेट

```java filename="इकोहैंडलर.जावा"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

एक `socket` विधि अपने नियंत्रक के पथ पर एक WebSocket खोलती है:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def socket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

ग्राहक अनुगामी स्लैश के साथ `/ws/echo/` से जुड़ते हैं।

## MockMvc के साथ परीक्षण

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

```python filename="परीक्षण/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## चल रहा है

| स्प्रिंग बूट | नेक्सी |
|---|---|
| प्रारंभ.वसंत.io | `nx new`, मॉड्यूलर राउटर के साथ |
| `./mvnw spring-boot:run` DevTools के साथ | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, फिर `nx start` |
| `./mvnw test` | `nx test` |

## अगले चरण

- [मॉड्यूलर रूटिंग](../routing/modular/README.md)
- [निर्भरता इंजेक्शन](../routing/modular/dependency-injection.md)
- [गार्ड और मेटाडेटा](../routing/modular/guards-and-metadata.md)
- [से NestJS से नेक्सी](nestjs.md): वही राउटर, TypeScript से
