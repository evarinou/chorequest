<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import type { User } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import { mdiTrophyVariant, mdiFire } from '@mdi/js';

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

	const rankColors = ['text-yellow-500', 'text-gray-400', 'text-amber-600'];
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
	<div class="space-y-2">
		{#each users as user, i (user.id)}
			<a href="/profil/{user.id}" class="block">
				<Card class="flex items-center gap-4 hover:border-primary-300 dark:hover:border-primary-600 transition-colors">
					<div class="w-8 text-center">
						{#if i < 3}
							<Icon path={mdiTrophyVariant} size={24} class={rankColors[i]} />
						{:else}
							<span class="text-lg font-bold text-gray-400">{i + 1}</span>
						{/if}
					</div>
					<div class="flex-1">
						<span class="font-semibold">{user.display_name || user.username}</span>
						<div class="flex items-center gap-3 mt-0.5 text-xs text-gray-500 dark:text-gray-400">
							{#if user.current_streak > 0}
								<span class="flex items-center gap-1">
									<Icon path={mdiFire} size={12} class="text-orange-500" />
									{user.current_streak} Tage Streak
								</span>
							{/if}
						</div>
					</div>
					<div class="text-right">
						<span class="text-lg font-bold text-primary-600 dark:text-primary-400">
							{mode === 'weekly' ? user.weekly_points : user.total_points}
						</span>
						<span class="text-xs text-gray-500 ml-1">Pkt.</span>
					</div>
				</Card>
			</a>
		{/each}
	</div>
{/if}
