<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import type { User } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import AnimatedCounter from '$lib/components/gamification/AnimatedCounter.svelte';
	import StreakBadge from '$lib/components/gamification/StreakBadge.svelte';
	import { mdiTrophyVariant, mdiCrown } from '@mdi/js';

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
	<h1 class="text-2xl font-bold">Rangliste</h1>
	<div class="flex bg-gray-200 dark:bg-gray-700 rounded-lg p-0.5">
		<button
			onclick={() => { mode = 'weekly'; }}
			class="px-3 py-1.5 text-sm rounded-md transition-colors {mode === 'weekly' ? 'bg-white dark:bg-gray-600 shadow-sm font-medium' : 'text-gray-600 dark:text-gray-400'}"
		>
			Woche
		</button>
		<button
			onclick={() => { mode = 'total'; }}
			class="px-3 py-1.5 text-sm rounded-md transition-colors {mode === 'total' ? 'bg-white dark:bg-gray-600 shadow-sm font-medium' : 'text-gray-600 dark:text-gray-400'}"
		>
			Gesamt
		</button>
	</div>
</div>

{#if loading}
	<Loading />
{:else if error}
	<ErrorMessage message={error} onretry={loadData} />
{:else if users.length === 0}
	<Card class="text-center py-8">
		<p class="text-gray-500 dark:text-gray-400">Keine Daten vorhanden.</p>
	</Card>
{:else}
	<!-- Podium für Top 3 -->
	{#if users.length >= 2}
		<div class="flex items-end justify-center gap-2 mb-8 px-4">
			<!-- Platz 2 - Silber -->
			<a href="/profil/{users[1].id}" class="flex flex-col items-center flex-1 max-w-[130px] group">
				<div class="text-center mb-2">
					<span class="text-sm font-semibold text-gray-600 dark:text-gray-300 group-hover:text-primary-500 transition-colors truncate block">
						{users[1].display_name || users[1].username}
					</span>
				</div>
				<div class="w-full rounded-t-xl bg-gradient-to-b from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 flex flex-col items-center justify-end pt-4 pb-3 h-24 relative">
					<Icon path={mdiTrophyVariant} size={28} class="text-gray-400 mb-1" />
					<span class="font-bold text-lg"><AnimatedCounter value={getPoints(users[1])} /></span>
					<span class="text-xs text-gray-500">Pkt.</span>
					<span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-gray-300 dark:bg-gray-500 text-gray-700 dark:text-gray-200 rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold">2</span>
				</div>
			</a>

			<!-- Platz 1 - Gold -->
			<a href="/profil/{users[0].id}" class="flex flex-col items-center flex-1 max-w-[140px] group">
				<div class="text-center mb-2">
					<Icon path={mdiCrown} size={24} class="text-yellow-500 mx-auto animate-bounce-in" />
					<span class="text-sm font-bold text-gray-800 dark:text-gray-100 group-hover:text-primary-500 transition-colors truncate block">
						{users[0].display_name || users[0].username}
					</span>
				</div>
				<div class="w-full rounded-t-xl gradient-card-gold flex flex-col items-center justify-end pt-4 pb-3 h-32 relative animate-shimmer overflow-hidden">
					<Icon path={mdiTrophyVariant} size={36} class="text-yellow-600 dark:text-yellow-300 mb-1" />
					<span class="font-bold text-xl"><AnimatedCounter value={getPoints(users[0])} /></span>
					<span class="text-xs text-yellow-700/70 dark:text-yellow-300/70">Pkt.</span>
					<span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-yellow-400 text-yellow-900 rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold shadow-md">1</span>
				</div>
			</a>

			<!-- Platz 3 - Bronze -->
			{#if users.length >= 3}
				<a href="/profil/{users[2].id}" class="flex flex-col items-center flex-1 max-w-[130px] group">
					<div class="text-center mb-2">
						<span class="text-sm font-semibold text-gray-600 dark:text-gray-300 group-hover:text-primary-500 transition-colors truncate block">
							{users[2].display_name || users[2].username}
						</span>
					</div>
					<div class="w-full rounded-t-xl bg-gradient-to-b from-amber-200 to-amber-300 dark:from-amber-800 dark:to-amber-900 flex flex-col items-center justify-end pt-4 pb-3 h-20 relative">
						<Icon path={mdiTrophyVariant} size={24} class="text-amber-600 dark:text-amber-400 mb-1" />
						<span class="font-bold text-lg"><AnimatedCounter value={getPoints(users[2])} /></span>
						<span class="text-xs text-amber-700/70 dark:text-amber-400/70">Pkt.</span>
						<span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-amber-400 dark:bg-amber-600 text-amber-900 dark:text-amber-100 rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold">3</span>
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
				<Card class="flex items-center gap-4 hover:border-primary-300 dark:hover:border-primary-600 hover:scale-[1.01] transition-all duration-200">
					<div class="w-8 text-center">
						<span class="text-lg font-bold text-gray-400">{rank}</span>
					</div>
					<div class="flex-1">
						<span class="font-semibold">{user.display_name || user.username}</span>
						<div class="flex items-center gap-3 mt-0.5 text-xs text-gray-500 dark:text-gray-400">
							{#if user.current_streak > 0}
								<StreakBadge streak={user.current_streak} size="sm" />
							{/if}
						</div>
					</div>
					<div class="text-right">
						<span class="text-lg font-bold text-primary-600 dark:text-primary-400">
							<AnimatedCounter value={getPoints(user)} />
						</span>
						<span class="text-xs text-gray-500 ml-1">Pkt.</span>
					</div>
				</Card>
			</a>
		{/each}
	</div>
{/if}
