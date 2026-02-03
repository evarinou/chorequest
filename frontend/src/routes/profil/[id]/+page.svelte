<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import type { UserStats, AchievementProgress } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import AchievementCard from '$lib/components/gamification/AchievementCard.svelte';
	import AnimatedCounter from '$lib/components/gamification/AnimatedCounter.svelte';
	import StreakBadge from '$lib/components/gamification/StreakBadge.svelte';
	import ProgressBar from '$lib/components/gamification/ProgressBar.svelte';
	import { generatePixelAvatar } from '$lib/utils/pixelAvatar';
	import { getLevelInfo } from '$lib/utils/level';

	let { data } = $props();

	let stats = $state<UserStats | null>(null);
	let achievements = $state<AchievementProgress[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let levelInfo = $derived(stats ? getLevelInfo(stats.user.total_points) : null);
	let avatarSvg = $derived(stats ? generatePixelAvatar(stats.user.id, 64) : '');

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
{:else if stats && levelInfo}
	<!-- Character Header -->
	<div class="flex flex-col items-center sm:flex-row sm:items-center gap-4 mb-6">
		<div class="w-16 h-16 border-3 border-nes-gold shrink-0">
			{@html avatarSvg}
		</div>
		<div class="flex-1">
			<h1 class="text-sm mb-1">{(stats.user.display_name || stats.user.username).toUpperCase()}</h1>
			<div class="text-[8px] text-nes-gold mb-2" style="font-family: 'Press Start 2P', monospace;">
				LV.{levelInfo.level} {levelInfo.title}
			</div>
			<ProgressBar value={levelInfo.progress} />
			<span class="text-xs text-parchment-400 dark:text-crt-green/60">
				{levelInfo.currentXP} / {levelInfo.requiredXP} XP zum nächsten Level
			</span>
		</div>
	</div>

	<!-- Stat Boxes -->
	<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mb-8">
		<Card class="pixel-border-gold">
			<div class="flex flex-col items-center text-center">
				<span class="text-[7px] text-nes-gold mb-1" style="font-family: 'Press Start 2P', monospace;">GESAMT-XP</span>
				<span class="text-2xl font-bold text-nes-gold"><AnimatedCounter value={stats.user.total_points} /></span>
			</div>
		</Card>
		<Card>
			<div class="flex flex-col items-center text-center">
				<span class="text-[7px] text-nes-orange mb-1" style="font-family: 'Press Start 2P', monospace;">STREAK</span>
				{#if stats.user.current_streak > 0}
					<StreakBadge streak={stats.user.current_streak} size="lg" />
				{:else}
					<span class="text-2xl text-parchment-400 dark:text-crt-green/40">0</span>
				{/if}
				<span class="text-xs text-parchment-400 dark:text-crt-green/50 mt-1">Tage</span>
			</div>
		</Card>
		<Card>
			<div class="flex flex-col items-center text-center">
				<span class="text-[7px] text-nes-green dark:text-crt-green mb-1" style="font-family: 'Press Start 2P', monospace;">ERLEDIGT</span>
				<span class="text-2xl font-bold text-nes-green dark:text-crt-green"><AnimatedCounter value={stats.tasks_completed_total} /></span>
			</div>
		</Card>
		<Card>
			<div class="flex flex-col items-center text-center">
				<span class="text-[7px] text-nes-purple mb-1" style="font-family: 'Press Start 2P', monospace;">TROPHÄEN</span>
				<span class="text-2xl font-bold text-nes-purple"><AnimatedCounter value={stats.achievements_count} /></span>
			</div>
		</Card>
	</div>

	<!-- Weekly Stats -->
	<Card class="mb-6">
		<div class="text-sm text-parchment-400 dark:text-crt-green/70">
			Diese Woche: <strong class="text-nes-gold">{stats.user.weekly_points} XP</strong>
			&middot; {stats.tasks_completed_this_week} Quests
			{#if stats.favorite_room}
				&middot; Lieblingszone: {stats.favorite_room}
			{/if}
		</div>
	</Card>

	<!-- Achievements -->
	<h2 class="text-[10px] mb-4" style="font-family: 'Press Start 2P', monospace;">TROPHÄEN-VITRINE</h2>
	{#if achievements.length === 0}
		<Card class="text-center py-6">
			<p class="text-parchment-400 dark:text-crt-green/60">Keine Achievements verfügbar.</p>
		</Card>
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			{#each achievements as progress (progress.achievement.id)}
				<AchievementCard {progress} />
			{/each}
		</div>
	{/if}
{/if}
