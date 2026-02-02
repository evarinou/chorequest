<script lang="ts">
	import { onMount } from 'svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import type { WeeklySummary } from '$lib/api/types';
	import { mdiRefresh, mdiClockOutline, mdiDoor, mdiChevronDown, mdiChevronUp } from '@mdi/js';

	let latest: WeeklySummary | null = $state(null);
	let older: WeeklySummary[] = $state([]);
	let loading = $state(true);
	let generating = $state(false);
	let error = $state('');
	let expandedId: number | null = $state(null);

	function getWeekNumber(dateStr: string): number {
		const d = new Date(dateStr + 'T00:00:00');
		const dayNum = d.getUTCDay() || 7;
		d.setUTCDate(d.getUTCDate() + 4 - dayNum);
		const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
		return Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr + 'T00:00:00').toLocaleDateString('de-DE', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric'
		});
	}

	async function loadSummaries() {
		loading = true;
		error = '';
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			const all = await client.summaries.list(20);
			if (all.length > 0) {
				latest = all[0];
				older = all.slice(1);
			} else {
				latest = null;
				older = [];
			}
		} catch (e: any) {
			if (e?.status === 404) {
				latest = null;
				older = [];
			} else {
				error = e?.detail || 'Fehler beim Laden';
			}
		} finally {
			loading = false;
		}
	}

	async function generate() {
		generating = true;
		error = '';
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			const result = await client.summaries.generate();
			latest = result.summary;
			const all = await client.summaries.list(20);
			if (all.length > 0) {
				latest = all[0];
				older = all.slice(1);
			}
		} catch (e: any) {
			error = e?.detail || 'Fehler beim Generieren';
		} finally {
			generating = false;
		}
	}

	function toggleExpanded(id: number) {
		expandedId = expandedId === id ? null : id;
	}

	onMount(loadSummaries);
</script>

<svelte:head>
	<title>KI-Bericht - ChoreQuest</title>
</svelte:head>

<div class="max-w-3xl mx-auto space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<h1 class="text-sm">DAS ORAKEL SPRICHT</h1>
		<Button onclick={generate} disabled={generating}>
			<Icon path={mdiRefresh} size={16} class={generating ? 'animate-spin' : ''} />
			{generating ? 'GENERIERT...' : 'NEU GENERIEREN'}
		</Button>
	</div>

	{#if error}
		<Card class="border-nes-red! text-nes-red">
			{error}
		</Card>
	{/if}

	{#if loading}
		<Loading text="DAS ORAKEL DENKT NACH" />
	{:else if !latest}
		<Card class="text-center py-8">
			<div class="text-4xl mb-3">🔮</div>
			<p class="text-[10px] mb-2" style="font-family: 'Press Start 2P', monospace;">NOCH KEINE PROPHEZEIUNG</p>
			<p class="text-parchment-400 dark:text-crt-green/60">
				Klicke auf "NEU GENERIEREN" oder warte bis Sonntag 19:00.
			</p>
		</Card>
	{:else}
		<!-- Neueste Summary -->
		<Card>
			<div class="border-b-2 border-[#5a3a1a] dark:border-crt-border pb-2 mb-3">
				<span class="text-[9px] text-nes-gold" style="font-family: 'Press Start 2P', monospace;">
					KW {getWeekNumber(latest.week_start)}: {formatDate(latest.week_start)} - {formatDate(latest.week_end)}
				</span>
			</div>
			{#if latest.summary_text}
				{#each latest.summary_text.split('\n\n') as paragraph}
					<p class="text-sm mb-3 last:mb-0 leading-relaxed">{paragraph}</p>
				{/each}
			{/if}
		</Card>

		<!-- Vorgeschlagene Aufgaben -->
		{#if latest.suggested_tasks && latest.suggested_tasks.length > 0}
			<div>
				<h2 class="text-[10px] mb-3" style="font-family: 'Press Start 2P', monospace;">VORGESCHLAGENE QUESTS</h2>
				<div class="grid gap-3">
					{#each latest.suggested_tasks as task}
						<Card>
							<div class="flex items-start justify-between gap-3">
								<div class="flex-1">
									<h3 class="text-sm font-bold">{task.title}</h3>
									<p class="text-sm text-parchment-400 dark:text-crt-green/70 mt-1">{task.description}</p>
									<p class="text-xs text-parchment-400 dark:text-crt-green/50 mt-2 italic">{task.reason}</p>
								</div>
								<div class="flex flex-col items-end gap-1 shrink-0">
									<span class="flex items-center gap-1 text-[7px] text-nes-blue dark:text-crt-green" style="font-family: 'Press Start 2P', monospace;">
										<Icon path={mdiDoor} size={12} />
										{task.room_name}
									</span>
									<span class="flex items-center gap-1 text-xs text-parchment-400 dark:text-crt-green/50">
										<Icon path={mdiClockOutline} size={12} />
										{task.estimated_minutes} Min.
									</span>
								</div>
							</div>
						</Card>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Ältere Zusammenfassungen -->
		{#if older.length > 0}
			<div>
				<h2 class="text-[10px] mb-3" style="font-family: 'Press Start 2P', monospace;">ARCHIV</h2>
				<div class="space-y-2">
					{#each older as summary (summary.id)}
						<Card>
							<button
								onclick={() => toggleExpanded(summary.id)}
								class="w-full flex items-center justify-between text-left"
							>
								<span class="text-[8px] text-parchment-400 dark:text-crt-green" style="font-family: 'Press Start 2P', monospace;">
									KW {getWeekNumber(summary.week_start)}: {formatDate(summary.week_start)} - {formatDate(summary.week_end)}
								</span>
								<Icon path={expandedId === summary.id ? mdiChevronUp : mdiChevronDown} size={18} class="text-parchment-400 dark:text-crt-green/50" />
							</button>
							{#if expandedId === summary.id}
								<div class="mt-3 pt-3 border-t-2 border-[#5a3a1a] dark:border-crt-border">
									{#if summary.summary_text}
										{#each summary.summary_text.split('\n\n') as paragraph}
											<p class="text-sm text-parchment-400 dark:text-crt-green/70 mb-2 last:mb-0">{paragraph}</p>
										{/each}
									{/if}
									{#if summary.suggested_tasks && summary.suggested_tasks.length > 0}
										<div class="mt-3 pt-2 border-t border-parchment-300 dark:border-crt-border">
											<p class="text-[7px] text-parchment-400 dark:text-crt-green/50 mb-1" style="font-family: 'Press Start 2P', monospace;">QUESTS:</p>
											{#each summary.suggested_tasks as task}
												<p class="text-sm text-parchment-400 dark:text-crt-green/60">- {task.title} ({task.room_name})</p>
											{/each}
										</div>
									{/if}
								</div>
							{/if}
						</Card>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>
