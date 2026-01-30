<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiClient, ApiError } from '$lib/api/client';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { showToast } from '$lib/stores/toast';
	import type { Room, RoomUpdate } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Loading from '$lib/components/shared/Loading.svelte';
	import ErrorMessage from '$lib/components/shared/ErrorMessage.svelte';
	import { mdiPencil, mdiInformation } from '@mdi/js';

	let rooms = $state<Room[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Edit Modal
	let editRoom = $state<Room | null>(null);
	let editMultiplier = $state(1.0);
	let editIcon = $state('');
	let editSortOrder = $state(0);
	let editModalOpen = $state(false);
	let saving = $state(false);

	async function loadData() {
		loading = true;
		error = null;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			rooms = await client.rooms.list();
		} catch (e) {
			error = e instanceof ApiError ? e.detail : 'Fehler beim Laden';
		} finally {
			loading = false;
		}
	}

	function openEdit(room: Room) {
		editRoom = room;
		editMultiplier = room.point_multiplier;
		editIcon = room.icon;
		editSortOrder = room.sort_order;
		editModalOpen = true;
	}

	async function saveEdit() {
		if (!editRoom) return;
		saving = true;
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			await client.rooms.update(editRoom.id, {
				icon: editIcon,
				point_multiplier: editMultiplier,
				sort_order: editSortOrder
			} as RoomUpdate);
			editModalOpen = false;
			showToast('Raum aktualisiert', 'success');
			await loadData();
		} catch (e) {
			showToast(e instanceof ApiError ? e.detail : 'Fehler beim Speichern', 'error');
		} finally {
			saving = false;
		}
	}

	onMount(loadData);
</script>

<svelte:head>
	<title>Räume - ChoreQuest</title>
</svelte:head>

<h1 class="text-2xl font-bold mb-4">Räume</h1>

<div class="flex items-center gap-2 mb-6 text-sm text-gray-500 dark:text-gray-400">
	<Icon path={mdiInformation} size={16} />
	<span>Räume werden aus Home Assistant synchronisiert.</span>
</div>

{#if loading}
	<Loading />
{:else if error}
	<ErrorMessage message={error} onretry={loadData} />
{:else if rooms.length === 0}
	<Card class="text-center py-8">
		<p class="text-gray-500 dark:text-gray-400">Keine Räume vorhanden. Synchronisiere mit Home Assistant.</p>
	</Card>
{:else}
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
		{#each rooms.toSorted((a, b) => a.sort_order - b.sort_order) as room (room.id)}
			<Card class="flex items-start justify-between">
				<div>
					<h3 class="font-semibold">{room.name}</h3>
					<div class="flex items-center gap-2 mt-2">
						{#if room.point_multiplier !== 1.0}
							<Badge variant="warning">{room.point_multiplier}x Punkte</Badge>
						{:else}
							<Badge>1.0x Punkte</Badge>
						{/if}
						{#if room.ha_area_id}
							<Badge variant="success">HA</Badge>
						{/if}
					</div>
					<p class="text-xs text-gray-400 mt-2">Icon: {room.icon}</p>
				</div>
				<button
					onclick={() => openEdit(room)}
					class="p-2 rounded-lg text-gray-400 hover:text-primary-600 hover:bg-gray-100 dark:hover:bg-gray-700"
				>
					<Icon path={mdiPencil} size={18} />
				</button>
			</Card>
		{/each}
	</div>
{/if}

<Modal open={editModalOpen} title="Raum bearbeiten" onclose={() => { editModalOpen = false; }}>
	{#if editRoom}
		<div class="space-y-4">
			<div>
				<label for="edit-icon" class="block text-sm font-medium mb-1">Icon (MDI)</label>
				<input
					id="edit-icon"
					type="text"
					bind:value={editIcon}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm"
					placeholder="mdi:room"
				/>
			</div>
			<div>
				<label for="edit-multiplier" class="block text-sm font-medium mb-1">
					Punkte-Multiplikator: {editMultiplier.toFixed(1)}x
				</label>
				<input
					id="edit-multiplier"
					type="range"
					min={0.5}
					max={3.0}
					step={0.1}
					bind:value={editMultiplier}
					class="w-full"
				/>
				<div class="flex justify-between text-xs text-gray-400">
					<span>0.5x</span>
					<span>3.0x</span>
				</div>
			</div>
			<div>
				<label for="edit-sort" class="block text-sm font-medium mb-1">Sortierung</label>
				<input
					id="edit-sort"
					type="number"
					min={0}
					bind:value={editSortOrder}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm"
				/>
			</div>
			<div class="flex gap-3 justify-end">
				<Button variant="secondary" onclick={() => { editModalOpen = false; }}>Abbrechen</Button>
				<Button onclick={saveEdit} disabled={saving}>
					{saving ? 'Speichert...' : 'Speichern'}
				</Button>
			</div>
		</div>
	{/if}
</Modal>
