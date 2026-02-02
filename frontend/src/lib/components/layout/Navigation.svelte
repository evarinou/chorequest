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
<nav class="md:hidden fixed bottom-0 left-0 right-0 z-40 border-t-3 border-t-[#5a3a1a] dark:border-t-crt-green bg-parchment-100 dark:bg-crt-bg">
	<div class="flex justify-around">
		{#each navItems as item (item.href)}
			<a
				href={item.href}
				class="flex flex-col items-center py-2 px-2 text-[7px] transition-colors relative {isActive(item.href) ? 'text-nes-green dark:text-crt-green' : 'text-parchment-400 dark:text-crt-green/50'}"
				style="font-family: 'Press Start 2P', monospace;"
			>
				{#if isActive(item.href)}
					<span class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[3px] bg-nes-green dark:bg-crt-green"></span>
				{/if}
				<Icon path={item.icon} size={20} />
				<span class="mt-1">{item.label}</span>
			</a>
		{/each}
	</div>
</nav>

<!-- Desktop Sidebar -->
<aside class="hidden md:flex flex-col w-56 shrink-0 border-r-3 border-r-[#5a3a1a] dark:border-r-crt-green bg-parchment-50 dark:bg-crt-bg min-h-[calc(100vh-3.5rem)]">
	<nav class="flex flex-col gap-1 p-3">
		{#each navItems as item (item.href)}
			<a
				href={item.href}
				class="flex items-center gap-3 px-3 py-2.5 text-[9px] transition-colors {isActive(item.href) ? 'bg-nes-green/10 text-nes-green dark:bg-crt-green/10 dark:text-crt-green border-l-3 border-l-nes-green dark:border-l-crt-green' : 'text-parchment-400 dark:text-crt-green/60 hover:bg-parchment-200 dark:hover:bg-crt-panel'}"
				style="font-family: 'Press Start 2P', monospace;"
			>
				{#if isActive(item.href)}
					<span class="text-nes-green dark:text-crt-green">&gt;</span>
				{:else}
					<span class="opacity-0">&gt;</span>
				{/if}
				<Icon path={item.icon} size={18} />
				{item.label}
			</a>
		{/each}
	</nav>
</aside>
