# রাউটিং

Nexy এর দুটি নেটিভ রাউটার রয়েছে। আপনি প্রতি বৈশিষ্ট্য একটি বাছাই করতে পারেন; তারা একই অ্যাপ্লিকেশনে সহাবস্থান করতে পারে।

**নিশ্চিত নন? ফাইল-ভিত্তিক ব্যবহার করুন রাউটিং** এটি কোনও সেটআপ ছাড়াই পৃষ্ঠা এবং API শেষ পয়েন্টগুলি কভার করে৷ মডুলার রাউটার যোগ করুন যখন ব্যাকএন্ডে কন্ট্রোলার, ইনজেকশন পরিষেবা বা গার্ডের প্রয়োজন হয়।

| আপনি নির্মাণ করছেন | ব্যবহার করুন |
|---|---|
| পৃষ্ঠা, বিষয়বস্তু, কয়েকটি শেষ পয়েন্ট সহ একটি সাইট | ফাইল-ভিত্তিক |
| রুট জুড়ে শেয়ার করা পরিষেবা সহ একটি বড় API | মডুলার |
| উভয়: মানুষের জন্য পৃষ্ঠা, মেশিনের জন্য একটি কাঠামোগত API | ফাইল-ভিত্তিক এবং মডুলার একসাথে |

<!-- router:fbr,custom -->
```diagram filename="ফাইল-ভিত্তিক রাউটার, এক নজরে"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```
<!-- /router -->

<!-- router:modular -->
```diagram filename="মডুলার রাউটার, এক নজরে"
@Controller()             class AppController   →  /
@Controller("/about")     class AboutController →  /about/
@Controller("/api/users") class UserController  →  /api/users/  (get, post, …)
@Module()                 class AppModule       →  lists the controllers
useRouter = AppModule     nexyconfig.py         →  mounts the module
```
<!-- /router -->

| রাউটার | উৎস | দ্বারা সক্রিয় |
|---|---|---|
| [ফাইল-ভিত্তিক (FBR)](fbr/README.md) | প্রতিটি ফাইল `src/routes/` এর অধীনে | ডিরেক্টরি বিদ্যমান |
| [মডুলার](modular/README.md) | কন্ট্রোলার এবং মডিউল | `useRouter = AppModule` `nexyconfig.py` |

FBR স্ক্যান করা হয় যখনই `src/routes/` থাকে, এমনকি একটি মডুলার রাউটার মাউন্ট করেও।

## সহাবস্থান এবং অগ্রাধিকার

আপনি FBR, মডুলার, এবং কাস্টম ইন্টিগ্রেশন একত্রিত করতে পারেন। Nexy এই রুটগুলিকে সেগুলি যেভাবে আবিষ্কৃত হয় সে অনুযায়ী নিবন্ধন করে৷ যদি দুটি রাউটার একই ইউআরএল পাথ সংজ্ঞায়িত করে, প্রথমটি নিবন্ধিত বিজয়ী হয়। 

*দ্রষ্টব্য: Nexy বর্তমানে URL সংঘর্ষের জন্য একটি ডায়াগনস্টিক প্রদান করে না; একটি পথ দাবি করার প্রথম পথটি কেবল অন্যদের ছায়া দেয়।*

<!-- router:fbr,custom -->
## ফাইল-ভিত্তিক রাউটিং

একটি রুট একটি ফাইল. URL হল এর পাথ `src/routes/` এর অধীনে, বিয়োগ এক্সটেনশন। Next.js এর মতো, একটি প্রকল্প দুটি মোডের একটিতে, `useCSR` এর সাথে নির্বাচিত:

| | `useCSR = False` (ডিফল্ট) | `useCSR = True` |
|---|---|---|
| পাতা | `.nexy`, `.md`, `.mdx` | আপনার ক্লায়েন্ট ফ্রেমওয়ার্কের ফাইল |
| রুট লেআউট | `layout.nexy` | `layout.tsx` (React) |
| ক্লায়েন্ট উপাদান | অনুমোদিত, পৃষ্ঠার ভিতরে দ্বীপ হিসাবে | পৃষ্ঠাগুলি নিজেরাই |
| API রুট | `.py` | `.py` |

[সার্ভার মোড এবং ক্লায়েন্ট মোড](fbr/modes.md) দেখুন।

| ধারা | এটা কভার কি |
|---|---|
| [fbr/পৃষ্ঠা](fbr/pages/README.md) | পৃষ্ঠা, [গতিশীল রুট](fbr/pages/dynamic-routes.md) এবং রুট গ্রুপ |
| [fbr/লেআউট](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/হ্যান্ডলার](fbr/handlers/README.md) | `.py` রুট হ্যান্ডলার, [বৈধকরণ এবং ত্রুটি](fbr/handlers/validation-and-errors.md) |
| [fbr/নির্ভরতা](fbr/dependencies/README.md) | `dependencies.py` এবং গার্ড, ডিরেক্টরি দ্বারা উত্তরাধিকারসূত্রে প্রাপ্ত |
| [fbr/মিডলওয়্যার](fbr/middleware/README.md) | `middleware.py`, ডিরেক্টরি দ্বারা উত্তরাধিকারসূত্রে প্রাপ্ত |
| [fbr/ত্রুটি](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON ত্রুটি |
| [fbr/নেভিগেশন](fbr/navigation/linking-and-navigating.md) | লিঙ্কিং, ক্লায়েন্ট নেভিগেশন, [হুকস](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | WebSocket হ্যান্ডলার |
| [fbr/উত্তরাধিকার](fbr/inheritance.md) | কিভাবে লেআউট, নির্ভরতা এবং ত্রুটি পৃষ্ঠাগুলি উত্তরাধিকারসূত্রে পাওয়া যায় |
<!-- /router -->

## মডুলার রাউটিং

কন্ট্রোলার, মডিউল এবং নির্ভরতা ইনজেকশন, এর স্টাইলে NestJS। [মডুলার রাউটিং](modular/README.md) এবং [Nexy এবং NestJS](modular/vs-nestjs.md) দেখুন।

<!-- router:modular -->
| ধারা | এটা কভার কি |
|---|---|
| [মডুলার](modular/README.md) | `@Controller`, `@Module`, আমদানি ও রপ্তানি |
| [মডুলার/নির্ভরতা-ইনজেকশন](modular/dependency-injection.md) | `@Injectable`, স্কোপ এবং ধারক |
| [মডুলার/গার্ডস-এন্ড-মেটাডেটা](modular/guards-and-metadata.md) | `@UseGuard`, `@UseResponse` এবং OpenAPI মেটাডেটা |

একটি কন্ট্রোলার একটি `.nexy` ভিউ `useViews` দিয়ে ফেরত দেয়, এবং এটিকে তার লেআউটে হাত দিয়ে পাস করে: ফোল্ডার দ্বারা কোন `layout.nexy` প্রয়োগ করা হয় না।
<!-- /router -->

## কাস্টম ইন্টিগ্রেশন

আপনি আপনার Nexy প্রজেক্টে একটি বিদ্যমান FastAPI রাউটারও সংহত করতে পারেন। [কাস্টম রাউটিং ইন্টিগ্রেশন](custom/README.md) দেখুন।

## পরবর্তী পদক্ষেপ

<!-- router:fbr,custom -->
- [ফাইল-ভিত্তিক রাউটিং](fbr/README.md)
<!-- /router -->
<!-- router:modular -->
- [মডুলার রাউটিং](modular/README.md)
<!-- /router -->
- [রেন্ডারিং ](../rendering/README.md)
- [ভিউ ](../views/README.md): ফাইলের ভিতরে যা যায়
