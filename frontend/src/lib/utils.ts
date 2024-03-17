import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'; // Extend as needed
  body?: BodyInit | FormData | Record<string, unknown>;
  headers?: HeadersInit;
  json?: boolean;
}

export async function apiRequest(url: string, options: ApiRequestOptions = {}): Promise<unknown> {
  const { method = 'GET', body, headers = {}, ...restOptions } = options;

  // Adjust headers based on the body type
  let adjustedBody: BodyInit | undefined;
  const adjustedHeaders: HeadersInit = { ...headers };
  if (body instanceof FormData) {
    // Let the browser set the Content-Type for FormData
    adjustedBody = body;
  } else if (typeof body === 'object' && !(body instanceof FormData)) {
    // For JSON payloads, set the Content-Type header
    const adjustedHeaders: HeadersInit = { ...headers };
    (adjustedHeaders as Record<string, string>)['Content-Type'] = 'application/json';
    adjustedBody = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, {
      method,
      headers: adjustedHeaders,
      body: adjustedBody,
      ...restOptions,
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('There was a problem with your fetch operation:', error);
    throw error;
  }
}
