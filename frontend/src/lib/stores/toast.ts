import { writable } from 'svelte/store';

export interface Toast {
	id: number;
	message: string;
	type: 'success' | 'error' | 'info' | 'points' | 'achievement';
	icon?: string;
	duration?: number;
}

let nextId = 0;

export const toasts = writable<Toast[]>([]);

function addToast(toast: Omit<Toast, 'id'>) {
	const id = nextId++;
	const duration = toast.duration ?? 3000;
	toasts.update((t) => [...t, { ...toast, id }]);
	if (duration > 0) {
		setTimeout(() => {
			toasts.update((t) => t.filter((item) => item.id !== id));
		}, duration);
	}
}

export function showToast(message: string, type: Toast['type'] = 'info') {
	addToast({ message, type });
}

export function showPointsToast(points: number, bonus: number) {
	const msg = bonus > 0 ? `+${points} Punkte (${bonus} Bonus!)` : `+${points} Punkte`;
	addToast({ message: msg, type: 'points', duration: 4000 });
}

export function showAchievementToast(name: string) {
	addToast({ message: `Achievement freigeschaltet: ${name}`, type: 'achievement', duration: 5000 });
}
