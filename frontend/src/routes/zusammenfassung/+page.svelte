<script lang="ts">
	import { onMount } from 'svelte';
	import { mdiRobotHappy, mdiRefresh, mdiClockOutline, mdiDoor, mdiChevronDown, mdiChevronUp } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';
	import { apiClient } from '$lib/stores/api';
	import type { WeeklySummary } from '$lib/api/types';

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
			const all = await apiClient.summaries.list(20);
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
				error = e?.detail || 'Fehler beim Laden der Zusammenfassungen';
			}
		} finally {
			loading = false;
		}
	}

	async function generate() {
		generating = true;
		error = '';
		try {
			const result = await apiClient.summaries.generate();
			latest = result.summary;
			// Liste neu laden für korrekte Sortierung
			const all = await apiClient.summaries.list(20);
			if (all.length > 0) {
				latest = all[0];
				older = all.slice(1);
			}
		} catch (e: any) {
			error = e?.detail || 'Fehler beim Generieren der Zusammenfassung';
		} finally {
			generating = false;
		}
	}

	function toggleExpanded(id: number) {
		expandedId = expandedId === id ? null : id;
	}

	onMount(loadSummaries);
</script>

<div class="max-w-3xl mx-auto space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-3">
			<Icon path={mdiRobotHappy} size={28} class="text-primary-600 dark:text-primary-400" />
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">Wochen-Zusammenfassung</h1>
		</div>
		<button
			onclick={generate}
			disabled={generating}
			class="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
		>
			<Icon path={mdiRefresh} size={18} class={generating ? 'animate-spin' : ''} />
			{generating ? 'Wird generiert...' : 'Neu generieren'}
		</button>
	</div>

	{#if error}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-700 dark:text-red-400">
			{error}
		</div>
	{/if}

	{#if loading}
		<div class="flex justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
		</div>
	{:else if !latest}
		<!-- Leerzustand -->
		<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
			<Icon path={mdiRobotHappy} size={48} class="text-gray-300 dark:text-gray-600 mx-auto mb-4" />
			<p class="text-gray-500 dark:text-gray-400 text-lg">Noch keine Zusammenfassung vorhanden</p>
			<p class="text-gray-400 dark:text-gray-500 text-sm mt-2">
				Klicke auf "Neu generieren" oder warte bis Sonntag um 19:00 Uhr.
			</p>
		</div>
	{:else}
		<!-- Neueste Summary -->
		<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
			<div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
				<p class="text-sm font-semibold text-primary-600 dark:text-primary-400">
					KW {getWeekNumber(latest.week_start)}: {formatDate(latest.week_start)} – {formatDate(latest.week_end)}
				</p>
			</div>
			<div class="px-6 py-5">
				{#if latest.summary_text}
					{#each latest.summary_text.split('\n\n') as paragraph}
						<p class="text-gray-700 dark:text-gray-300 mb-3 last:mb-0 leading-relaxed">{paragraph}</p>
					{/each}
				{/if}
			</div>
		</div>

		<!-- Vorgeschlagene Aufgaben -->
		{#if latest.suggested_tasks && latest.suggested_tasks.length > 0}
			<div>
				<h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Vorgeschlagene Aufgaben</h2>
				<div class="grid gap-3">
					{#each latest.suggested_tasks as task}
						<div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
							<div class="flex items-start justify-between gap-3">
								<div class="flex-1">
									<h3 class="font-medium text-gray-900 dark:text-white">{task.title}</h3>
									<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{task.description}</p>
									<p class="text-xs text-gray-500 dark:text-gray-500 mt-2 italic">{task.reason}</p>
								</div>
								<div class="flex flex-col items-end gap-1 shrink-0">
									<span class="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded text-xs font-medium">
										<Icon path={mdiDoor} size={12} />
										{task.room_name}
									</span>
									<span class="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
										<Icon path={mdiClockOutline} size={12} />
										{task.estimated_minutes} Min.
									</span>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Ältere Zusammenfassungen -->
		{#if older.length > 0}
			<div>
				<h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Frühere Zusammenfassungen</h2>
				<div class="space-y-2">
					{#each older as summary (summary.id)}
						<div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
							<button
								onclick={() => toggleExpanded(summary.id)}
								class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
							>
								<span class="text-sm font-medium text-gray-700 dark:text-gray-300">
									KW {getWeekNumber(summary.week_start)}: {formatDate(summary.week_start)} – {formatDate(summary.week_end)}
								</span>
								<Icon path={expandedId === summary.id ? mdiChevronUp : mdiChevronDown} size={20} class="text-gray-400" />
							</button>
							{#if expandedId === summary.id}
								<div class="px-4 pb-4 border-t border-gray-100 dark:border-gray-700 pt-3">
									{#if summary.summary_text}
										{#each summary.summary_text.split('\n\n') as paragraph}
											<p class="text-sm text-gray-600 dark:text-gray-400 mb-2 last:mb-0">{paragraph}</p>
										{/each}
									{/if}
									{#if summary.suggested_tasks && summary.suggested_tasks.length > 0}
										<div class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
											<p class="text-xs font-medium text-gray-500 dark:text-gray-500 mb-2">Vorgeschlagene Aufgaben:</p>
											{#each summary.suggested_tasks as task}
												<p class="text-sm text-gray-600 dark:text-gray-400">• {task.title} ({task.room_name})</p>
											{/each}
										</div>
									{/if}
								</div>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>
