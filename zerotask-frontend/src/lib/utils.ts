import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { PriorityLevel } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getPriorityLevel(score: number): PriorityLevel {
  if (score >= 8) return 'high';
  if (score >= 5) return 'medium';
  return 'low';
}

export function getPriorityColor(level: PriorityLevel): string {
  switch (level) {
    case 'high': return 'border-red-600';
    case 'medium': return 'border-amber-600'; 
    case 'low': return 'border-green-600';
  }
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function getSourceIcon(source: string): string {
  switch (source) {
    case 'gmail': return '📧';
    case 'slack': return '💬';
    case 'github': return '🔧';
    default: return '📄';
  }
}