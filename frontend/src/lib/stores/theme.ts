import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createThemeStore() {
	const stored = browser ? localStorage.getItem('chorequest_dark_mode') : null;
	const initial = stored ? JSON.parse(stored) : false;
	const store = writable<boolean>(initial);

	if (browser) {
		store.subscribe((dark) => {
			localStorage.setItem('chorequest_dark_mode', JSON.stringify(dark));
			if (dark) {
				document.documentElement.classList.add('dark');
			} else {
				document.documentElement.classList.remove('dark');
			}
		});
	}

	return store;
}

export const darkMode = createThemeStore();
