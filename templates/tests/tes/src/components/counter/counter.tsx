

import { useState } from "react";
import type { ReactNode } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div className="flex justify-end rounded-xl p-4 border border-white/40 hover:rounded-2xl hover:border-dashed hover:bg-[hsl(193,46%,29%)]/5 transition-all duration-300">
      <div className="flex-1 flex flex-col justify-between gap-2">
        <p className="uppercase text-xs font-mono font-medium border border-white/40 text-white w-fit px-2 py-1 rounded-2xl">
          Counter
        </p>
        <span className="text-6xl font-medium text-white w-fit ">
          {count}
        </span>
      </div>

      <div className="relative md:h-full flex flex-col items-center justify-between p-1 border border-gray-50/40 rounded-full">
        <Button onClick={() => setCount((c) => c + 1)}>
          <AddIcon />
        </Button>

        <div className="space-y-0.5px opacity-40 z-0 absolute top-1/2 -translate-y-1/2">
          {Array(30).fill(0).map((_, i) => (
            <div key={i} className="border-b border-white w-5 h-0.5" />
          ))}
        </div>

        <Button onClick={() => setCount((c) => c - 1)} variant="secondary">
          <RemoveIcon />
        </Button>
      </div>
    </div>
  );
}

type ButtonVariant = "primary" | "secondary";

type ButtonProps = {
  onClick: () => void;
  children: ReactNode;
  variant?: ButtonVariant;
};

const Button = ({ onClick, children, variant = "primary" }: ButtonProps) => (
  <button
    onClick={onClick}
    className={` z-10 size-8 cursor-pointer flex items-center justify-center  rounded-full transition-colors  ${
      variant === "primary"
        ? "bg-white text-gray-950 hover:bg-yellow-500"
        : "border border-white/40 text-white bg-background/0.5 backdrop-blur-2xl hover:bg-indigo-100/20"
    }`}
  >
    {children}
  </button>
);

const AddIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="size-5">
    <path d="M5 12h14" />
    <path d="M12 5v14" />
  </svg>
);

const RemoveIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="size-5">
    <path d="M5 12h14" />
  </svg>
);

