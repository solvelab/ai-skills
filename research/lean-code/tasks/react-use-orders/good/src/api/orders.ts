import { z } from 'zod';
import { apiClient } from './client';

export const orderSchema = z.object({
  id: z.string(),
  total: z.number(),
  status: z.enum(['pending', 'paid', 'cancelled']),
  createdAt: z.string(),
});
export type Order = z.infer<typeof orderSchema>;

export const fetchOrders = async (): Promise<Order[]> =>
  z.array(orderSchema).parse(await apiClient.get<unknown>('/orders'));
