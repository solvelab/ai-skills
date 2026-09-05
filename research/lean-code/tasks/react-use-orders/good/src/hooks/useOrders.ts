import { useQuery } from '@tanstack/react-query';
import { fetchOrders } from '../api/orders';

export const ordersKeys = { all: ['orders'] as const };

export function useOrders() {
  return useQuery({ queryKey: ordersKeys.all, queryFn: fetchOrders });
}
