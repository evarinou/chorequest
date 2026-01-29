import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type { User } from '$lib/api/types';

function persistentStore<T>(key: string, initial: T) {
	const stored = browser ? localStorage.getItem(key) : null;
	const value = stored ? JSON.parse(stored) : initial;
	const store = writable<T>(value);

	if (browser) {
		store.subscribe((v) => {
			localStorage.setItem(key, JSON.stringify(v));
		});
	}

	return store;
}

export const selectedUserId = persistentStore<number | null>('chorequest_selected_user', null);
export const users = writable<User[]>([]);

export const selectedUser = derived(
	[users, selectedUserId],
	([$users, $selectedUserId]) => $users.find((u) => u.id === $selectedUserId) ?? null
);
