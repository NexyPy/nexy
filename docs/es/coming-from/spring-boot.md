# De Spring Boot a Nexy

El enrutador modular de Nexy mantiene la forma de una aplicación Spring Boot: un `@RestController` es una clase `@Controller`, un `@Service` es un `@Injectable` inyectado a través de `__init__` y un módulo los agrupa. Bean Validation se convierte en Pydantic y la página OpenAPI de springdoc está integrada.

Cada sección a continuación muestra un hábito de Spring Boot, luego lo mismo en Nexy.

## Encendido del enrutador modular

```java filename="Aplicación de demostración.java"
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) { SpringApplication.run(DemoApplication.class, args); }
}
```

El módulo raíz es un campo de `nexyconfig.py` y `nx dev` le sirve:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

Spring encuentra sus frijoles escaneando paquetes; un módulo Nexy los enumera, por lo que para qué sirve un módulo está escrito en un solo lugar.

## un controlador

```java filename="HolaController.java"
@RestController
@RequestMapping("/api/hello")
public class HelloController {
    @GetMapping
    public Map<String, String> hello() {
        return Map.of("message", "Hello");
    }
}
```

La ruta es el primer argumento de `@Controller` y el nombre del método es el verbo HTTP:

```python filename="src/apps/hola/hola_controller.py"
from nexy.decorators import Controller


@Controller("/api/hello")
class HelloController:
    async def get(self) -> dict:
        return {"message": "Hello"}
```

Un controlador tiene un controlador por verbo, por lo que `@GetMapping` y `@PostMapping` en una ruta son los métodos `get` y `post` de una clase. `GET /items` y `GET /items/{id}` son ​​dos controladores.

## `@PathVariable` y `@RequestParam`

```java filename="Controlador de usuario.java"
@GetMapping("/api/users/{id}")
public Map<String, Object> user(@PathVariable long id,
                                @RequestParam(defaultValue = "") String fields) {
    return Map.of("id", id, "fields", fields);
}
```

`{id}` permanece en la ruta y se convierte en un parámetro escrito; un parámetro de solicitud es un parámetro con un valor predeterminado:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/api/users/{id}")
class UserController:
    async def get(self, id: int, fields: str = "") -> dict:
        return {"id": id, "fields": fields}
```

Un `id` no numérico responde `404` y un parámetro de solicitud del tipo incorrecto `422`.

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

El registro y sus anotaciones son un modelo Pydantic, siempre validado, y `@UseResponse` establece el estado:

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

## `@Service` e inyección de constructor

```java filename="SaludoService.java"
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

`@Service` es `@Injectable()`, y la anotación de `__init__` le dice al contenedor qué inyectar:

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

Un bean es un singleton por defecto, como en Spring. `@RequestScope` es `@Injectable(scope=Scope.REQUEST)` y `@Scope("prototype")` es `Scope.TRANSIENT`. Consulte [Inyección de dependencia](../routing/modular/dependency-injection.md).

## `@Configuration` clases y módulos

Un módulo enumera sus controladores y los servicios que utilizan, y exporta lo que otros módulos pueden inyectar:

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

El módulo raíz importa los demás:

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

## `@RequestMapping` en la clase

```java filename="AdministradorController.java"
@RestController
@RequestMapping("/admin")
public class AdminController {
    @GetMapping("/stats")
    public Map<String, Integer> stats() { return Map.of("users", 3); }

    @GetMapping("/health")
    public Map<String, String> health() { return Map.of("status", "UP"); }
}
```

Un mapeo compartido es el `prefix` de un módulo, y cada subruta es un controlador de ese módulo:

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

Una guardia es una función que se activa cuando la solicitud no puede continuar. `@UseGuard` lo coloca en un controlador, o en un método, como `@PreAuthorize`:

```python filename="src/apps/admin/guards.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header("")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
```

## Filtros

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

Un filtro para cada solicitud es una clase de middleware ASGI, que se enumera en `nexyconfig.py`:

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

Un `HandlerInterceptor` que solo se ejecuta antes de algunos controladores es un guardia para ellos.

## `ResponseStatusException` y `@ControllerAdvice`

```java filename="Controlador de pedidos.java"
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

Un cliente API que envía `Accept: application/json` obtiene `{"detail": "No such order"}` con el estado que usted planteó; un navegador obtiene la página HTML no encontrada.

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

Un controlador devuelve una vista de la misma manera que devuelve `"users"`: `useViews` representa un archivo `.nexy`, y su `context` es el `Model`:

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

`th:text` escapa y `{{ }}` no: escapa de lo que un visitante escribió con `| e`. Una página también puede contener un archivo de `src/routes/`, servido junto a los controladores.

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

La entidad es una clase SQLModel y el repositorio es un servicio inyectable alrededor de una sesión:

```python filename="src/modelos/post_model.py"
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

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    usePort = 8080
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

## Salud del actuador

```properties filename="propiedades.de.aplicación"
management.endpoints.web.exposure.include=health
```

Un chequeo de salud es un controlador como cualquier otro, aquí el `/admin/health` de arriba. Uno público va en el módulo raíz:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class PublicHealthController:
    async def get(self) -> dict:
        return {"status": "UP"}
```

## `@Async` y `@Scheduled`

```java filename="Servicio de correo.java"
@Async
public void sendWelcome(String email) { ... }
```

El trabajo que se ejecuta después de la respuesta es una tarea en segundo plano, tomada como parámetro:

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

Para trabajos `@Scheduled`, ejecute un programador como APScheduler, o un trabajo cron, junto a `nx start`.

## WebSockets

```java filename="EchoHandler.java"
public class EchoHandler extends TextWebSocketHandler {
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        session.sendMessage(message);
    }
}
```

Un método `socket` abre un WebSocket en la ruta de su controlador:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def socket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Los clientes se conectan a `/ws/echo/`, con la barra diagonal final.

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
| inicio.primavera.io | `nx new`, con el enrutador modular |
| `./mvnw spring-boot:run` con DevTools | `nx dev` |
| `./mvnw package && java -jar app.jar` | `nx build`, luego `nx start` |
| `./mvnw test` | `nx test` |

## Próximos pasos

- [Enrutamiento modular](../routing/modular/README.md)
- [Inyección de dependencia](../routing/modular/dependency-injection.md)
- [Guardias y metadatos](../routing/modular/guards-and-metadata.md)
- [De NestJS a Nexy](nestjs.md): el mismo enrutador, de TypeScript
