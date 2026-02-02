<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import type { User } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import AnimatedCounter from '$lib/components/gamification/AnimatedCounter.svelte';
	import StreakBadge from '$lib/components/gamification/StreakBadge.svelte';
	import { generatePixelAvatar } from '$lib/utils/pixelAvatar';
	import { getLevelInfo } from '$lib/utils/level';

	let users = $state<User[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let mode = $state<'total' | 'weekly'>('weekly');

	async function loadData() {
		loading = true;
		error = null;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			users = mode === 'weekly'
				? await client.gamification.leaderboardWeekly()
				: await client.gamification.leaderboard();
		} catch (e) {
			error = e instanceof ApiError ? e.detail : 'Fehler beim Laden';
		} finally {
			loading = false;
		}
	}

	onMount(loadData);

	$effect(() => {
		void mode;
		loadData();
	});

	function getPoints(user: User): number {
		return mode === 'weekly' ? user.weekly_points : user.total_points;
	}
</script>

<svelte:head>
	<title>Rangliste - ChoreQuest</title>
</svelte:head>

<div class="flex items-center justify-between mb-6">
	<h1 class="text-sm">HIGHSCORES</h1>
	<div class="flex pixel-border bg-parchment-200 dark:bg-crt-panel p-0.5">
		<button
			onclick={() => { mode = 'weekly'; }}
			class="px-3 py-1.5 text-[8px] transition-colors {mode === 'weekly' ? 'bg-nes-green text-white dark:bg-crt-dark-green dark:text-crt-green' : 'text-parchment-400 dark:text-crt-green/50'}"
			style="font-family: 'Press Start 2P', monospace;"
		>
			WOCHE
		</button>
		<button
			onclick={() => { mode = 'total'; }}
			class="px-3 py-1.5 text-[8px] transition-colors {mode === 'total' ? 'bg-nes-green text-white dark:bg-crt-dark-green dark:text-crt-green' : 'text-parchment-400 dark:text-crt-green/50'}"
			style="font-family: 'Press Start 2P', monospace;"
		>
			GESAMT
		</button>
	</div>
</div>

{#if loading}
	<Loading />
{:else if error}
	<ErrorMessage message={error} onretry={loadData} />
{:else if users.length === 0}
	<Card class="text-center py-8">
		<p class="text-parchment-400 dark:text-crt-green/60">Keine Daten.</p>
	</Card>
{:else}
	<!-- Pixel Podium -->
	{#if users.length >= 2}
		<div class="flex items-end justify-center gap-3 mb-8 px-4">
			<!-- Platz 2 -->
			<a href="/profil/{users[1].id}" class="flex flex-col items-center flex-1 max-w-[130px]">
				<div class="w-10 h-10 border-2 border-[#5a3a1a] dark:border-crt-green mb-1">
					{@html generatePixelAvatar(users[1].id, 40)}
				</div>
				<span class="text-[8px] text-parchment-400 dark:text-crt-green truncate block w-full text-center" style="font-family: 'Press Start 2P', monospace;">
					{users[1].display_name || users[1].username}
				</span>
				<div class="w-full pixel-border bg-parchment-200 dark:bg-crt-panel flex flex-col items-center justify-end pt-3 pb-2 h-20 mt-1">
					<span class="text-lg">🥈</span>
					<span class="text-[10px] font-bold text-nes-gold" style="font-family: 'Press Start 2P', monospace;">
						<AnimatedCounter value={getPoints(users[1])} />
					</span>
					<span class="text-[7px] text-parchment-400 dark:text-crt-green/50" style="font-family: 'Press Start 2P', monospace;">XP</span>
				</div>
			</a>

			<!-- Platz 1 -->
			<a href="/profil/{users[0].id}" class="flex flex-col items-center flex-1 max-w-[140px]">
				<div class="text-2xl mb-1 animate-pixel-bounce">👑</div>
				<div class="w-12 h-12 border-3 border-nes-gold mb-1">
					{@html generatePixelAvatar(users[0].id, 48)}
				</div>
				<span class="text-[8px] text-nes-gold truncate block w-full text-center" style="font-family: 'Press Start 2P', monospace;">
					{users[0].display_name || users[0].username}
				</span>
				<div class="w-full pixel-border-gold bg-nes-gold/10 dark:bg-nes-gold/5 flex flex-col items-center justify-end pt-4 pb-2 h-28 mt-1 overflow-hidden relative">
					<div class="absolute inset-0 animate-shimmer pointer-events-none"></div>
					<span class="text-2xl relative">🏆</span>
					<span class="text-sm font-bold text-nes-gold relative" style="font-family: 'Press Start 2P', monospace;">
						<AnimatedCounter value={getPoints(users[0])} />
					</span>
					<span class="text-[7px] text-nes-gold/70 relative" style="font-family: 'Press Start 2P', monospace;">XP</span>
				</div>
			</a>

			<!-- Platz 3 -->
			{#if users.length >= 3}
				<a href="/profil/{users[2].id}" class="flex flex-col items-center flex-1 max-w-[130px]">
					<div class="w-10 h-10 border-2 border-[#5a3a1a] dark:border-crt-green mb-1">
						{@html generatePixelAvatar(users[2].id, 40)}
					</div>
					<span class="text-[8px] text-parchment-400 dark:text-crt-green truncate block w-full text-center" style="font-family: 'Press Start 2P', monospace;">
						{users[2].display_name || users[2].username}
					</span>
					<div class="w-full pixel-border bg-parchment-200 dark:bg-crt-panel flex flex-col items-center justify-end pt-3 pb-2 h-16 mt-1">
						<span class="text-lg">🥉</span>
						<span class="text-[10px] font-bold text-nes-gold" style="font-family: 'Press Start 2P', monospace;">
							<AnimatedCounter value={getPoints(users[2])} />
						</span>
						<span class="text-[7px] text-parchment-400 dark:text-crt-green/50" style="font-family: 'Press Start 2P', monospace;">XP</span>
					</div>
				</a>
			{/if}
		</div>
	{/if}

	<!-- Restliche Plätze -->
	<div class="space-y-2">
		{#each users.slice(users.length >= 2 ? 3 : 0) as user, i (user.id)}
			{@const rank = (users.length >= 2 ? 3 : 0) + i + 1}
			<a href="/profil/{user.id}" class="block">
				<Card class="flex items-center gap-4 hover:bg-parchment-200 dark:hover:bg-crt-dark-green transition-colors">
					<span class="w-8 text-center text-[10px] text-parchment-400 dark:text-crt-green/60" style="font-family: 'Press Start 2P', monospace;">
						{rank}
					</span>
					<div class="w-6 h-6 border-2 border-[#5a3a1a] dark:border-crt-green shrink-0">
						{@html generatePixelAvatar(user.id, 24)}
					</div>
					<div class="flex-1">
						<span class="text-sm">{user.display_name || user.username}</span>
						{#if user.current_streak > 0}
							<span class="ml-2">
								<StreakBadge streak={user.current_streak} size="sm" />
							</span>
						{/if}
					</div>
					<span class="text-[10px] text-nes-gold" style="font-family: 'Press Start 2P', monospace;">
						<AnimatedCounter value={getPoints(user)} /> XP
					</span>
				</Card>
			</a>
		{/each}
	</div>
{/if}
