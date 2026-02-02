<script lang="ts">
	import type { User } from '$lib/api/types';
	import { generatePixelAvatar } from '$lib/utils/pixelAvatar';

	interface Props {
		users: User[];
		mode: 'total' | 'weekly';
	}

	let { users, mode }: Props = $props();
</script>

<div class="space-y-2">
	{#each users as user, i (user.id)}
		<a
			href="/profil/{user.id}"
			class="flex items-center gap-4 p-3 pixel-border bg-parchment-50 dark:bg-crt-panel hover:bg-parchment-200 dark:hover:bg-crt-dark-green transition-colors"
		>
			<div class="w-8 text-center">
				{#if i < 3}
					<span class="text-lg">{i === 0 ? '👑' : i === 1 ? '🥈' : '🥉'}</span>
				{:else}
					<span class="text-[10px] text-parchment-400 dark:text-crt-green" style="font-family: 'Press Start 2P', monospace;">
						{i + 1}
					</span>
				{/if}
			</div>
			<div class="w-6 h-6 border-2 border-[#5a3a1a] dark:border-crt-green shrink-0">
				{@html generatePixelAvatar(user.id, 24)}
			</div>
			<div class="flex-1">
				<span class="text-sm">{user.display_name || user.username}</span>
				{#if user.current_streak > 0}
					<span class="text-xs text-nes-orange ml-2">🔥{user.current_streak}</span>
				{/if}
			</div>
			<span class="text-[10px] text-nes-gold" style="font-family: 'Press Start 2P', monospace;">
				{mode === 'weekly' ? user.weekly_points : user.total_points} XP
			</span>
		</a>
	{/each}
</div>
