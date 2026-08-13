import * as React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant = "default", size = "default", ...props }, ref) => {
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700",
    outline: "border border-slate-700 bg-transparent hover:bg-slate-800 text-slate-200",
    ghost: "hover:bg-slate-800 text-slate-200",
  };
  const sizes = { default: "h-10 px-4 py-2", sm: "h-8 rounded-md px-3 text-xs", lg: "h-11 rounded-md px-8" };
  return <button ref={ref} className={cn("inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:pointer-events-none disabled:opacity-50", variants[variant], sizes[size], className)} {...props} />;
});
Button.displayName = "Button";
