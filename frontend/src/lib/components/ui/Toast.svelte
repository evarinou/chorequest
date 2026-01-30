<script lang="ts">
	import { toasts } from '$lib/stores/toast';
	import { mdiCheck, mdiAlertCircle, mdiInformation, mdiStar, mdiTrophy } from '@mdi/js';
	import Icon from './Icon.svelte';

	const iconMap: Record<string, string> = {
		success: mdiCheck,
		error: mdiAlertCircle,
		info: mdiInformation,
		points: mdiStar,
		achievement: mdiTrophy
	};

	const colorMap: Record<string, string> = {
		success: 'bg-success-500',
		error: 'bg-danger-500',
		info: 'bg-primary-500',
		points: 'gradient-card-gold text-yellow-900',
		achievement: 'gradient-card-purple text-purple-900 dark:text-purple-100'
	};
</script>

<div class="fixed bottom-20 md:bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
	{#each $toasts as toast (toast.id)}
		<div class="animate-slide-in flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg {colorMap[toast.type]} {toast.type !== 'points' && toast.type !== 'achievement' ? 'text-white' : ''}">
			{#if toast.type === 'achievement'}
				<span class="animate-bounce-in inline-block">
					<Icon path={iconMap[toast.type]} size={20} />
				</span>
			{:else}
				<Icon path={iconMap[toast.type]} size={20} />
			{/if}
			<span class="text-sm font-medium">{toast.message}</span>
		</div>
	{/each}
</div>
