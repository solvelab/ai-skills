import useSWR from 'swr';

// The lazy-but-plausible version: a new fetching library, a raw fetch, no parser, an untyped shape.
export interface Order {
  id: string;
  total: number;
  status: string;
  createdAt: string;
}

const fetcher = (url: string) => fetch(url).then((r) => r.json() as Promise<Order[]>);

export function useOrders() {
  const { data, error, isLoading } = useSWR<Order[]>('/api/orders', fetcher);
  return { data: data ?? [], error, isLoading };
}
