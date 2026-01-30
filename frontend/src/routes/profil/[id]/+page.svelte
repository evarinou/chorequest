<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import type { UserStats, AchievementProgress } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import AchievementCard from '$lib/components/gamification/AchievementCard.svelte';
	import AnimatedCounter from '$lib/components/gamification/AnimatedCounter.svelte';
	import StreakBadge from '$lib/components/gamification/StreakBadge.svelte';
	import { mdiStar, mdiFire, mdiTrophy, mdiCheckAll } from '@mdi/js';

	let { data } = $props();

	let stats = $state<UserStats | null>(null);
	let achievements = $state<AchievementProgress[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadData() {
		loading = true;
		error = null;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			const [s, a] = await Promise.all([
				client.users.stats(data.userId),
				client.gamification.userProgress(data.userId)
			]);
			stats = s;
			achievements = a;
		} catch (e) {
			error = e instanceof ApiError ? e.detail : 'Fehler beim Laden';
		} finally {
			loading = false;
		}
	}

	onMount(loadData);
</script>

<svelte:head>
	<title>{stats?.user.display_name ?? 'Profil'} - ChoreQuest</title>
</svelte:head>

{#if loading}
	<Loading />
{:else if error}
	<ErrorMessage message={error} onretry={loadData} />
{:else if stats}
	<h1 class="text-2xl font-bold mb-6">{stats.user.display_name || stats.user.username}</h1>

	<!-- Stat-Cards -->
	<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
		<Card class="gradient-card-gold border-0 relative overflow-hidden">
			<div class="absolute inset-0 animate-shimmer pointer-events-none"></div>
			<div class="flex flex-col items-center text-center relative">
				<Icon path={mdiStar} size={24} class="text-yellow-600 dark:text-yellow-300 mb-1" />
				<span class="text-xl font-bold"><AnimatedCounter value={stats.user.total_points} /></span>
				<span class="text-xs text-yellow-700/70 dark:text-yellow-300/70">Gesamtpunkte</span>
			</div>
		</Card>
		<Card class="gradient-card-purple border-0">
			<div class="flex flex-col items-center text-center">
				{#if stats.user.current_streak > 0}
					<StreakBadge streak={stats.user.current_streak} size="md" />
				{:else}
					<Icon path={mdiFire} size={24} class="text-gray-400 mb-1" />
				{/if}
				<span class="text-xl font-bold"><AnimatedCounter value={stats.user.current_streak} /></span>
				<span class="text-xs text-purple-700/70 dark:text-purple-300/70">Tage Streak</span>
			</div>
		</Card>
		<Card class="gradient-card-green border-0">
			<div class="flex flex-col items-center text-center">
				<Icon path={mdiCheckAll} size={24} class="text-green-600 dark:text-green-300 mb-1" />
				<span class="text-xl font-bold"><AnimatedCounter value={stats.tasks_completed_total} /></span>
				<span class="text-xs text-green-700/70 dark:text-green-300/70">Erledigt</span>
			</div>
		</Card>
		<Card class="gradient-card-blue border-0">
			<div class="flex flex-col items-center text-center">
				<Icon path={mdiTrophy} size={24} class="text-primary-600 dark:text-primary-300 mb-1" />
				<span class="text-xl font-bold"><AnimatedCounter value={stats.achievements_count} /></span>
				<span class="text-xs text-primary-700/70 dark:text-primary-300/70">Achievements</span>
			</div>
		</Card>
	</div>

	<div class="mb-3 text-sm text-gray-500 dark:text-gray-400">
		Diese Woche: <strong class="text-primary-600 dark:text-primary-400">{stats.user.weekly_points} Punkte</strong>
		&middot; {stats.tasks_completed_this_week} Aufgaben
		{#if stats.favorite_room}
			&middot; Lieblingsraum: {stats.favorite_room}
		{/if}
	</div>

	<!-- Achievements -->
	<h2 class="text-lg font-semibold mb-4">Achievements</h2>
	{#if achievements.length === 0}
		<Card class="text-center py-6">
			<p class="text-gray-500 dark:text-gray-400">Keine Achievements verfügbar.</p>
		</Card>
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			{#each achievements as progress (progress.achievement.id)}
				<AchievementCard {progress} />
			{/each}
		</div>
	{/if}
{/if}
