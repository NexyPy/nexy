# De Spring Boot a Nexy

En Nexy, un método Spring `@RestController` se convierte en una función en un archivo en `src/routes/`, o un método de una clase `@Controller` en el enrutador modular: Bean Validation se convierte en Pydantic, y la página Springdoc OpenAPI está integrada.

Cada sección a continuación muestra un hábito de Spring Boot, luego lo mismo en Nexy.

## un controlador

```java filename="HolaController.java"
@RestController
public class HelloController {
    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

La ruta del archivo es la URL, el nombre de la función es el método HTTP:

```python filename="src/rutas/api/hola.py"
async def GET():
    return {"message": "Hello"}
```

## `@PathVariable` y `@RequestParam`

```java filename="Controlador de usuario.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` es un segmento `[id]`; un parámetro de solicitud es un parámetro con un valor predeterminado:

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int, fields: str = ""):
    return {"id": id, "fields": fields}
```

Un `id` no numérico responde `404`, un parámetro de solicitud incorrecto `422`.

## `@RequestBody`, `@Valid` y `ResponseEntity`

```java filename="Nuevo elemento.java"
public record NewItem(@NotBlank @Size(max = 100) String name,
                      @Positive double price) {}
```

```java filename="ItemController.java"
@PostMapping("/api/items")
public ResponseEntity<NewItem> create(@Valid @RequestBody NewItem item) {
    return ResponseEntity.status(HttpStatus.CREATED).body(item);
}
```

El registro y sus anotaciones son un modelo Pydantic, siempre validado:

```python filename="src/rutas/api/items.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `@RequestMapping` en la clase

```java filename="AdministradorController.java"
@RestController
@RequestMapping("/admin")
public class AdminController {
    @GetMapping("/stats")
    public Map<String, Integer> stats() {
        return Map.of("users", 3);
    }
}
```

La carpeta es el mapeo:

```python filename="src/rutas/admin/stats.py"
async def GET():
    return {"users": 3}
```

## `@Service` e inyección de constructor

```java filename="SaludoService.java"
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

En un archivo de ruta, el servicio es una dependencia:

```python filename="src/servicios/saludo.py"
class GreetingService:
    def greet(self, name: str) -> str:
        return f"Hello {name}"


def get_greetings() -> GreetingService:
    return GreetingService()
```

```python filename="src/rutas/api/greet.py"
from nexy.http import Depends

from src.services.greeting import GreetingService, get_greetings


async def GET(name: str, greetings: GreetingService = Depends(get_greetings)):
    return {"message": greetings.greet(name)}
```

Para las clases `@Service` inyectadas a través de constructores, con alcances singleton y de solicitud, use el [enrutador modular](../routing/modular/dependency-injection.md): `@Injectable()` y `@Controller()` funcionan de la misma manera que lo hacen `@Service` y `@RestController`.

## Seguridad de primavera

```java filename="SecurityConfig.java"
@Bean
SecurityFilterChain filters(HttpSecurity http) throws Exception {
    return http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().permitAll())
        .build();
}
```

`/admin/**` es la carpeta `admin/` y su `dependencies.py` es la regla:

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

## Filtros y `HandlerInterceptor`

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

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## `ResponseStatusException` y `@ControllerAdvice`

```java filename="Controlador de pedidos.java"
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

La respuesta es `{"detail": "No such order"}`. Para un HTML `error/404.html`, coloque un `notfound.nexy` en la raíz de la ruta:

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
```

## hoja de tomillo

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

```html filename="plantillas/usuarios.html"
<ul>
  <li th:each="user : ${users}" th:text="${user.name}"></li>
</ul>
```

```nexy filename="src/rutas/usuarios.nexy"
---
users = [{"name": "Ada"}, {"name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

`th:text` escapa y `{{ }}` no: escapa de lo que un visitante escribió con `| e`.

## Entidades y repositorios JPA

```java filename="Publicar.java"
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

Con SQLModel, uno de los ORM `nx new` puede implementar:

```python filename="src/modelos/post_model.py"
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    published: bool = False
```

```python filename="src/rutas/api/posts/published.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


async def GET():
    with Session(engine) as session:
        posts = session.exec(select(Post).where(Post.published)).all()
    return {"titles": [post.title for post in posts]}
```

Las migraciones Flyway o Liquibase se convierten en `nx migrate -m "add posts"` y `nx migrate --upgrade`. Consulte [Bases de datos](../guides/databases.md).

## `application.properties`

| Bota de primavera | nexy |
|---|---|
| `server.port=8080` | `usePort = 8080` en `nexyconfig.py` |
| `spring.datasource.url` | `DATABASE_URL` en `.env` |
| `@CrossOrigin` / `CorsConfigurationSource` | `useCORS = {"allow_origins": [...]}` |
| `server.compression.enabled=true` | `useGZip = {"minimum_size": 1000}` |
| `springdoc.swagger-ui.path=/docs` | `useDocsUrl = "/docs"`, activado de forma predeterminada |
| `src/main/resources/static/` | `public/`, servido en `/` |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Salud del actuador

```properties filename="propiedades.de.aplicación"
management.endpoints.web.exposure.include=health
```

Un control de salud es una ruta como cualquier otra:

```python filename="src/rutas/salud.py"
async def GET():
    return {"status": "UP"}
```

## `@Async` y `@Scheduled`

```java filename="Servicio de correo.java"
@Async
public void sendWelcome(String email) { ... }
```

El trabajo que se ejecuta después de la respuesta es una tarea en segundo plano:

```python filename="src/rutas/api/signup.py"
from nexy.http import BackgroundTasks, JSONResponse


def send_welcome(email: str) -> None: ...


async def POST(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_welcome, email)
    return JSONResponse({"queued": True}, status_code=202)
```

Para trabajos de `@Scheduled`, ejecute un programador como APScheduler, o un trabajo cron, junto a `nx start`.

## WebSockets

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

```python filename="src/rutas/ws/echo.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())
```

## Pruebas con MockMvc

```java filename="HolaControllerTest.java"
@WebMvcTest(HelloController.class)
class HelloControllerTest {
    @Autowired MockMvc mvc;

    @Test
    void hello() throws Exception {
        mvc.perform(get("/api/hello")).andExpect(jsonPath("$.message").value("Hello"));
    }
}
```

```python filename="pruebas/test_hello.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_hello():
    assert TestClient(app).get("/api/hello").json() == {"message": "Hello"}
```

## corriendo

| Bota de primavera | nexy |
|---|---|
| inicio.primavera.io | `nx new` |
| `./mvnw spring-boot:run` con DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, luego `nx start` |
| `./mvnw test` | `nx test` |

## Próximos pasos

- [De NestJS a Nexy](nestjs.md): el router modular, clase por clase
- [Inyección de dependencia](../routing/modular/dependency-injection.md)
- [Controladores de ruta](../routing/fbr/handlers/README.md)
- [Bases de datos](../guides/databases.md)
