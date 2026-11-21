import { useState } from "preact/hooks";

type Plan = {
  name: string;
  blurb: string;
  monthly: number; // dollars a month, billed monthly
  yearly: number; // dollars a month, billed once a year
  features: string[];
  featured?: boolean;
};

const PLANS: Plan[] = [
  {
    name: "Hobby",
    blurb: "For a side project and its one server.",
    monthly: 0,
    yearly: 0,
    features: ["5 monitors", "Checks every 5 minutes", "Email alerts", "A public status page"],
  },
  {
    name: "Team",
    blurb: "For a product people pay for.",
    monthly: 19,
    yearly: 15,
    features: ["50 monitors", "Checks every 30 seconds", "Email, chat and SMS alerts", "A status page on your domain", "Incident timeline"],
    featured: true,
  },
  {
    name: "Business",
    blurb: "For teams on call, in several regions.",
    monthly: 49,
    yearly: 39,
    features: ["200 monitors", "Checks from 6 regions", "On-call rotations", "Certificate and domain expiry", "90 days of history"],
  },
];

const CHECK = "M20 6L9 17l-5-5";

function Price({ plan, yearly }: { plan: Plan; yearly: boolean }) {
  const amount = yearly ? plan.yearly : plan.monthly;
  if (!amount) return <p class="mt-6 text-4xl font-semibold tracking-tight">Free</p>;
  return (
    <p class="mt-6 flex items-baseline gap-1.5">
      <span class="text-4xl font-semibold tracking-tight tabular-nums">${amount}</span>
      <span class="text-sm text-foreground-second">a month{yearly ? ", billed yearly" : ""}</span>
    </p>
  );
}

function Card({ plan, yearly }: { plan: Plan; yearly: boolean }) {
  const frame = plan.featured ? "border-foreground shadow-[0_24px_60px_-36px_rgb(11_18_32/0.5)]" : "border-border";
  return (
    <article class={`relative flex flex-col rounded-2xl border bg-background p-6 ${frame}`}>
      {plan.featured && (
        <span class="absolute -top-3 left-6 rounded-full bg-foreground px-3 py-1 text-xs font-medium text-background">Most picked</span>
      )}
      <h3 class="text-lg font-semibold">{plan.name}</h3>
      <p class="mt-1 text-sm text-foreground-second">{plan.blurb}</p>
      <Price plan={plan} yearly={yearly} />
      <ul class="mt-6 flex-1 space-y-3 text-sm">
        {plan.features.map((feature) => (
          <li key={feature} class="flex gap-2.5">
            <svg viewBox="0 0 24 24" class="mt-0.5 size-4 flex-none stroke-signal" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d={CHECK} />
            </svg>
            {feature}
          </li>
        ))}
      </ul>
      <a
        href="#join"
        class={`mt-8 inline-flex h-11 items-center justify-center rounded-lg text-sm font-medium transition-opacity hover:opacity-85 ${
          plan.featured ? "bg-foreground text-background" : "border border-border-second"
        }`}
      >
        Join the waitlist
      </a>
    </article>
  );
}

// The prices are in this file, so the server renders them into the page: without JavaScript the
// monthly prices show, and the switch below is what the island adds.
export default function Pricing() {
  const [yearly, setYearly] = useState(false);
  const option = (on: boolean) =>
    `h-9 rounded-md px-4 text-sm font-medium transition-colors ${
      yearly === on ? "bg-background text-foreground shadow-sm" : "text-foreground-second hover:text-foreground"
    }`;

  return (
    <div>
      <div class="flex justify-center">
        <div role="group" aria-label="Billing" class="inline-flex gap-1 rounded-lg border border-border bg-background-second p-1">
          <button type="button" class={option(false)} aria-pressed={!yearly} onClick={() => setYearly(false)}>
            Monthly
          </button>
          <button type="button" class={option(true)} aria-pressed={yearly} onClick={() => setYearly(true)}>
            Yearly <span class="ml-1 text-signal">-20%</span>
          </button>
        </div>
      </div>
      <div class="mt-10 grid gap-6 md:grid-cols-3">
        {PLANS.map((plan) => (
          <Card key={plan.name} plan={plan} yearly={yearly} />
        ))}
      </div>
    </div>
  );
}
