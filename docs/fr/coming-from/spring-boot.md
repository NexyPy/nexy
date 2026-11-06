# De Spring Boot à Nexy

Dans Nexy, une méthode Spring `@RestController` devient une fonction dans un fichier sous `src/routes/`, ou une méthode d'une classe `@Controller` dans le routeur modulaire : Bean Validation devient Pydantic, et la page OpenAPI de Springdoc est intégrée.

Chaque section ci-dessous montre une habitude Spring Boot, puis la même chose dans Nexy.

## Un contrôleur

```java filename="BonjourController.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

Le chemin du fichier est l'URL, le nom de la fonction est la méthode HTTP :

```python filename="src/routes/api/hello.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` et `@RequestParam`

```java filename="UserController.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` est un segment `[id]` ; un paramètre de requête est un paramètre avec une valeur par défaut :

```python filename="src/routes/api/users/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

Un `id` non numérique répond à `404`, un mauvais paramètre de requête `422`.

## `@RequestBody`, `@Valid` et `ResponseEntity`

```java filename="NouvelArticle.java"
public record NewItem(@NotBlank @Size(max = 100) String name,
                      @Positive double price) {}
```

```java filename="ItemController.java"
@PostMapping("/api/items")
public ResponseEntity<NewItem> create(@Valid @RequestBody NewItem item) {
    return ResponseEntity.status(HttpStatus.CREATED).body(item);
}
```

La notice et ses annotations sont un modèle Pydantic, toujours validé :

```python filename="src/routes/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `@RequestMapping` sur la classe

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

Le dossier est le mappage :

```python filename="src/routes/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` et injection de constructeur

```java filename="SalutationService.java"
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

Dans un fichier de route, le service est une dépendance :

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

Pour les classes `@Service` injectées via des constructeurs, avec des étendues singleton et requête, utilisez le [routeur modulaire](../routing/modular/dependency-injection.md) : `@Injectable()` et `@Controller()` fonctionnent comme le font `@Service` et `@RestController`.

## Sécurité du printemps

```java filename="SécuritéConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

`/admin/**` est le dossier `admin/`, et son `dependencies.py` est la règle :

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Filtres et `HandlerInterceptor`

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

## `ResponseStatusException` et `@ControllerAdvice`

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

La réponse est `{"detail": "No such order"}`. Pour un HTML `error/404.html`, mettez un `notfound.nexy` à la racine des routes :

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

## Feuille de thym

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

```html filename="modèles/utilisateurs.html"
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

`th:text` s'échappe et `{{ }}` ne le fait pas : échappe à ce qu'un visiteur a tapé avec `| e`.

## Entités et référentiels JPA

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

Avec SQLModel, l'un des ORM `nx new` peut échafauder :

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

Les migrations Flyway ou Liquibase deviennent `nx migrate -m "add posts"` et `nx migrate --upgrade`. Voir [Bases de données](../guides/databases.md).

## `application.properties`

| Botte de printemps | Nexy |
|---|---|
| `server.port=8080` | `usePort = 8080` dans `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` dans `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, activé par défaut |
| `src/main/resources/static/` | `public/`, servi à `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Santé de l'actionneur

```properties filename="application.propriétés"
management.endpoints.web.exposure.include=health
```

Un bilan de santé est un parcours comme un autre :

```python filename="src/routes/health.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` et `@Scheduled`

```java filename="MailService.java"
@Async
public void sendWelcome(String email) { ... }
```

Le travail qui s'exécute après la réponse est une tâche en arrière-plan :

```python filename="src/routes/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Pour les tâches `@Scheduled`, exécutez un planificateur tel qu'APScheduler ou une tâche cron, à côté de `nx start`.

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

## Tests avec MockMvc

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

## Courir

| Botte de printemps | Nexy |
|---|---|
| start.spring.io | `nx new` |
| `./mvnw spring-boot:run` avec DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, puis `nx start` |
| `./mvnw test` | `nx test` |

## Prochaines étapes

- [De NestJS à Nexy](nestjs.md) : le routeur modulaire, classe par classe
- [Injection de dépendances](../routing/modular/dependency-injection.md)
- [Gestionnaires de routes](../routing/fbr/handlers/README.md)
- [Bases de données](../guides/databases.md)
