> Draft kept out of `docs/` on 2026-11-01. It replaced `getting-started/tutorial.md` in the working
> copy, but it does not meet DOC-23: no `filename=` block that `test_recipes.py` can scaffold, no
> ten-step increment, and it drops the environment activation that F11 locks. The tutorial was
> restored from HEAD; this file is the raw draft, not a published page.

# The Rosetta Stone: One App, Five Frameworks

Welcome to the Rosetta Stone guide. To demonstrate the power of Nexy's **Contract-First** architecture, we will build the same simple application—a **Task Tracker**—using five different frontend frameworks.

Regardless of the framework you choose, the **what** (the logic, the data flow, and the routing) remains identical. Only the **how** (the syntax) changes.

## The Application: Task Tracker

Our app consists of:
1. A **Page** to list tasks.
2. A **Layout** to provide a consistent header.
3. An **Island** for the interactive "Add Task" form.
4. An **Action** to handle the server-side mutation.

---

## 1. The Universal Logic (The "What")

Before looking at the frameworks, here is the logic shared by all of them:

- **Route**: `/tasks`
- **Layout**: A simple wrapper with a site title.
- **Action**: `add_task(title: str)` $\rightarrow$ validates input, saves to DB, and calls `revalidate()`.
- **State**: A list of tasks fetched from the server.

---

## 2. The Implementations (The "How")

### 🟦 React
**Page & Layout**
```tsx
// src/routes/layout.tsx
export default function Layout({ children }) {
  return <html><body><header>Nexy Tasks</header>{children}</body></html>;
}

// src/routes/tasks.tsx
export default function TasksPage() {
  return <div><h1>My Tasks</h1><AddTask /></div>;
}
```

**The Island**
```tsx
// src/components/AddTask.tsx
export default function AddTask() {
  const { run, pending } = useAction(add_task);
  return <button disabled={pending} onClick={() => run({ title: "New Task" })}>Add</button>;
}
```

---

### 🟩 Vue
**Page & Layout**
```vue
<!-- src/routes/layout.vue -->
<template>
  <html><body><header>Nexy Tasks</header><slot /></body></html>
</template>

<!-- src/routes/tasks.vue -->
<template>
  <div><h1>My Tasks</h1><AddTask /></div>
</template>
```

**The Island**
```vue
<!-- src/components/AddTask.vue -->
<script setup>
const { run, pending } = useAction(add_task);
</script>
<template>
  <button :disabled="pending" @click="run({ title: 'New Task' })">Add</button>
</template>
```

---

### 🟧 Svelte
**Page & Layout**
```svelte
<!-- src/routes/layout.svelte -->
<script>let { children } = $props();</script>
<html><body><header>Nexy Tasks</header>{@render children()}</body></html>

<!-- src/routes/tasks.svelte -->
<h1>My Tasks</h1>
<AddTask />
```

**The Island**
```svelte
<!-- src/components/AddTask.svelte -->
<script>
  const save = useAction(add_task);
</script>
<button disabled={$save.pending} onclick={() => save.run({ title: "New Task" })}>Add</button>
```

---

### 🟪 Solid
**Page & Layout**
```tsx
// src/routes/layout.tsx
export default function Layout(props) {
  return <html><body><header>Nexy Tasks</header>{props.children}</body></html>;
}

// src/routes/tasks.tsx
export default function TasksPage() {
  return <div><h1>My Tasks</h1><AddTask /></div>;
}
```

**The Island**
```tsx
// src/components/AddTask.tsx
export default function AddTask() {
  const save = useAction(add_task);
  return <button disabled={save.pending()}>Add</button>;
}
```

---

### ⬜ Preact
**Page & Layout**
```tsx
// src/routes/layout.tsx
export default function Layout({ children }) {
  return <html><body><header>Nexy Tasks</header>{children}</body></html>;
}

// src/routes/tasks.tsx
export default function TasksPage() {
  return <div><h1>My Tasks</h1><AddTask /></div>;
}
```

**The Island**
```tsx
// src/components/AddTask.tsx
export default function AddTask() {
  const { run, pending } = useAction(add_task);
  return <button disabled={pending} onClick={() => run({ title: "New Task" })}>Add</button>;
}
```

---

## Conclusion: The Nexy Promise

As you can see, whether you use **React, Vue, Svelte, Solid, or Preact**, the architecture is exactly the same:
1. **File-based routing** defines the URL.
2. **Layouts** wrap the page content.
3. **Islands** bring interactivity to server-rendered pages.
4. **Actions** provide a type-safe bridge to the backend.

You are free to use the tool you love most, without worrying about the underlying plumbing.
