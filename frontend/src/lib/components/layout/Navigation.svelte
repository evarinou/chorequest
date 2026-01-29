<script lang="ts">
	import { page } from '$app/state';
	import { mdiViewDashboard, mdiClipboardList, mdiDoor, mdiTrophy, mdiRobotHappy } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';

	const navItems = [
		{ href: '/', icon: mdiViewDashboard, label: 'Übersicht' },
		{ href: '/aufgaben', icon: mdiClipboardList, label: 'Aufgaben' },
		{ href: '/raeume', icon: mdiDoor, label: 'Räume' },
		{ href: '/rangliste', icon: mdiTrophy, label: 'Rangliste' },
		{ href: '/zusammenfassung', icon: mdiRobotHappy, label: 'KI-Bericht' }
	];

	function isActive(href: string): boolean {
		if (href === '/') return page.url.pathname === '/';
		return page.url.pathname.startsWith(href);
	}
</script>

<!-- Mobile Bottom Navigation -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
	<div class="flex justify-around">
		{#each navItems as item (item.href)}
			<a
				href={item.href}
				class="flex flex-col items-center py-2 px-3 text-xs transition-colors {isActive(item.href) ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'}"
			>
				<Icon path={item.icon} size={22} />
				<span class="mt-1">{item.label}</span>
			</a>
		{/each}
	</div>
</nav>

<!-- Desktop Sidebar -->
<aside class="hidden md:flex flex-col w-56 shrink-0 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 min-h-[calc(100vh-3.5rem)]">
	<nav class="flex flex-col gap-1 p-3">
		{#each navItems as item (item.href)}
			<a
				href={item.href}
				class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors {isActive(item.href) ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700/50'}"
			>
				<Icon path={item.icon} size={20} />
				{item.label}
			</a>
		{/each}
	</nav>
</aside>
