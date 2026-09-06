import { z } from 'zod';
import { apiClient } from './client';

/** One zod parser per domain: payload drift throws here, never deep inside a component. */
export const userSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});
export type User = z.infer<typeof userSchema>;

export const fetchUsers = async (): Promise<User[]> =>
  z.array(userSchema).parse(await apiClient.get<unknown>('/users'));
