<script lang="ts">
	import type { User } from '$lib/api/types';
	import Icon from '$lib/components/ui/Icon.svelte';
	import { mdiTrophyVariant, mdiFire } from '@mdi/js';

	interface Props {
		users: User[];
		mode: 'total' | 'weekly';
	}

	let { users, mode }: Props = $props();

	const rankColors = ['text-yellow-500', 'text-gray-400', 'text-amber-600'];
</script>

<div class="space-y-2">
	{#each users as user, i (user.id)}
		<a
			href="/profil/{user.id}"
			class="flex items-center gap-4 p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-primary-300 transition-colors"
		>
			<div class="w-8 text-center">
				{#if i < 3}
					<Icon path={mdiTrophyVariant} size={24} class={rankColors[i]} />
				{:else}
					<span class="text-lg font-bold text-gray-400">{i + 1}</span>
				{/if}
			</div>
			<div class="flex-1">
				<span class="font-semibold">{user.display_name || user.username}</span>
				{#if user.current_streak > 0}
					<span class="flex items-center gap-1 text-xs text-gray-500 mt-0.5">
						<Icon path={mdiFire} size={12} class="text-orange-500" />
						{user.current_streak} Tage
					</span>
				{/if}
			</div>
			<span class="text-lg font-bold text-primary-600 dark:text-primary-400">
				{mode === 'weekly' ? user.weekly_points : user.total_points}
			</span>
		</a>
	{/each}
</div>
