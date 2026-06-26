def build_sections(s, mode="fbr"):
    getting_started = [
        {"label": s.getting_started.introduction, "href": "/"},
        {"label": s.getting_started.quick_start, "href": "/create_a_projet"},
        {"label": s.getting_started.fbr_or_modular, "href": "/router-choice"},
        {"label": s.getting_started.project_structure, "href": "/projet_structure"},
        {"label": s.getting_started.build_deploy, "href": "/build_and_deploy"},
    ]

    composable_views = [
        {"label": s.views.introduction, "href": "/components"},
        {"label": s.views.usage, "href": "/components/usage"},
        {"label": s.views.markup, "href": "/components/markup"},
        {"label": s.views.python, "href": "/components/python"},
        {"label": s.views.properties, "href": "/components/properties"},
        {"label": s.views.conditional, "href": "/components/conditional"},
        {"label": s.views.modules, "href": "/components/modules"},
        {"label": s.views.styles, "href": "/components/styles"},
    ]

    fbr_router_items = [
        {"label": s.fbr_router.introduction, "href": "/fbrouters"},
        {"label": s.fbr_router.pages, "href": "/fbrouters/pages"},
        {"label": s.fbr_router.layouts, "href": "/fbrouters/layouts"},
        {"label": s.fbr_router.rest_routes, "href": "/fbrouters/route_handlers"},
        {"label": s.fbr_router.request_body, "href": "/fbrouters/request-body"},
        {"label": s.fbr_router.cookies_headers, "href": "/fbrouters/cookie-header"},
        {"label": s.fbr_router.response_model, "href": "/fbrouters/response-model"},
        {"label": s.fbr_router.background_tasks, "href": "/fbrouters/background-tasks"},
        {"label": s.fbr_router.async_, "href": "/fbrouters/async"},
        {"label": s.fbr_router.sse, "href": "/fbrouters/sse"},
        {"label": s.fbr_router.websocket, "href": "/fbrouters/websocket"},
        {"label": s.fbr_router.redirects, "href": "/fbrouters/redirects"},
        {"label": s.fbr_router.authorization, "href": "/fbrouters/authorization"},
        {"label": s.fbr_router.useguard, "href": "/fbrouters/useguard"},
        {"label": s.fbr_router.middleware_decorator, "href": "/fbrouters/middleware"},
        {"label": s.fbr_router.error_handling, "href": "/guides/error-handling"},
        {"label": s.fbr_router.static_files, "href": "/guides/static-files"},
        {"label": s.fbr_router.dependencies, "href": "/fbrouters/dependencies"},
        {"label": s.fbr_router.middlewares, "href": "/fbrouters/middlewares"},
        {"label": s.fbr_router.dynamic_urls, "href": "/fbrouters/route_parameters"},
        {"label": s.fbr_router.query_params, "href": "/fbrouters/query_parameters"},
    ]

    modular_router_items = [
        {"label": s.modular_router.introduction, "href": "/modular/overview"},
        {"label": s.modular_router.controllers, "href": "/modular/controllers"},
        {"label": s.modular_router.providers_di, "href": "/modular/providers"},
        {"label": s.modular_router.modules, "href": "/modular/modules"},
        {"label": s.modular_router.guards, "href": "/modular/guards"},
        {"label": s.modular_router.middleware, "href": "/modular/middleware"},
        {"label": s.modular_router.request_body, "href": "/modular/request-body"},
        {"label": s.modular_router.cookies_headers, "href": "/modular/cookie-header"},
        {"label": s.modular_router.response, "href": "/modular/response-model"},
        {"label": s.modular_router.background_tasks, "href": "/modular/background-tasks"},
        {"label": s.modular_router.async_, "href": "/modular/async"},
        {"label": s.modular_router.sse, "href": "/modular/sse"},
        {"label": s.modular_router.websocket, "href": "/modular/websocket"},
        {"label": s.modular_router.redirects, "href": "/modular/redirects"},
        {"label": s.modular_router.authorization, "href": "/modular/authorization"},
        {"label": s.modular_router.error_handling, "href": "/guides/error-handling"},
        {"label": s.modular_router.static_files, "href": "/guides/static-files"},
    ]

    fbr_decorators = [
        {"label": s.decorators.introduction, "href": "/decorators"},
        {"label": s.decorators.action, "href": "/decorators/action"},
        {"label": s.decorators.useguard, "href": "/decorators/useguard"},
        {"label": s.decorators.middleware, "href": "/decorators/middleware"},
    ]

    modular_decorators = [
        {"label": s.decorators.introduction, "href": "/decorators"},
        {"label": s.decorators.action, "href": "/decorators/action"},
        {"label": s.decorators.controller, "href": "/decorators/controller"},
        {"label": s.decorators.module, "href": "/decorators/module"},
        {"label": s.decorators.injectable, "href": "/decorators/injectable"},
        {"label": s.decorators.useguard, "href": "/decorators/useguard"},
        {"label": s.decorators.middleware, "href": "/decorators/middleware"},
        {"label": s.decorators.useroute, "href": "/decorators/useroute"},
        {"label": s.decorators.useresponse, "href": "/decorators/useresponse"},
    ]

    components_items = [
        {"label": s.components.audio, "href": "#", "badge": s.components.badge_soon},
        {"label": s.components.video, "href": "#", "badge": s.components.badge_soon},
        {"label": s.components.form, "href": "#", "badge": s.components.badge_soon},
        {"label": s.components.image, "href": "#", "badge": s.components.badge_soon},
        {"label": s.components.link, "href": "#", "badge": s.components.badge_soon},
        {"label": s.components.script, "href": "#", "badge": s.components.badge_soon},
        {"label": s.components.vite, "href": "/frontend/vite"},
    ]

    config_items = [
        {"label": s.config.introduction, "href": "/config"},
        {"label": s.config.nexy, "href": "/config/nexy"},
        {"label": s.config.vite, "href": "/config/vite"},
        {"label": s.config.cors, "href": "/config/cors"},
        {"label": s.config.aliases, "href": "/config/aliases"},
        {"label": s.config.session, "href": "/config/session"},
        {"label": s.config.i18n, "href": "/config/i18n"},
        {"label": s.config.toc, "href": "/config/toc"},
    ]

    cli_items = [
        {"label": s.cli.introduction, "href": "/cli"},
        {"label": s.cli.dev, "href": "/cli/dev"},
        {"label": s.cli.start, "href": "/cli/start"},
        {"label": s.cli.build, "href": "/cli/build"},
        {"label": s.cli.new, "href": "/cli/new"},
        {"label": s.cli.init, "href": "/cli/init"},
        {"label": s.cli.migrate_cmd, "href": "/cli/migrate"},
    ]

    hooks_items = [
        {"label": s.hooks.introduction, "href": "/hooks"},
        {"label": s.hooks.pathname, "href": "/hooks/usePathname"},
        {"label": s.hooks.searchparams, "href": "/hooks/useSearchParams"},
        {"label": s.hooks.router, "href": "/hooks/useRouter"},
        {"label": s.hooks.query, "href": "/hooks/useQuery"},
        {"label": s.hooks.session, "href": "/hooks/useSession"},
        {"label": s.hooks.cookies, "href": "/hooks/useCookies"},
        {"label": s.hooks.toc, "href": "/hooks/useToc"},
        {"label": s.hooks.views, "href": "/hooks/useViews"},
    ]

    security_items = [
        {"label": s.security.introduction, "href": "/security"},
        {"label": s.security.authentication, "href": "/security/authentication"},
        {"label": s.security.authorization, "href": "/security/authorization"},
        {"label": s.security.encryption, "href": "/security/encryption-hashing"},
        {"label": s.security.jwt, "href": "/security/jwt"},
        {"label": s.security.uid, "href": "/security/uid"},
    ]

    databases_items = [
        {"label": s.databases.introduction, "href": "/orm/database"},
        {"label": s.databases.postgresql, "href": "/orm/postgresql"},
        {"label": s.databases.mysql, "href": "/orm/mysql"},
        {"label": s.databases.sqlite, "href": "/orm/sqlite"},
        {"label": s.databases.sqlmodel, "href": "/orm/sqlmodel"},
        {"label": s.databases.sqlalchemy, "href": "/orm/sqlalchemy"},
        {"label": s.databases.tortoise, "href": "/orm/tortoise"},
    ]

    guides_items = [
        {"label": s.guides.introduction, "href": "/guides"},
        {"label": s.guides.react, "href": "/frontend/react"},
        {"label": s.guides.vue, "href": "/frontend/vue"},
        {"label": s.guides.svelte, "href": "/frontend/svelte"},
        {"label": s.guides.solid, "href": "/frontend/solid"},
        {"label": s.guides.preact, "href": "/frontend/preact"},
        {"label": s.guides.vite_ssr, "href": "/frontend/vite"},
        {"label": s.guides.jinja2, "href": "/guides/jinja2"},
        {"label": s.guides.data_loading, "href": "/guides/data-loading"},
        {"label": s.guides.error_handling, "href": "/guides/error-handling"},
        {"label": s.guides.actions, "href": "/guides/actions"},
        {"label": s.guides.auth, "href": "/guides/auth"},
        {"label": s.guides.i18n, "href": "/guides/i18n"},
        {"label": s.guides.css_js, "href": "/guides/css-js"},
        {"label": s.guides.realtime, "href": "/guides/websocket"},
        {"label": s.guides.deploy, "href": "/guides/deploy"},
    ]

    migrate_items = [
        {"label": s.migrate.introduction, "href": "/migrate"},
        {"label": s.migrate.fastapi, "href": "/migrate/fastapi"},
        {"label": s.migrate.django, "href": "/migrate/django"},
        {"label": s.migrate.nestjs, "href": "/migrate/nestjs"},
        {"label": s.migrate.flask, "href": "/migrate/flask"},
        {"label": s.migrate.nextjs, "href": "/migrate/nextjs"},
    ]

    fastapi_items = [
        {"label": s.fastapi.introduction, "href": "/fastapi"},
        {"label": s.fastapi.forms_files, "href": "/fastapi/forms-files"},
        {"label": s.fastapi.testing, "href": "/fastapi/testing"},
        {"label": s.fastapi.debugging, "href": "/fastapi/debugging"},
        {"label": s.fastapi.lifespan, "href": "/fastapi/lifespan-events"},
        {"label": s.fastapi.env_settings, "href": "/fastapi/env-settings"},
        {"label": s.fastapi.custom_docs, "href": "/fastapi/custom-docs"},
        {"label": s.fastapi.graphql, "href": "/fastapi/graphql"},
        {"label": s.fastapi.wsgi, "href": "/fastapi/wsgi"},
        {"label": s.fastapi.proxy, "href": "/fastapi/proxy"},
        {"label": s.fastapi.sub_apps, "href": "/fastapi/sub-apps"},
        {"label": s.fastapi.openapi_webhooks, "href": "/fastapi/openapi-webhooks"},
        {"label": s.fastapi.generate_clients, "href": "/fastapi/generate-clients"},
    ]

    getting_started_section = {"title": s.getting_started.title, "href": "", "items": getting_started, "collapsible": False}
    views_section = {"title": s.views.title, "href": "", "items": composable_views}
    fbr_router_section = {"title": s.fbr_router.title, "href": "", "items": fbr_router_items}
    modular_router_section = {"title": s.modular_router.title, "href": "", "items": modular_router_items}
    fbr_decorators_section = {"title": s.decorators.title, "href": "", "items": fbr_decorators}
    modular_decorators_section = {"title": s.decorators.title, "href": "", "items": modular_decorators}
    components_section = {"title": s.components.title, "href": "", "items": components_items}
    config_section = {"title": s.config.title, "href": "", "items": config_items}
    cli_section = {"title": s.cli.title, "href": "", "items": cli_items}
    hooks_section = {"title": s.hooks.title, "href": "", "items": hooks_items}
    security_section = {"title": s.security.title, "href": "", "items": security_items}
    databases_section = {"title": s.databases.title, "href": "", "items": databases_items}
    guides_section = {"title": s.guides.title, "href": "", "items": guides_items}
    migrate_section = {"title": s.migrate.title, "href": "", "items": migrate_items}
    fastapi_section = {"title": s.fastapi.title, "href": "", "items": fastapi_items}

    if mode == "fbr":
        return [
            getting_started_section,
            fbr_router_section,
            views_section,
            components_section,
            config_section,
            cli_section,
            hooks_section,
            fbr_decorators_section,
            security_section,
            databases_section,
            migrate_section,
            guides_section,
            fastapi_section,
        ]
    return [
        getting_started_section,
        modular_router_section,
        views_section,
        components_section,
        config_section,
        cli_section,
        hooks_section,
        modular_decorators_section,
        security_section,
        databases_section,
        migrate_section,
        guides_section,
        fastapi_section,
    ]
