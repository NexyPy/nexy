# स्प्रिंग बूट से नेक्सी तक

नेक्सी में एक स्प्रिंग `@RestController` विधि `src/routes/` के तहत फ़ाइल में एक फ़ंक्शन बन जाती है, या मॉड्यूलर राउटर में `@Controller` क्लास की एक विधि बन जाती है: बीन वैलिडेशन Pydantic बन जाता है, और स्प्रिंगडॉक का OpenAPI पेज बनाया जाता है।

नीचे प्रत्येक अनुभाग स्प्रिंग बूट आदत दिखाता है, फिर नेक्सी में भी यही चीज़।

## एक नियंत्रक

```java filename="HelloController.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

फ़ाइल पथ URL है, फ़ंक्शन नाम HTTP विधि है:

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` और `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` एक `[id]` खंड है; अनुरोध पैरामीटर एक डिफ़ॉल्ट पैरामीटर है:

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

एक गैर-संख्यात्मक `id` उत्तर देता है `404`, एक ख़राब अनुरोध पैरामीटर `422`।

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

रिकॉर्ड और उसके एनोटेशन एक Pydantic मॉडल हैं, जो हमेशा मान्य होते हैं:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `@RequestMapping` कक्षा में

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

फ़ोल्डर मैपिंग है:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` और कंस्ट्रक्टर इंजेक्शन

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

रूट फ़ाइल में, सेवा एक निर्भरता है:

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

`@Service` सिंगलटन और अनुरोध स्कोप के साथ कंस्ट्रक्टर के माध्यम से इंजेक्ट की गई कक्षाओं के लिए, [मॉड्यूलर राउटर ](../routing/modular/dependency-injection.md) का उपयोग करें: `@Injectable()` और `@Controller()` उसी तरह काम करते हैं जैसे `@Service` और `@RestController` करते हैं।

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

`/admin/**` `admin/` फ़ोल्डर है, और इसका `dependencies.py` नियम है:

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## फ़िल्टर और `HandlerInterceptor`

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

## `ResponseStatusException` और `@ControllerAdvice`

```java filename="ऑर्डरकंट्रोलर.जावा"
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

उत्तर है `{"detail": "No such order"}`. HTML `error/404.html` के लिए, रूट रूट पर `notfound.nexy` लगाएं:

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

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

`th:text` बच जाता है और `{{ }}` नहीं बचता: विज़िटर ने `| e` के साथ जो टाइप किया है वह बच जाता है।

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

SQLModel के साथ, ओआरएम में से एक `nx new` मचान बना सकता है:

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


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## एक्चुएटर स्वास्थ्य

```properties filename="अनुप्रयोग.गुण"
management.endpoints.web.exposure.include=health
```

स्वास्थ्य जांच किसी भी अन्य की तरह एक मार्ग है:

```python filename="src/routes/health.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` और `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

उत्तर के बाद चलने वाला कार्य एक पृष्ठभूमि कार्य है:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
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

```python filename="src/routes/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

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
| प्रारंभ.वसंत.io | `nx new` |
| `./mvnw spring-boot:run` DevTools के साथ | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, फिर `nx start` |
| `./mvnw test` | `nx test` |

## अगले चरण

- [से NestJS से नेक्सी](nestjs.md): मॉड्यूलर राउटर, वर्ग दर वर्ग
- [निर्भरता इंजेक्शन](../routing/modular/dependency-injection.md)
- [मार्ग संचालक](../routing/fbr/handlers/README.md)
- [डेटाबेस](../guides/databases.md)
