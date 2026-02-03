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
	import { mdiPlus, mdiPencil, mdiDelete } from '@mdi/js';

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
		if (!confirm('Quest wirklich löschen?')) return;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			await client.tasks.delete(id);
			showToast('Quest gelöscht', 'success');
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
		void filterRoom;
		void filterActive;
		if (mounted) loadData();
	});
</script>

<svelte:head>
	<title>Aufgaben - ChoreQuest</title>
</svelte:head>

<div class="flex items-center justify-between mb-6">
	<h1 class="text-sm">QUEST-VERWALTUNG</h1>
	<a href="/aufgaben/neu">
		<Button>
			<Icon path={mdiPlus} size={16} />
			NEUE QUEST
		</Button>
	</a>
</div>

<!-- Filter -->
<Card class="mb-4">
	<div class="flex flex-wrap gap-4">
		<div>
			<label for="filter-room" class="block text-[8px] mb-1" style="font-family: 'Press Start 2P', monospace;">ZONE</label>
			<select
				id="filter-room"
				bind:value={filterRoom}
				class="pixel-input w-full sm:w-auto"
			>
				<option value={null}>Alle Zonen</option>
				{#each rooms as room (room.id)}
					<option value={room.id}>{room.name}</option>
				{/each}
			</select>
		</div>
		<div>
			<label for="filter-active" class="block text-[8px] mb-1" style="font-family: 'Press Start 2P', monospace;">STATUS</label>
			<select
				id="filter-active"
				bind:value={filterActive}
				class="pixel-input w-full sm:w-auto"
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
		<p class="text-parchment-400 dark:text-crt-green/60">Keine Quests gefunden.</p>
	</Card>
{:else}
	<div class="space-y-2">
		{#each tasks as task (task.id)}
			<Card class="flex items-center gap-3">
				<div class="shrink-0 text-nes-gold text-sm">
					{task.base_points >= 20 ? '★★★' : task.base_points >= 10 ? '★★' : '★'}
				</div>
				<div class="flex-1 min-w-0">
					<div class="flex items-center gap-2">
						<span class="text-sm">{task.title}</span>
						{#if !task.is_active}
							<Badge variant="default">INAKTIV</Badge>
						{/if}
					</div>
					<div class="flex items-center gap-3 mt-1 text-xs text-parchment-400 dark:text-crt-green/60">
						<span>{getRoomName(task.room_id)}</span>
						<Badge variant="points">{task.base_points} XP</Badge>
						<span>{task.estimated_minutes} Min.</span>
						<Badge>{recurrenceLabels[task.recurrence] ?? task.recurrence}</Badge>
					</div>
				</div>
				<div class="flex items-center gap-1">
					<a
						href="/aufgaben/{task.id}"
						class="p-2 min-w-[44px] min-h-[44px] flex items-center justify-center text-parchment-400 hover:text-nes-gold dark:text-crt-green/60 dark:hover:text-crt-green"
					>
						<Icon path={mdiPencil} size={18} />
					</a>
					<button
						onclick={() => deleteTask(task.id)}
						class="p-2 min-w-[44px] min-h-[44px] flex items-center justify-center text-parchment-400 hover:text-nes-red dark:text-crt-green/60 dark:hover:text-nes-red"
					>
						<Icon path={mdiDelete} size={18} />
					</button>
				</div>
			</Card>
		{/each}
	</div>
{/if}
