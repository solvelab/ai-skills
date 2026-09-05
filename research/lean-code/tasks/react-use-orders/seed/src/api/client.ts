import axios, { AxiosError, type AxiosRequestConfig } from 'axios';

/** Every backend body is the envelope; the client unwraps `data` and normalises failures. */
export interface Envelope<T> {
  status: 'success' | 'error';
  code: string;
  message: string;
  data?: T;
}

export class ApiException extends Error {
  constructor(readonly code: string, message: string, readonly status?: number) {
    super(message);
  }
}

const instance = axios.create({ baseURL: '/api', timeout: 10_000 });

function normalizeError(error: unknown): ApiException {
  if (error instanceof AxiosError) {
    const body = error.response?.data as Envelope<unknown> | undefined;
    if (body?.code) return new ApiException(body.code, body.message, error.response?.status);
    if (!error.response) return new ApiException('NETWORK', 'Network error');
  }
  return new ApiException('UNKNOWN', 'Unexpected error');
}

async function unwrap<T>(request: Promise<{ data: Envelope<T> }>): Promise<T> {
  try {
    const { data: body } = await request;
    return body.data as T;
  } catch (error) {
    throw normalizeError(error);
  }
}

/** The one HTTP client of the app. Feature code never calls axios or fetch directly. */
export const apiClient = {
  get: <T>(url: string, config?: AxiosRequestConfig) => unwrap<T>(instance.get(url, config)),
  post: <T>(url: string, body?: unknown, config?: AxiosRequestConfig) =>
    unwrap<T>(instance.post(url, body, config)),
  delete: <T>(url: string, config?: AxiosRequestConfig) => unwrap<T>(instance.delete(url, config)),
};
