import { writable } from 'svelte/store';
import { browser } from '$app/environment';

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

export const apiBaseUrl = persistentStore('chorequest_api_url', 'http://localhost:8000');
export const apiKey = persistentStore('chorequest_api_key', '');
