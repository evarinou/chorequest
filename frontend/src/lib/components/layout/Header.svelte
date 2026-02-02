<script lang="ts">
	import { mdiCog } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';
	import UserSelector from './UserSelector.svelte';
	import StreakBadge from '$lib/components/gamification/StreakBadge.svelte';
	import { selectedUser } from '$lib/stores/user';
	import { getLevelInfo } from '$lib/utils/level';
	import { generatePixelAvatar } from '$lib/utils/pixelAvatar';

	let levelInfo = $derived($selectedUser ? getLevelInfo($selectedUser.total_points) : null);
	let avatarSvg = $derived($selectedUser ? generatePixelAvatar($selectedUser.id) : '');
</script>

<header class="sticky top-0 z-40 border-b-3 border-b-[#5a3a1a] dark:border-b-crt-green bg-parchment-100 dark:bg-crt-bg">
	<div class="max-w-5xl mx-auto flex items-center justify-between px-4 h-14">
		<!-- Logo -->
		<a href="/" class="flex items-center gap-2">
			<span class="text-[10px] text-nes-green dark:text-crt-green" style="font-family: 'Press Start 2P', monospace;">
				ChoreQuest
			</span>
		</a>

		<!-- Center: Level + XP Bar (only if user selected) -->
		{#if $selectedUser && levelInfo}
			<div class="hidden md:flex items-center gap-3 flex-1 max-w-md mx-6">
				<!-- Pixel Avatar -->
				<div class="w-8 h-8 border-2 border-[#5a3a1a] dark:border-crt-green shrink-0">
					{@html avatarSvg}
				</div>

				<div class="flex-1 min-w-0">
					<div class="flex items-center justify-between mb-0.5">
						<span class="text-[7px] text-nes-gold dark:text-nes-gold" style="font-family: 'Press Start 2P', monospace;">
							LV.{levelInfo.level} {levelInfo.title}
						</span>
						<span class="text-xs text-parchment-400 dark:text-crt-green">
							{levelInfo.currentXP}/{levelInfo.requiredXP} XP
						</span>
					</div>
					<!-- Segmented XP Bar -->
					<div class="flex gap-px h-3 bg-parchment-300 dark:bg-[#0a1a0a] border-2 border-[#5a3a1a] dark:border-crt-border">
						{#each Array(10) as _, i}
							{@const filled = levelInfo.progress >= (i + 1) * 10}
							{@const partial = !filled && levelInfo.progress > i * 10}
							<div
								class="flex-1 transition-colors duration-100 {filled ? 'bg-nes-green dark:bg-crt-green' : partial ? 'bg-nes-green/40 dark:bg-crt-green/40' : ''}"
							></div>
						{/each}
					</div>
				</div>
			</div>
		{/if}

		<div class="flex items-center gap-3">
			{#if $selectedUser && $selectedUser.current_streak > 0}
				<StreakBadge streak={$selectedUser.current_streak} size="md" />
			{/if}
			<UserSelector />
			<a
				href="/einstellungen"
				class="p-2 text-parchment-400 hover:text-nes-gold dark:text-crt-green dark:hover:text-nes-gold transition-colors"
			>
				<Icon path={mdiCog} size={20} />
			</a>
		</div>
	</div>
</header>
