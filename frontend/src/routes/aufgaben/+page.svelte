<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import type { Task, Room } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import { showToast } from '$lib/stores/toast';
	import { mdiPlus, mdiPencil, mdiDelete, mdiStar, mdiClock } from '@mdi/js';

	let tasks = $state<Task[]>([]);
	let rooms = $state<Room[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let filterRoom = $state<number | null>(null);
	let filterActive = $state<boolean | null>(true);

	async function loadData() {
		loading = true;
		error = null;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			const [t, r] = await Promise.all([
				client.tasks.list({
					room_id: filterRoom ?? undefined,
					is_active: filterActive ?? undefined
				}),
				client.rooms.list()
			]);
			tasks = t;
			rooms = r;
		} catch (e) {
			error = e instanceof ApiError ? e.detail : 'Fehler beim Laden';
		} finally {
			loading = false;
		}
	}

	async function deleteTask(id: number) {
		if (!confirm('Aufgabe wirklich löschen?')) return;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			await client.tasks.delete(id);
			showToast('Aufgabe gelöscht', 'success');
			await loadData();
		} catch (e) {
			showToast('Fehler beim Löschen', 'error');
		}
	}

	function getRoomName(roomId: number): string {
		return rooms.find((r) => r.id === roomId)?.name ?? 'Unbekannt';
	}

	const recurrenceLabels: Record<string, string> = {
		once: 'Einmalig',
		daily: 'Täglich',
		weekly: 'Wöchentlich',
		monthly: 'Monatlich'
	};

	let mounted = $state(false);

	onMount(() => {
		loadData().then(() => { mounted = true; });
	});

	$effect(() => {
		// Reloade bei Filter-Änderung
		void filterRoom;
		void filterActive;
		if (mounted) loadData();
	});
</script>

<svelte:head>
	<title>Aufgaben - ChoreQuest</title>
</svelte:head>

<div class="flex items-center justify-between mb-6">
	<h1 class="text-2xl font-bold">Aufgaben</h1>
	<a href="/aufgaben/neu">
		<Button>
			<Icon path={mdiPlus} size={18} />
			Neue Aufgabe
		</Button>
	</a>
</div>

<!-- Filter -->
<Card class="mb-4">
	<div class="flex flex-wrap gap-4">
		<div>
			<label for="filter-room" class="block text-xs font-medium mb-1">Raum</label>
			<select
				id="filter-room"
				bind:value={filterRoom}
				class="text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1.5"
			>
				<option value={null}>Alle Räume</option>
				{#each rooms as room (room.id)}
					<option value={room.id}>{room.name}</option>
				{/each}
			</select>
		</div>
		<div>
			<label for="filter-active" class="block text-xs font-medium mb-1">Status</label>
			<select
				id="filter-active"
				bind:value={filterActive}
				class="text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1.5"
			>
				<option value={null}>Alle</option>
				<option value={true}>Aktiv</option>
				<option value={false}>Inaktiv</option>
			</select>
		</div>
	</div>
</Card>

{#if loading}
	<Loading />
{:else if error}
	<ErrorMessage message={error} onretry={loadData} />
{:else if tasks.length === 0}
	<Card class="text-center py-8">
		<p class="text-gray-500 dark:text-gray-400">Keine Aufgaben gefunden.</p>
	</Card>
{:else}
	<div class="space-y-2">
		{#each tasks as task (task.id)}
			<Card class="flex items-center gap-3">
				<div class="flex-1 min-w-0">
					<div class="flex items-center gap-2">
						<span class="font-medium text-sm">{task.title}</span>
						{#if !task.is_active}
							<Badge variant="default">Inaktiv</Badge>
						{/if}
					</div>
					<div class="flex items-center gap-3 mt-1 text-xs text-gray-500 dark:text-gray-400">
						<span>{getRoomName(task.room_id)}</span>
						<span class="flex items-center gap-1">
							<Icon path={mdiStar} size={12} />
							{task.base_points}
						</span>
						<span class="flex items-center gap-1">
							<Icon path={mdiClock} size={12} />
							{task.estimated_minutes} Min.
						</span>
						<Badge>{recurrenceLabels[task.recurrence] ?? task.recurrence}</Badge>
					</div>
				</div>
				<div class="flex items-center gap-1">
					<a
						href="/aufgaben/{task.id}"
						class="p-2 rounded-lg text-gray-400 hover:text-primary-600 hover:bg-gray-100 dark:hover:bg-gray-700"
					>
						<Icon path={mdiPencil} size={18} />
					</a>
					<button
						onclick={() => deleteTask(task.id)}
						class="p-2 rounded-lg text-gray-400 hover:text-danger-500 hover:bg-gray-100 dark:hover:bg-gray-700"
					>
						<Icon path={mdiDelete} size={18} />
					</button>
				</div>
			</Card>
		{/each}
	</div>
{/if}
