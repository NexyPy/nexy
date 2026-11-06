# Do Spring Boot ao Nexy

No Nexy, um método Spring `@RestController` se torna uma função em um arquivo em `src/routes/`, ou um método de uma classe `@Controller` no roteador modular: Bean Validation se torna Pydantic, e a página OpenAPI do springdoc é incorporada.

Cada seção abaixo mostra um hábito do Spring Boot e a mesma coisa no Nexy.

## Um controlador

```java filename="OláController.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

O caminho do arquivo é a URL, o nome da função é o método HTTP:

```python filename="src/rotas/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` e `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` é um segmento `[id]`; um parâmetro de solicitação é um parâmetro com um padrão:

```python filename="src/rotas/api/users/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

Um `id` não numérico responde `404`, um parâmetro de solicitação incorreto `422`.

## `@RequestBody`, `@Valid` e `ResponseEntity`

```java filename="NovoItem.java"
public record NewItem(@NotBlank @Size(max = 100) String name,
                      @Positive double price) {}
```

```java filename="ItemController.java"
@PostMapping("/api/items")
public ResponseEntity<NewItem> create(@Valid @RequestBody NewItem item) {
    return ResponseEntity.status(HttpStatus.CREATED).body(item);
}
```

O registro e suas anotações são um modelo Pydantic, sempre validado:

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `@RequestMapping` na aula

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

A pasta é o mapeamento:

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` e injeção de construtor

```java filename="SaudaçãoService.java"
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

Em um arquivo de rota, o serviço é uma dependência:

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

Para classes `@Service` injetadas através de construtores, com escopos singleton e de solicitação, use o [roteador modular](../routing/modular/dependency-injection.md): `@Injectable()` e `@Controller()` funcionam da maneira que `@Service` e `@RestController` funcionam.

## Segurança Primavera

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

`/admin/**` é a pasta `admin/` e seu `dependencies.py` é a regra:

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Filtros e `HandlerInterceptor`

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

## `ResponseStatusException` e `@ControllerAdvice`

```java filename="OrderController.java"
@GetMapping("/api/orders/{id}")
public Order order(@PathVariable long id) {
    return orders.findById(id)
        .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "No such order"));
}
```

```python filename="src/rotas/api/orders/[id].py"
from nexy.http import HTTPException

ORDERS = {1: {"id": 1, "total": 42}}


async def GET(id: int):
    if id not in ORDERS:
        raise HTTPException(status_code=404, detail="No such order")
    return ORDERS[id]
```

A resposta é `{"detail": "No such order"}`. Para um HTML `error/404.html`, coloque um `notfound.nexy` na raiz das rotas:

```nexy filename="src/rotas/notfound.nexy"
<h1>Not found</h1>
```

## Folha de tomilho

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

```html filename="modelos/usuários.html"
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

`th:text` escapa e `{{ }}` não: escapa o que um visitante digitou com `| e`.

## Entidades e repositórios JPA

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

Com SQLModel, um dos ORMs `nx new` pode criar:

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

As migrações Flyway ou Liquibase tornam-se `nx migrate -m "add posts"` e `nx migrate --upgrade`. Consulte [Bancos de dados](../guides/databases.md).

## `application.properties`

| Bota Primavera | Nexy |
|---|---|
| `server.port=8080` | `usePort = 8080` em `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` em `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, ativado por padrão |
| `src/main/resources/static/` | `public/`, servido em `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Saúde do atuador

```properties filename="aplicação.propriedades"
management.endpoints.web.exposure.include=health
```

Uma verificação de saúde é um caminho como qualquer outro:

```python filename="src/rotas/health.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` e `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

O trabalho executado após a resposta é uma tarefa em segundo plano:

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Para trabalhos `@Scheduled`, execute um agendador como APScheduler ou um cron job, próximo a `nx start`.

## WebSockets

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

```python filename="src/rotas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Testes com MockMvc

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

```python filename="testes/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## Correndo

| Bota Primavera | Nexy |
|---|---|
| start.spring.io | `nx new` |
| `./mvnw spring-boot:run` com DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, então `nx start` |
| `./mvnw test` | `nx test` |

## Próximas etapas

- [De NestJS a Nexy](nestjs.md): o roteador modular, classe por classe
- [Injeção de dependência](../routing/modular/dependency-injection.md)
- [Manipuladores de rota](../routing/fbr/handlers/README.md)
- [Bancos de dados](../guides/databases.md)
